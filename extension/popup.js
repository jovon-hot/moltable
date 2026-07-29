// ============================================================
// Moltable Chrome Extension — Popup Script
// ============================================================

const STORAGE_KEYS = {
  API_KEY: 'moltable_api_key',
  SERVER_URL: 'moltable_server_url',
};

const DEFAULT_SERVER_URL = 'http://localhost:8642';

// --- DOM refs ---
const statusDot = document.getElementById('statusDot');
const statusText = document.getElementById('statusText');
const apiKeyInput = document.getElementById('apiKeyInput');
const saveKeyBtn = document.getElementById('saveKeyBtn');
const clearKeyBtn = document.getElementById('clearKeyBtn');
const keyStatus = document.getElementById('keyStatus');
const serverUrlInput = document.getElementById('serverUrlInput');
const saveServerBtn = document.getElementById('saveServerBtn');
const resetServerBtn = document.getElementById('resetServerBtn');
const serverStatus = document.getElementById('serverStatus');
const currentServerUrl = document.getElementById('currentServerUrl');
const openSearchBtn = document.getElementById('openSearchBtn');
const testApiBtn = document.getElementById('testApiBtn');

// --- Load saved values ---
async function loadSettings() {
  const result = await chrome.storage.local.get([STORAGE_KEYS.API_KEY, STORAGE_KEYS.SERVER_URL]);
  const apiKey = result[STORAGE_KEYS.API_KEY] || '';
  const serverUrl = result[STORAGE_KEYS.SERVER_URL] || DEFAULT_SERVER_URL;

  if (apiKey) {
    apiKeyInput.value = apiKey;
    clearKeyBtn.classList.remove('hidden');
  }
  serverUrlInput.value = serverUrl;
  currentServerUrl.textContent = `Current: ${serverUrl}`;
}

// --- Show status message ---
function showStatus(el, message, type) {
  el.textContent = message;
  el.className = 'status ' + type;
  setTimeout(() => {
    if (el.textContent === message) {
      el.className = 'status';
    }
  }, 4000);
}

// --- Update connection status ---
async function updateConnectionStatus() {
  const result = await chrome.storage.local.get([STORAGE_KEYS.API_KEY, STORAGE_KEYS.SERVER_URL]);
  const apiKey = result[STORAGE_KEYS.API_KEY] || '';
  const serverUrl = result[STORAGE_KEYS.SERVER_URL] || DEFAULT_SERVER_URL;

  if (!apiKey) {
    statusDot.className = 'dot disconnected';
    statusText.textContent = 'No API Key configured';
    return;
  }

  try {
    const resp = await fetch(`${serverUrl}/api/health`, {
      headers: { 'X-API-Key': apiKey },
      signal: AbortSignal.timeout(5000),
    });
    if (resp.ok) {
      statusDot.className = 'dot connected';
      statusText.textContent = 'Connected to Moltable server';
    } else {
      statusDot.className = 'dot disconnected';
      statusText.textContent = `Server error (${resp.status})`;
    }
  } catch (e) {
    statusDot.className = 'dot unknown';
    statusText.textContent = 'Server unreachable';
  }
}

// --- Save API Key ---
saveKeyBtn.addEventListener('click', async () => {
  const key = apiKeyInput.value.trim();
  if (!key) {
    showStatus(keyStatus, 'Please enter an API Key', 'error');
    return;
  }
  await chrome.storage.local.set({ [STORAGE_KEYS.API_KEY]: key });
  clearKeyBtn.classList.remove('hidden');
  showStatus(keyStatus, 'API Key saved successfully', 'success');
  await updateConnectionStatus();
});

// --- Clear API Key ---
clearKeyBtn.addEventListener('click', async () => {
  await chrome.storage.local.remove(STORAGE_KEYS.API_KEY);
  apiKeyInput.value = '';
  clearKeyBtn.classList.add('hidden');
  showStatus(keyStatus, 'API Key cleared', 'info');
  await updateConnectionStatus();
});

// --- Save Server URL ---
saveServerBtn.addEventListener('click', async () => {
  const url = serverUrlInput.value.trim() || DEFAULT_SERVER_URL;
  await chrome.storage.local.set({ [STORAGE_KEYS.SERVER_URL]: url });
  currentServerUrl.textContent = `Current: ${url}`;
  showStatus(serverStatus, 'Server URL saved', 'success');
  await updateConnectionStatus();
});

// --- Reset Server URL ---
resetServerBtn.addEventListener('click', async () => {
  serverUrlInput.value = DEFAULT_SERVER_URL;
  await chrome.storage.local.set({ [STORAGE_KEYS.SERVER_URL]: DEFAULT_SERVER_URL });
  currentServerUrl.textContent = `Current: ${DEFAULT_SERVER_URL}`;
  showStatus(serverStatus, 'Reset to default', 'info');
  await updateConnectionStatus();
});

// --- Open Search on current tab ---
openSearchBtn.addEventListener('click', async () => {
  const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
  if (tab && tab.id) {
    try {
      await chrome.tabs.sendMessage(tab.id, { action: 'moltable_toggle' });
      window.close();
    } catch {
      showStatus(keyStatus, 'Cannot reach this page — not a supported AI site?', 'error');
    }
  }
});

// --- Test API Connection ---
testApiBtn.addEventListener('click', async () => {
  testApiBtn.textContent = '⏳ Testing...';
  testApiBtn.disabled = true;
  await updateConnectionStatus();
  testApiBtn.textContent = '🧪 Test Connection';
  testApiBtn.disabled = false;
});

// --- Listen for settings changes from other contexts ---
chrome.storage.onChanged.addListener((changes) => {
  if (STORAGE_KEYS.API_KEY in changes || STORAGE_KEYS.SERVER_URL in changes) {
    loadSettings();
    updateConnectionStatus();
  }
});

// --- Init ---
document.addEventListener('DOMContentLoaded', async () => {
  await loadSettings();
  await updateConnectionStatus();
});
