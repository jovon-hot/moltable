// ============================================================
// Moltable Chrome Extension — Background Service Worker
// ============================================================

// --- Installation handler ---
chrome.runtime.onInstalled.addListener((details) => {
  if (details.reason === 'install') {
    // Set default server URL on first install
    chrome.storage.local.set({
      moltable_server_url: 'http://localhost:8642',
    });

    console.log('[Moltable] Extension installed. Default server URL set to http://localhost:8642');
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
