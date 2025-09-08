(async function main(){
  const BUST = Date.now();
  
  // Security: HTML escaping
  function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
  }
  
  // Performance: Debounced functions
  function debounce(func, wait) {
    let timeout;
    return function(...args) {
      clearTimeout(timeout);
      timeout = setTimeout(() => func.apply(this, args), wait);
    };
  }
  
  // Loading state
  function showLoading() {
    const cardsEl = document.getElementById('cards');
    if (cardsEl) cardsEl.innerHTML = '<div class="loading">Loading problems...</div>';
  }
  
  function showError(message) {
    const cardsEl = document.getElementById('cards');
    if (cardsEl) cardsEl.innerHTML = `<div class="error">${escapeHtml(message)}</div>`;
  }
  
  showLoading();
  
  let data;
  try {
    const response = await fetch(`./data/index.json?ts=${BUST}`, {cache:"no-store"});
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    data = await response.json();
  } catch (error) {
    showError('Failed to load data. Please refresh the page.');
    console.error('Data loading failed:', error);
    return;
  }

  // Owner/repo detection
  function detectOwnerRepo(){
    if (location.hostname.endsWith("github.io")) {
      const owner = location.hostname.split(".")[0];
      const repo = location.pathname.split("/").filter(Boolean)[0] || "leetcode-grind";
      return { owner, repo };
    }
    return { owner: "mh-13", repo: "leetcode-grind" };
  }
  const OR = detectOwnerRepo();
  const BRANCHES = ["main", "master", "gh-pages"];

  async function fetchRawWithFallback(path){
    let lastErr = null;
    for (const branch of BRANCHES){
      const url = `https://raw.githubusercontent.com/${OR.owner}/${OR.repo}/${branch}/${path}?ts=${Date.now()}`;
      try {
        const res = await fetch(url, {cache:"no-store"});
        if (res.ok) return { txt: await res.text(), url, branch };
        lastErr = { status: res.status, url };
      } catch (e) { lastErr = { error: e, url }; }
    }
    throw lastErr || new Error("Raw fetch failed");
  }
  
  function ghBlobUrl(path, branch="main"){ return `https://github.com/${OR.owner}/${OR.repo}/blob/${branch}/${path}`; }
  function ghRawUrl(path, branch="main"){  return `https://raw.githubusercontent.com/${OR.owner}/${OR.repo}/${branch}/${path}`; }

  // Elements with null checks
  const elements = {
    cards: document.getElementById("cards"),
    trackSel: document.getElementById("track"),
    typeSel: document.getElementById("type"),
    tagsEl: document.getElementById("tags"),
    tagSearch: document.getElementById("tagSearch"),
    statsEl: document.getElementById("stats"),
    resetBtn: document.getElementById("reset"),
    refreshBtn: document.getElementById("refreshData"),
    catSel: document.getElementById("category"),
    qInput: document.getElementById("q"),
    modal: document.getElementById("modal"),
    codePre: document.getElementById("codePre"),
    codeEl: document.getElementById("codeEl"),
    modalTitle: document.getElementById("modalTitle"),
    modalMeta: document.getElementById("modalMeta"),
    closeBtn: document.getElementById("closeBtn"),
    copyBtn: document.getElementById("copyBtn"),
    ghBtn: document.getElementById("ghBtn"),
    rawBtn: document.getElementById("rawBtn")
  };

  // State
  const state = { track:"", type:"", category:"", tags:new Set(), q:"", list:[], selectedIndex:-1 };

  // Populate filters safely
  if (elements.trackSel && data.tracks) {
    elements.trackSel.innerHTML = `<option value="">All Tracks</option>` + 
      data.tracks.map(t => `<option value="${escapeHtml(t)}">${escapeHtml(t)}</option>`).join("");
  }
  
  if (elements.catSel && data.categories) {
    elements.catSel.innerHTML = `<option value="">All Categories</option>` + 
      data.categories.map(c => `<option value="${escapeHtml(c)}">${escapeHtml(c)}</option>`).join("");
  }

  // Event listeners with null checks
  if (elements.trackSel) elements.trackSel.onchange = () => { state.track = elements.trackSel.value; render(); };
  if (elements.typeSel) elements.typeSel.onchange = () => { state.type = elements.typeSel.value; render(); };
  if (elements.catSel) elements.catSel.onchange = () => { state.category = elements.catSel.value; render(); };

  // Tags with performance optimization
  let filteredTagList = data.tags ? data.tags.slice() : [];
  
  function renderTags(){
    if (!elements.tagsEl) return;
    
    // Use DocumentFragment for better performance
    const fragment = document.createDocumentFragment();
    
    filteredTagList.forEach(tag => {
      const el = document.createElement("span");
      el.className = "tag" + (state.tags.has(tag) ? " active" : "");
      el.textContent = tag; // Safe from XSS
      el.onclick = () => {
        state.tags.has(tag) ? state.tags.delete(tag) : state.tags.add(tag);
        renderTags();
        render();
      };
      fragment.appendChild(el);
    });
    
    elements.tagsEl.innerHTML = "";
    elements.tagsEl.appendChild(fragment);
  }
  
  // Debounced tag search
  const debouncedTagSearch = debounce(() => {
    if (!elements.tagSearch || !data.tags) return;
    const q = elements.tagSearch.value.toLowerCase().trim();
    filteredTagList = data.tags.filter(t => t.toLowerCase().includes(q));
    renderTags();
  }, 200);
  
  if (elements.tagSearch) elements.tagSearch.oninput = debouncedTagSearch;
  renderTags();

  // Debounced text search
  const debouncedSearch = debounce(() => {
    if (!elements.qInput) return;
    state.q = elements.qInput.value.toLowerCase();
    render();
  }, 300);
  
  if (elements.qInput) elements.qInput.oninput = debouncedSearch;

  // Reset functionality
  if (elements.resetBtn) {
    elements.resetBtn.onclick = () => {
      state.track = state.type = state.category = "";
      if (elements.trackSel) elements.trackSel.value = "";
      if (elements.typeSel) elements.typeSel.value = "";
      if (elements.catSel) elements.catSel.value = "";
      state.tags.clear();
      if (elements.tagSearch) elements.tagSearch.value = "";
      state.q = "";
      if (elements.qInput) elements.qInput.value = "";
      filteredTagList = data.tags ? data.tags.slice() : [];
      renderTags();
      render();
    };
  }
  
  if (elements.refreshBtn) {
    elements.refreshBtn.onclick = () => location.reload();
  }

  // Filtering with early returns for performance
  function matchQuery(x){
    if (!state.q) return true;
    const searchText = `${x.id} ${x.title || ''} ${x.slug || ''} ${(x.tags || []).join(" ")}`.toLowerCase();
    return searchText.includes(state.q);
  }
  
  function filterItems(){
    if (!data.items) return [];
    const tags = [...state.tags];
    return data.items.filter(x => {
      if (state.track && x.track !== state.track) return false;
      if (state.type && x.type !== state.type) return false;
      if (state.category && x.category !== state.category) return false;
      if (tags.length && !tags.every(t => (x.tags || []).includes(t))) return false;
      return matchQuery(x);
    });
  }
  
  // Safe card HTML generation
  function createCard(x, i) {
    const card = document.createElement('div');
    card.className = 'card';
    card.setAttribute('data-idx', i);
    
    const title = document.createElement('h3');
    title.textContent = `${String(x.id || 0).padStart(4,"0")} — ${x.title || 'Untitled'}`;
    
    const meta = document.createElement('div');
    meta.className = 'meta';
    const metaText = [x.track, (x.type || '').toUpperCase(), x.difficulty || '', x.category || '']
      .filter(Boolean).join(' · ');
    meta.textContent = metaText;
    
    const chips = document.createElement('div');
    chips.className = 'chips';
    (x.tags || []).slice(0, 6).forEach(tag => {
      const chip = document.createElement('span');
      chip.className = 'chip';
      chip.textContent = tag;
      chips.appendChild(chip);
    });
    
    card.appendChild(title);
    card.appendChild(meta);
    card.appendChild(chips);
    
    return card;
  }
  
  // Performance optimized render
  function render(){
    if (!elements.cards) return;
    
    state.list = filterItems();
    
    if (elements.statsEl) {
      elements.statsEl.textContent = `${state.list.length} / ${data.items ? data.items.length : 0} shown`;
    }
    
    // Use DocumentFragment for batch DOM updates
    const fragment = document.createDocumentFragment();
    state.list.forEach((item, i) => {
      fragment.appendChild(createCard(item, i));
    });
    
    elements.cards.innerHTML = '';
    elements.cards.appendChild(fragment);
  }
  
  render();

  // Modal functionality
  if (elements.cards) {
    elements.cards.addEventListener("click", e => {
      const card = e.target.closest(".card");
      if (!card) return;
      const idx = parseInt(card.getAttribute("data-idx"));
      if (!isNaN(idx)) openItem(idx);
    });
  }

  function langClass(item){ 
    return item.type === "py" ? "language-python" : 
           item.type === "sql" ? "language-sql" : "language-none"; 
  }

  async function openItem(idx){
    if (idx < 0 || idx >= state.list.length || !elements.modal) return;
    const item = state.list[idx];
    state.selectedIndex = idx;

    if (elements.modalTitle) {
      elements.modalTitle.textContent = `#${String(item.id || 0).padStart(4,"0")} — ${item.title || 'Untitled'}`;
    }
    
    if (elements.modalMeta) {
      const metaText = [item.track, (item.type || '').toUpperCase(), item.difficulty || '', item.category || '', item.link || '']
        .filter(Boolean).join(' · ');
      elements.modalMeta.textContent = metaText;
    }
    
    if (elements.codeEl) {
      elements.codeEl.className = langClass(item);
      elements.codeEl.textContent = "Loading…";
    }
    
    showModal(true);

    try {
      const { txt, url, branch } = await fetchRawWithFallback(item.path);
      if (elements.codeEl) elements.codeEl.textContent = txt;
      if (elements.ghBtn) elements.ghBtn.href = ghBlobUrl(item.path, branch);
      if (elements.rawBtn) elements.rawBtn.href = url;
      if (window.Prism && elements.codeEl) Prism.highlightElement(elements.codeEl);
      location.hash = `item=${encodeURIComponent(item.track || '')}:${item.type || ''}:${item.id || 0}`;
    } catch (err) {
      const tried = BRANCHES.map(b => ghRawUrl(item.path, b)).join("\n");
      if (elements.codeEl) {
        elements.codeEl.className = "language-none";
        elements.codeEl.textContent = `404: Not Found\n\nTried:\n${tried}\n\nCheck:\n• File path & name (4-digit id + slug)\n• Branch exists (main/master/gh-pages)\n• Pushed to GitHub`;
      }
      if (elements.ghBtn) elements.ghBtn.href = ghBlobUrl(item.path, "main");
      if (elements.rawBtn) elements.rawBtn.href = ghRawUrl(item.path, "main");
      console.warn(err);
    }
  }

  function showModal(show) {
    if (!elements.modal) return;
    elements.modal.classList.toggle("hidden", !show);
    elements.modal.setAttribute("aria-hidden", String(!show));
    if (show && elements.codePre) elements.codePre.scrollTop = 0;
  }
  
  // Modal controls
  if (elements.closeBtn) {
    elements.closeBtn.onclick = () => { showModal(false); location.hash = ""; };
  }
  
  if (elements.copyBtn) {
    elements.copyBtn.onclick = async () => {
      try {
        await navigator.clipboard.writeText(elements.codeEl?.textContent || "");
        elements.copyBtn.textContent = "Copied ✓";
      } catch {
        elements.copyBtn.textContent = "Copy Failed";
      }
      setTimeout(() => elements.copyBtn.textContent = "Copy", 1200);
    };
  }
  
  // Keyboard navigation
  window.addEventListener("keydown", (e) => {
    if (!elements.modal || elements.modal.classList.contains("hidden")) return;
    if (e.key === "Escape") { showModal(false); location.hash = ""; }
    if (e.key === "ArrowRight") openItem(Math.min(state.selectedIndex + 1, state.list.length - 1));
    if (e.key === "ArrowLeft") openItem(Math.max(state.selectedIndex - 1, 0));
  });
  
  if (elements.modal) {
    elements.modal.addEventListener("click", (e) => {
      if (e.target === elements.modal) { showModal(false); location.hash = ""; }
    });
  }

  // Deep linking
  function tryOpenFromHash(){
    const h = new URLSearchParams(location.hash.replace(/^#/, ""));
    const val = h.get("item");
    if (!val) return;
    
    const [track, type, idStr] = val.split(":");
    const id = Number(idStr);
    
    if (elements.trackSel) { elements.trackSel.value = track || ""; state.track = elements.trackSel.value; }
    if (elements.typeSel) { elements.typeSel.value = type || ""; state.type = elements.typeSel.value; }
    
    render();
    const idx = state.list.findIndex(x => x.track === track && x.type === type && x.id === id);
    if (idx >= 0) openItem(idx);
  }
  
  window.addEventListener("hashchange", tryOpenFromHash);
  tryOpenFromHash();
})();
