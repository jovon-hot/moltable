// ============================================================
// Moltable Chrome Extension — Background Service Worker
// ============================================================

const CAPTURE_QUEUE_KEY = 'moltable_capture_queue';
const FLUSH_FALLBACK_MS = 60000;
const DEFAULT_SERVER_URL = 'http://localhost:8642';
let flushTimer = null;

// --- Installation handler ---
chrome.runtime.onInstalled.addListener((details) => {
  if (details.reason === 'install') {
    // Set default server URL on first install
    chrome.storage.local.set({
      moltable_server_url: DEFAULT_SERVER_URL,
    });

    console.log(`[Moltable] Extension installed. Default server URL set to ${DEFAULT_SERVER_URL}`);
  }
});

// --- Listen for messages from content scripts ---
chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  // Handle proxy API requests from content script if needed
  if (message.type === 'PROXY_SEARCH') {
    handleProxySearch(message.query, message.apiKey, message.serverUrl)
      .then(sendResponse)
      .catch((err) => sendResponse({ error: err.message }));
    return true; // Keep channel open for async response
  }
  if (message.type === 'MOLTABLE_CAPTURED') {
    scheduleFlush(3000);
    sendResponse({ ok: true });
  }
});

// --- Proxy search (direct fetch from service worker) ---
async function handleProxySearch(query, apiKey, serverUrl) {
  const url = `${serverUrl}/api/memories/search?q=${encodeURIComponent(query)}&top_k=5`;

  const resp = await fetch(url, {
    headers: { 'X-API-Key': apiKey },
    signal: AbortSignal.timeout(10000),
  });

  if (!resp.ok) {
    throw new Error(`API error: ${resp.status} ${resp.statusText}`);
  }

  const data = await resp.json();
  return data.results || [];
}

// --- Auto-capture: batch-send queued memories when browser is idle ---
function scheduleFlush(delayMs) {
  clearTimeout(flushTimer);
  flushTimer = setTimeout(flushCaptureQueue, delayMs);
}

async function flushCaptureQueue() {
  const stored = await chrome.storage.local.get([CAPTURE_QUEUE_KEY, 'moltable_api_key', 'moltable_server_url']);
  const queue = stored[CAPTURE_QUEUE_KEY] || [];
  if (queue.length === 0 || !stored.moltable_api_key) return;

  const url = `${stored.moltable_server_url || DEFAULT_SERVER_URL}/api/sync/push`;
  try {
    const resp = await fetch(url, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', 'X-API-Key': stored.moltable_api_key },
      body: JSON.stringify({ memories: queue }),
      signal: AbortSignal.timeout(15000),
    });
    if (!resp.ok) throw new Error(`HTTP ${resp.status}`);
    const data = await resp.json();
    if (data.conflicts && data.conflicts.length > 0) {
      console.warn('[Moltable] Sync conflicts (dropped, need manual resolution):', data.conflicts.map((c) => c.id));
    }
    await chrome.storage.local.set({ [CAPTURE_QUEUE_KEY]: [] });
  } catch (err) {
    console.warn('[Moltable] Sync flush failed (will retry):', err.message);
  }
}

// Flush when the browser goes idle
chrome.idle.onStateChanged.addListener((state) => {
  if (state === 'idle') scheduleFlush(2000);
});

// Fallback: periodically flush in case idle events are missed
setInterval(() => {
  chrome.storage.local.get(CAPTURE_QUEUE_KEY, (stored) => {
    if ((stored[CAPTURE_QUEUE_KEY] || []).length > 0) flushCaptureQueue();
  });
}, FLUSH_FALLBACK_MS);
