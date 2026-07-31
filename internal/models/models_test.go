package models

import (
	"encoding/json"
	"testing"
)

func TestProtocolStatusConstants(t *testing.T) {
	if ProtocolStatusOpen != "open" {
		t.Errorf("ProtocolStatusOpen = %s, want 'open'", ProtocolStatusOpen)
	}
	if ProtocolStatusAccepted != "accepted" {
		t.Errorf("ProtocolStatusAccepted = %s, want 'accepted'", ProtocolStatusAccepted)
	}
	if ProtocolStatusCompleted != "completed" {
		t.Errorf("ProtocolStatusCompleted = %s, want 'completed'", ProtocolStatusCompleted)
	}
	if ProtocolStatusDisputed != "disputed" {
		t.Errorf("ProtocolStatusDisputed = %s, want 'disputed'", ProtocolStatusDisputed)
	}
}

func TestProtocolTypeConstants(t *testing.T) {
	if ProtocolTypeTrade != "TRADE" {
		t.Errorf("ProtocolTypeTrade = %s, want 'TRADE'", ProtocolTypeTrade)
	}
	if ProtocolTypeBet != "BET" {
		t.Errorf("ProtocolTypeBet = %s, want 'BET'", ProtocolTypeBet)
	}
}

func TestRulingConstants(t *testing.T) {
	if RulingProposerWins != "proposer_wins" {
		t.Errorf("RulingProposerWins = %s, want 'proposer_wins'", RulingProposerWins)
	}
	if RulingOpponentWins != "opponent_wins" {
		t.Errorf("RulingOpponentWins = %s, want 'opponent_wins'", RulingOpponentWins)
	}
	if RulingDraw != "draw" {
		t.Errorf("RulingDraw = %s, want 'draw'", RulingDraw)
	}
	if RulingSplit != "split" {
		t.Errorf("RulingSplit = %s, want 'split'", RulingSplit)
	}
}

func TestJSONBScan(t *testing.T) {
	tests := []struct {
		name    string
		input   interface{}
		want    JSONB
		wantErr bool
	}{
		{
			name:    "valid json",
			input:   []byte(`{"key": "value"}`),
			want:    JSONB{"key": "value"},
			wantErr: false,
		},
		{
			name:    "nil input",
			input:   nil,
			want:    nil,
			wantErr: false,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			var j JSONB
			err := j.Scan(tt.input)
			if (err != nil) != tt.wantErr {
				t.Errorf("JSONB.Scan() error = %v, wantErr %v", err, tt.wantErr)
			}
		})
	}
}

func TestProtocolJSON(t *testing.T) {
	p := Protocol{
		ProtocolID:    "PROTO-test123",
		ProtocolType:  ProtocolTypeTrade,
		InitiatorAIID: "agent1",
		Title:         "Test Protocol",
		Content:       "Test content",
		Stake:         100,
		Status:        ProtocolStatusOpen,
	}

	data, err := json.Marshal(p)
	if err != nil {
		t.Fatalf("Failed to marshal Protocol: %v", err)
	}

	var p2 Protocol
	if err := json.Unmarshal(data, &p2); err != nil {
		t.Fatalf("Failed to unmarshal Protocol: %v", err)
	}

	if p.ProtocolID != p2.ProtocolID {
		t.Errorf("ProtocolID mismatch: %s != %s", p.ProtocolID, p2.ProtocolID)
	}
	if p.ProtocolType != p2.ProtocolType {
		t.Errorf("ProtocolType mismatch: %s != %s", p.ProtocolType, p2.ProtocolType)
	}
}
