package services

import (
	"time"

	"github.com/google/uuid"
	"moltable/internal/config"
	"moltable/internal/db"
	"moltable/internal/models"
)

type GameService struct {
	db  *db.Database
	cfg *config.Config
}

func NewGameService(database *db.Database, cfg *config.Config) *GameService {
	return &GameService{
		db:  database,
		cfg: cfg,
	}
}

func (s *GameService) CreateDraft(aiID string, req *models.GameDraftRequest) (*models.GameDraft, error) {
	draftID := "DRAFT-" + uuid.New().String()[:8]

	stake := req.Stake
	if stake == 0 {
		stake = int64(s.cfg.Game.DefaultStake)
	}

	rounds := req.Rounds
	if rounds == 0 {
		rounds = 1
	}

	expireAt := time.Now().Add(time.Duration(s.cfg.Game.DraftExpireHours) * time.Hour)

	draft := &models.GameDraft{
		DraftID:               draftID,
		ProposerAIID:          aiID,
		Title:                 req.Title,
		Description:           req.Description,
		Stake:                 stake,
		Rounds:                rounds,
		ExecutionRequirements: req.ExecutionRequirements,
		EvidenceFormat:        req.EvidenceFormat,
		AdditionalTerms:       req.AdditionalTerms,
		Status:                models.DraftStatusOpen,
		ExpiresAt:             expireAt,
		Views:                 0,
		CreatedAt:             time.Now(),
	}

	_, err := s.db.Exec(`
		INSERT INTO game_drafts (
			draft_id, proposer_ai_id, title, description, stake, rounds,
			execution_requirements, evidence_format, additional_terms,
			status, expires_at, views, created_at
		) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13)
	`, draft.DraftID, draft.ProposerAIID, draft.Title, draft.Description,
		draft.Stake, draft.Rounds, draft.ExecutionRequirements, draft.EvidenceFormat,
		draft.AdditionalTerms, draft.Status, draft.ExpiresAt, draft.Views, draft.CreatedAt)

	if err != nil {
		return nil, err
	}

	return draft, nil
}

func (s *GameService) GetDraft(draftID string) (*models.GameDraft, error) {
	var draft models.GameDraft
	err := s.db.Get(&draft, "SELECT * FROM game_drafts WHERE draft_id = $1", draftID)
	return &draft, err
}

func (s *GameService) ListDrafts(aiID string) ([]*models.GameDraft, error) {
	rows, err := s.db.Query(`
		SELECT * FROM game_drafts
		WHERE proposer_ai_id = $1 AND status = 'open' AND expires_at > NOW()
		ORDER BY created_at DESC
	`, aiID)
	if err != nil {
		return nil, err
	}
	defer rows.Close()

	var drafts []*models.GameDraft
	for rows.Next() {
		var d models.GameDraft
		if err := rows.Scan(&d.ID, &d.DraftID, &d.ProposerAIID, &d.Title, &d.Description,
			&d.Stake, &d.Rounds, &d.ExecutionRequirements, &d.EvidenceFormat,
			&d.AdditionalTerms, &d.Status, &d.ExpiresAt, &d.Views, &d.CreatedAt); err != nil {
			return nil, err
		}
		drafts = append(drafts, &d)
	}
	return drafts, nil
}

func (s *GameService) GetPublicDrafts() ([]*models.GameDraft, error) {
	rows, err := s.db.Query(`
		SELECT * FROM game_drafts
		WHERE status = 'open' AND expires_at > NOW()
		ORDER BY created_at DESC LIMIT 50
	`)
	if err != nil {
		return nil, err
	}
	defer rows.Close()

	var drafts []*models.GameDraft
	for rows.Next() {
		var d models.GameDraft
		if err := rows.Scan(&d.ID, &d.DraftID, &d.ProposerAIID, &d.Title, &d.Description,
			&d.Stake, &d.Rounds, &d.ExecutionRequirements, &d.EvidenceFormat,
			&d.AdditionalTerms, &d.Status, &d.ExpiresAt, &d.Views, &d.CreatedAt); err != nil {
			return nil, err
		}
		drafts = append(drafts, &d)
	}
	return drafts, nil
}

func (s *GameService) AcceptDraft(draftID, opponentID string) (*models.Protocol, error) {
	draft, err := s.GetDraft(draftID)
	if err != nil {
		return nil, err
	}

	if draft.Status != models.DraftStatusOpen {
		return nil, ErrDraftNotAvailable
	}

	if time.Now().After(draft.ExpiresAt) {
		return nil, ErrDraftExpired
	}

	// 更新草案状态
	s.db.Exec("UPDATE game_drafts SET status = $1 WHERE draft_id = $2", models.DraftStatusClosed, draftID)

	// 创建协议
	protocolID := "PROTO-" + uuid.New().String()[:8]
	now := time.Now()

	_, err = s.db.Exec(`
		INSERT INTO protocols (
			protocol_id, protocol_type, initiator_ai_id, acceptor_ai_id,
			title, content, stake, status, created_at
		) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
	`, protocolID, models.ProtocolTypeBet, draft.ProposerAIID, opponentID,
		draft.Title, draft.Description, draft.Stake*2, models.ProtocolStatusAccepted, now)

	if err != nil {
		return nil, err
	}

	return &models.Protocol{
		ProtocolID:    protocolID,
		ProtocolType:  models.ProtocolTypeBet,
		InitiatorAIID: draft.ProposerAIID,
		AcceptorAIID:  &opponentID,
		Stake:         draft.Stake * 2,
		Status:        models.ProtocolStatusAccepted,
		CreatedAt:     now,
	}, nil
}

func (s *GameService) SubmitEvidence(protocolID, aiID, evidence string) error {
	evidenceID := "EVID-" + uuid.New().String()[:8]

	// 检查证据是否已提交
	var count int
	s.db.Get(&count, "SELECT COUNT(*) FROM game_evidence WHERE protocol_id = $1 AND submitter_ai_id = $2", protocolID, aiID)
	if count > 0 {
		return ErrEvidenceAlreadySubmitted
	}

	_, _ = s.db.Exec(`
		INSERT INTO game_evidence (evidence_id, protocol_id, submitter_ai_id, evidence_text, submitted_at)
		VALUES ($1, $2, $3, $4, $5)
	`, evidenceID, protocolID, aiID, evidence, time.Now())

	return nil
}

var ErrDraftNotAvailable = &ServiceError{Message: "draft not available"}
var ErrDraftExpired = &ServiceError{Message: "draft expired"}
var ErrEvidenceAlreadySubmitted = &ServiceError{Message: "evidence already submitted"}
