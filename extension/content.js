// ============================================================
// Moltable Chrome Extension — Content Script
// Injects a floating memory toolbar into supported AI chat pages.
// ============================================================

(function () {
  'use strict';

  // --- Configuration ---
  const CONFIG = {
    STORAGE_API_KEY: 'moltable_api_key',
    STORAGE_SERVER_URL: 'moltable_server_url',
    DEFAULT_SERVER_URL: 'http://localhost:8642',
    MAX_RESULTS: 5,
    TOOLBAR_ID: 'moltable-toolbar-root',
    SEARCH_DEBOUNCE_MS: 350,
    CAPTURE_QUEUE_KEY: 'moltable_capture_queue',
    CAPTURE_DEBOUNCE_MS: 2000,
    CAPTURE_MIN_LENGTH: 40,
    CAPTURE_MAX_QUEUE: 200,
    CAPTURE_SELECTORS: {
      'chatgpt.com': '[data-message-author-role="assistant"]',
      'claude.ai': '[data-testid="assistant-message"], .font-claude-message',
      'gemini.google.com': '.model-response-text',
      'chat.deepseek.com': '.ds-markdown',
    },
  };

  // --- DOM ---
  let rootEl = null;
  let isOpen = false;
  let searchTimeout = null;

  // --- Helpers ---
  function createElement(tag, attrs = {}, children = []) {
    const el = document.createElement(tag);
    for (const [k, v] of Object.entries(attrs)) {
      if (k === 'className') el.className = v;
      else if (k === 'style' && typeof v === 'object') Object.assign(el.style, v);
      else if (k.startsWith('data')) el.setAttribute(k, v);
      else if (k === 'html') el.innerHTML = v;
      else el.setAttribute(k, v);
    }
    for (const child of children) {
      if (typeof child === 'string') el.appendChild(document.createTextNode(child));
      else if (child instanceof Node) el.appendChild(child);
    }
    return el;
  }

  async function getFromStorage(key) {
    const result = await chrome.storage.local.get(key);
    return result[key];
  }

  async function getServerUrl() {
    return (await getFromStorage(CONFIG.STORAGE_SERVER_URL)) || CONFIG.DEFAULT_SERVER_URL;
  }

  async function getApiKey() {
    return (await getFromStorage(CONFIG.STORAGE_API_KEY)) || '';
  }

  // --- API call ---
  async function searchMemories(query) {
    const apiKey = await getApiKey();
    if (!apiKey) {
      throw new Error('NO_API_KEY');
    }
    const serverUrl = await getServerUrl();
    const url = `${serverUrl}/api/memories/search?q=${encodeURIComponent(query)}&top_k=${CONFIG.MAX_RESULTS}`;
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

  // --- Inject memory into AI input ---
  function injectIntoInput(text) {
    const selectors = {
      'chatgpt': '#prompt-textarea, [contenteditable="true"][role="textbox"], .ProseMirror',
      'claude': '[contenteditable="true"][role="textbox"], .ProseMirror',
      'gemini': '.input-area textarea, .ql-editor, [contenteditable="true"]',
      'deepseek': '#chat-input, textarea[placeholder*="message"], ._7619e9cc textarea',
    };

    const allSelectors = Object.values(selectors).flatMap(s => s.split(', '));
    let inputEl = null;

    for (const sel of allSelectors) {
      inputEl = document.querySelector(sel);
      if (inputEl) break;
    }

    if (!inputEl) {
      // Fallback: focus any textarea or contenteditable in the main area
      inputEl = document.querySelector('textarea, [contenteditable="true"]');
    }

    if (!inputEl) {
      alert('Moltable: Could not find the AI input field on this page.');
      return false;
    }

    // Focus and insert
    inputEl.focus();

    if (inputEl.isContentEditable || inputEl.tagName === 'DIV' || inputEl.getAttribute('contenteditable') === 'true') {
      // ContentEditable / ProseMirror
      const selection = window.getSelection();
      const range = document.createRange();
      range.selectNodeContents(inputEl);
      range.collapse(false);
      selection.removeAllRanges();
      selection.addRange(range);

      // Insert text
      document.execCommand('insertText', false, '\n' + text + '\n');
    } else {
      // Standard textarea / input
      const start = inputEl.selectionStart;
      const end = inputEl.selectionEnd;
      const prefix = inputEl.value.substring(0, start);
      const suffix = inputEl.value.substring(end);
      inputEl.value = prefix + '\n' + text + '\n' + suffix;
      inputEl.selectionStart = inputEl.selectionEnd = prefix.length + text.length + 2;

      // Trigger input event
      inputEl.dispatchEvent(new Event('input', { bubbles: true }));
      inputEl.dispatchEvent(new Event('change', { bubbles: true }));
    }

    // Trigger any React/Vue listeners
    inputEl.dispatchEvent(new KeyboardEvent('keydown', { key: 'Enter', bubbles: true }));

    return true;
  }

  // --- Build toolbar UI ---
  function buildToolbar() {
    // Main floating button (fab)
    const fab = createElement('button', {
      className: 'moltable-fab',
      html: '🧠',
      title: 'Moltable Memory',
    });

    // Panel container
    const panel = createElement('div', { className: 'moltable-panel moltable-hidden' });

    // Header
    const header = createElement('div', { className: 'moltable-header' }, [
      createElement('span', { className: 'moltable-logo' }, ['M']),
      createElement('span', { className: 'moltable-title' }, ['Moltable Memory']),
      createElement('button', {
        className: 'moltable-close-btn',
        html: '&times;',
        title: 'Close',
      }),
    ]);

    // Search input
    const searchWrapper = createElement('div', { className: 'moltable-search-wrapper' });
    const searchIcon = createElement('span', { className: 'moltable-search-icon' }, ['🔍']);
    const searchInput = createElement('input', {
      className: 'moltable-search-input',
      type: 'text',
      placeholder: 'Search your memories...',
    });
    const searchClear = createElement('button', {
      className: 'moltable-clear-btn moltable-hidden',
      html: '&times;',
    });
    searchWrapper.appendChild(searchIcon);
    searchWrapper.appendChild(searchInput);
    searchWrapper.appendChild(searchClear);

    // Results container
    const resultsContainer = createElement('div', { className: 'moltable-results' });

    // Loading indicator
    const loading = createElement('div', { className: 'moltable-loading moltable-hidden' }, ['Searching...']);

    // Error / empty state
    const emptyState = createElement('div', { className: 'moltable-empty moltable-hidden' }, [
      createElement('div', { className: 'moltable-empty-icon' }, ['📭']),
      createElement('div', { className: 'moltable-empty-text' }, ['No memories found']),
    ]);

    // Assemble panel
    panel.appendChild(header);
    panel.appendChild(searchWrapper);
    panel.appendChild(loading);
    panel.appendChild(resultsContainer);
    panel.appendChild(emptyState);

    // Root
    const root = createElement('div', { id: CONFIG.TOOLBAR_ID });
    root.appendChild(fab);
    root.appendChild(panel);

    // --- Event handlers ---

    // Toggle
    fab.addEventListener('click', () => {
      isOpen = !isOpen;
      panel.classList.toggle('moltable-hidden', !isOpen);
      fab.classList.toggle('moltable-active', isOpen);
      if (isOpen) {
        searchInput.focus();
        // Load initial memories if API key exists
        getApiKey().then(key => {
          if (key) {
            performSearch('');
          }
        });
      }
    });

    header.querySelector('.moltable-close-btn').addEventListener('click', () => {
      isOpen = false;
      panel.classList.add('moltable-hidden');
      fab.classList.remove('moltable-active');
    });

    // Search with debounce
    searchInput.addEventListener('input', () => {
      const val = searchInput.value.trim();
      searchClear.classList.toggle('moltable-hidden', !val);
      clearTimeout(searchTimeout);
      searchTimeout = setTimeout(() => performSearch(val), CONFIG.SEARCH_DEBOUNCE_MS);
    });

    // Clear search
    searchClear.addEventListener('click', () => {
      searchInput.value = '';
      searchClear.classList.add('moltable-hidden');
      performSearch('');
      searchInput.focus();
    });

    // Keyboard: Escape to close
    searchInput.addEventListener('keydown', (e) => {
      if (e.key === 'Escape') {
        isOpen = false;
        panel.classList.add('moltable-hidden');
        fab.classList.remove('moltable-active');
      }
    });

    return root;
  }

  // --- Perform search and render results ---
  async function performSearch(query) {
    const panel = rootEl?.querySelector('.moltable-panel');
    const resultsContainer = panel?.querySelector('.moltable-results');
    const loading = panel?.querySelector('.moltable-loading');
    const emptyState = panel?.querySelector('.moltable-empty');

    if (!resultsContainer || !loading || !emptyState) return;

    // Show loading
    loading.classList.remove('moltable-hidden');
    resultsContainer.innerHTML = '';
    emptyState.classList.add('moltable-hidden');

    try {
      const results = await searchMemories(query);

      loading.classList.add('moltable-hidden');

      if (!results || results.length === 0) {
        emptyState.classList.remove('moltable-hidden');
        return;
      }

      emptyState.classList.add('moltable-hidden');

      for (const mem of results) {
        const card = createMemoryCard(mem);
        resultsContainer.appendChild(card);
      }
    } catch (err) {
      loading.classList.add('moltable-hidden');

      if (err.message === 'NO_API_KEY') {
        emptyState.querySelector('.moltable-empty-icon').textContent = '🔑';
        emptyState.querySelector('.moltable-empty-text').textContent = 'Set your API Key in the extension popup';
        emptyState.classList.remove('moltable-hidden');
      } else if (err.name === 'AbortError' || err.message.includes('fetch') || err.message.includes('NetworkError')) {
        emptyState.querySelector('.moltable-empty-icon').textContent = '🔌';
        emptyState.querySelector('.moltable-empty-text').textContent = 'Cannot connect to Moltable server';
        emptyState.classList.remove('moltable-hidden');
      } else {
        emptyState.querySelector('.moltable-empty-icon').textContent = '⚠️';
        emptyState.querySelector('.moltable-empty-text').textContent = err.message || 'Search failed';
        emptyState.classList.remove('moltable-hidden');
      }
    }
  }

  // --- Create a single memory card ---
  function createMemoryCard(memory) {
    const content = memory.content || memory.text || '';
    const category = memory.category || memory.type || 'general';
    const similarity = memory.similarity || memory.score || null;
    const id = memory.id || '';

    // Truncate content
    const truncatedContent = content.length > 200 ? content.substring(0, 200) + '...' : content;

    const card = createElement('div', { className: 'moltable-card' });

    // Category badge
    const badge = createElement('span', { className: `moltable-badge moltable-badge-${category.toLowerCase().replace(/\s+/g, '-')}` }, [category]);

    // Content
    const contentEl = createElement('div', { className: 'moltable-card-content' }, [truncatedContent]);

    // Similarity score
    const meta = createElement('div', { className: 'moltable-card-meta' });
    if (similarity !== null) {
      const score = createElement('span', { className: 'moltable-score' }, [`${Math.round(similarity * 100)}% match`]);
      meta.appendChild(score);
    }

    // Inject button
    const injectBtn = createElement('button', {
      className: 'moltable-inject-btn',
      html: '📥 Inject',
      title: 'Inject into AI input',
    });
    injectBtn.addEventListener('click', () => {
      const success = injectIntoInput(content);
      if (success) {
        // Brief visual feedback
        injectBtn.innerHTML = '✅ Injected!';
        injectBtn.classList.add('moltable-injected');
        setTimeout(() => {
          injectBtn.innerHTML = '📥 Inject';
          injectBtn.classList.remove('moltable-injected');
        }, 2000);
      }
    });

    // Footer row
    const footer = createElement('div', { className: 'moltable-card-footer' });
    footer.appendChild(meta);
    footer.appendChild(injectBtn);

    card.appendChild(badge);
    card.appendChild(contentEl);
    card.appendChild(footer);

    return card;
  }

  // --- Inject toolbar into page ---
  function injectToolbar() {
    if (document.getElementById(CONFIG.TOOLBAR_ID)) return;
    rootEl = buildToolbar();
    document.body.appendChild(rootEl);
  }

  // --- Auto-capture: save new assistant messages as memories ---
  const capturePending = new Set();
  const captureLastLen = new WeakMap();
  const captureHashes = new Set();
  let captureTimer = null;

  function captureSelectorForHost() {
    const host = window.location.hostname;
    for (const [domain, selector] of Object.entries(CONFIG.CAPTURE_SELECTORS)) {
      if (host.endsWith(domain)) return selector;
    }
    return null;
  }

  function isAssistantNode(node) {
    if (node.nodeType !== Node.ELEMENT_NODE || !node.matches) return false;
    const selector = captureSelectorForHost();
    if (!selector) return false;
    return node.matches(selector) || !!node.closest(selector);
  }

  function captureHash(text) {
    let hash = 0;
    for (let i = 0; i < text.length; i++) hash = ((hash << 5) - hash + text.charCodeAt(i)) | 0;
    return hash;
  }

  async function queueCapturedMemory(text) {
    if (!(await getApiKey())) return;
    const stored = await chrome.storage.local.get(CONFIG.CAPTURE_QUEUE_KEY);
    const queue = stored[CONFIG.CAPTURE_QUEUE_KEY] || [];
    queue.push({
      id: `ext-${Date.now().toString(36)}-${Math.random().toString(36).slice(2, 8)}`,
      content: text,
      base_version: 0,
      updated_at: new Date().toISOString(),
    });
    await chrome.storage.local.set({ [CONFIG.CAPTURE_QUEUE_KEY]: queue.slice(-CONFIG.CAPTURE_MAX_QUEUE) });
    chrome.runtime.sendMessage({ type: 'MOLTABLE_CAPTURED' }).catch(() => {});
  }

  function scheduleCapture() {
    clearTimeout(captureTimer);
    captureTimer = setTimeout(flushCapture, CONFIG.CAPTURE_DEBOUNCE_MS);
  }

  async function flushCapture() {
    if (capturePending.size === 0 || !(await getApiKey())) return;
    const ready = [];
    let unstable = false;
    const keep = new Set();
    for (const node of capturePending) {
      const text = (node.textContent || '').trim();
      if (text.length < CONFIG.CAPTURE_MIN_LENGTH) continue;
      const prev = captureLastLen.get(node);
      if (prev === undefined || prev !== text.length) {
        captureLastLen.set(node, text.length);
        unstable = true;
        keep.add(node);
        continue;
      }
      const hash = captureHash(text);
      if (captureHashes.has(hash)) continue;
      captureHashes.add(hash);
      ready.push(text);
    }
    capturePending.clear();
    for (const node of keep) capturePending.add(node);
    if (unstable) scheduleCapture();
    for (const text of ready) await queueCapturedMemory(text);
    if (captureHashes.size > 1000) captureHashes.clear();
  }

  function startCaptureObserver() {
    if (!captureSelectorForHost()) return;
    new MutationObserver((mutations) => {
      let found = false;
      for (const mutation of mutations) {
        for (const node of mutation.addedNodes) {
          if (isAssistantNode(node)) {
            capturePending.add(node);
            found = true;
          }
        }
      }
      if (found) scheduleCapture();
    }).observe(document.body, { childList: true, subtree: true });
  }

  // --- Listen for messages from popup ---
  chrome.runtime.onMessage.addListener((msg, sender, sendResponse) => {
    if (msg.action === 'moltable_toggle') {
      const panel = rootEl?.querySelector('.moltable-panel');
      const fab = rootEl?.querySelector('.moltable-fab');
      if (panel && fab) {
        isOpen = !isOpen;
        panel.classList.toggle('moltable-hidden', !isOpen);
        fab.classList.toggle('moltable-active', isOpen);
        if (isOpen) {
          const searchInput = panel.querySelector('.moltable-search-input');
          if (searchInput) {
            searchInput.focus();
            performSearch(searchInput.value.trim());
          }
        }
      } else {
        injectToolbar();
        // Auto-open after injection
        setTimeout(() => {
          const p = rootEl?.querySelector('.moltable-panel');
          const f = rootEl?.querySelector('.moltable-fab');
          if (p && f) {
            isOpen = true;
            p.classList.remove('moltable-hidden');
            f.classList.add('moltable-active');
            const si = p.querySelector('.moltable-search-input');
            if (si) si.focus();
          }
        }, 100);
      }
    }
    return true;
  });

  // --- Initialize: inject toolbar + auto-capture ---
  function init() {
    startCaptureObserver();
    // Wait for DOM to be ready
    if (document.readyState === 'loading') {
      document.addEventListener('DOMContentLoaded', injectToolbar);
    } else {
      injectToolbar();
    }
  }

  init();
})();
