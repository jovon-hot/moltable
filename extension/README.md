# Moltable Memory — Chrome Extension

Inject Moltable memory toolbar into AI chat pages (ChatGPT, Claude, Gemini, DeepSeek).

## Features

- 🧠 **Floating Memory Toolbar** — Purple FAB button in bottom-right corner of supported AI sites
- 🔍 **Search Memories** — Search your Moltable memory store with debounced auto-search
- 📥 **One-Click Inject** — Inject memory content directly into the AI input field
- 🔑 **API Key Auth** — Secure API key stored in `chrome.storage.local`
- 🌙 **Dark Theme** — Matches Moltable brand identity
- ⚡ **No Build Required** — Pure JavaScript, zero dependencies

## Supported Sites

| Site | URL |
|------|-----|
| ChatGPT | https://chatgpt.com/* |
| Claude | https://claude.ai/* |
| Gemini | https://gemini.google.com/* |
| DeepSeek | https://chat.deepseek.com/* |

## Installation (Developer Mode)

1. Open Chrome and navigate to `chrome://extensions`
2. Enable **Developer mode** (toggle in top-right)
3. Click **Load unpacked**
4. Select the `extension/` directory
5. The Moltable icon should appear in your toolbar

## Usage

### 1. Configure API Key
- Click the Moltable icon in Chrome's extension bar
- Enter your Moltable API Key
- Click **Save**

### 2. Search & Inject
- Navigate to any supported AI chat page
- Click the 🧠 floating button (bottom-right)
- Type a search query to find memories
- Click **📥 Inject** on any memory to add it to the AI input field

### 3. Open from Popup
- Click the Moltable extension icon
- Click **🔍 Open Search** to toggle the toolbar on the current page

## API Configuration

Default API endpoint: `http://localhost:8642`

You can change the server URL in the extension popup. The backend API should expose:

```
GET /api/memories/search?q=<query>&top_k=5
Headers: X-API-Key: <your-api-key>
Response: { results: [{ id, content, category, similarity, ... }] }
```

## File Structure

```
extension/
├── manifest.json       # Chrome extension manifest (V3)
├── popup.html          # API key configuration popup
├── popup.js            # Popup logic
├── content.js          # Content script: toolbar injection & interaction
├── toolbar.css         # Toolbar styles (dark theme)
├── background.js       # Service worker
├── icons/
│   ├── icon16.svg      # Toolbar icon (16px)
│   ├── icon48.svg      # Extension icon (48px)
│   └── icon128.svg     # Extension icon (128px)
└── README.md           # This file
```
