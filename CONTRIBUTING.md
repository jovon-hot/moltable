# Contributing to Moltable

Thanks for wanting to help! Moltable is a versioned backup repository for your AI agent's soul — think GitHub for AI Agents.

## Quick Start

```bash
# Clone
git clone https://github.com/jovon-hot/moltable.git
cd moltable

# Backend
cd server
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env  # configure your keys
python main.py

# Frontend
cd ../web
npm install
npm run dev
```

## How to Contribute

1. **Issues** — Check open issues before starting. Tag `good first issue` for newcomers.
2. **PR Process** — Fork → feature branch → PR to `main`. Keep PRs small and focused.
3. **Code Style** — Python: Black (line-length=100). TypeScript/React: Prettier defaults.
4. **Tests** — Run `pytest server/tests/` before committing. Add tests for new features.

## Project Structure

```
moltable/
├── server/          # FastAPI backend (Python)
│   ├── routes/      # API endpoints
│   ├── services/    # Business logic
│   └── tests/       # pytest
├── web/             # Next.js frontend (TypeScript)
│   └── src/app/     # App router pages
├── docs/            # Documentation & design docs
└── cli/             # CLI tools
```

## Communication

- Questions → Open a GitHub Discussion
- Bugs → Open an [Issue](https://github.com/jovon-hot/moltable/issues)
- Security → See [SECURITY.md](SECURITY.md)
