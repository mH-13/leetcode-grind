(async function main(){
  const VERSION = "2.0.0"; // Update this when making changes
  const BUST = Date.now();

  // Version check and auto-reload if outdated
  function checkVersion() {
    const metaVersion = document.querySelector('meta[name="version"]');
    const htmlVersion = metaVersion ? metaVersion.getAttribute('content') : VERSION;

    // Store version in localStorage
    const storedVersion = localStorage.getItem('app_version');

    if (storedVersion && storedVersion !== htmlVersion) {
      console.log(`Version update detected: ${storedVersion} → ${htmlVersion}`);
      // Clear cache and reload
      if ('caches' in window) {
        caches.keys().then(names => {
          names.forEach(name => caches.delete(name));
        }).then(() => {
          localStorage.setItem('app_version', htmlVersion);
          window.location.reload(true); // Hard reload
        });
      } else {
        localStorage.setItem('app_version', htmlVersion);
        window.location.reload(true);
      }
      return false;
    }

    localStorage.setItem('app_version', htmlVersion);
    return true;
  }

  // Check version before proceeding
  if (!checkVersion()) {
    return; // Will reload
  }

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
    rawBtn: document.getElementById("rawBtn"),
    themeToggle: document.getElementById("themeToggle"),
    dashboardView: document.getElementById("dashboardView"),
    problemsView: document.getElementById("problemsView"),
    viewTitle: document.getElementById("viewTitle")
  };

  // State
  const state = {
    track:"", type:"", category:"", tags:new Set(), q:"",
    list:[], selectedIndex:-1, currentView: "dashboard"
  };

  // Theme Management
  function initTheme() {
    const savedTheme = localStorage.getItem('theme') || 'dark';
    document.documentElement.setAttribute('data-theme', savedTheme);
    updateThemeIcon(savedTheme);
  }

  function updateThemeIcon(theme) {
    if (elements.themeToggle) {
      elements.themeToggle.textContent = theme === 'dark' ? '🌙' : '☀️';
    }
  }

  function toggleTheme() {
    const current = document.documentElement.getAttribute('data-theme') || 'dark';
    const newTheme = current === 'dark' ? 'light' : 'dark';
    document.documentElement.setAttribute('data-theme', newTheme);
    localStorage.setItem('theme', newTheme);
    updateThemeIcon(newTheme);
  }

  if (elements.themeToggle) {
    elements.themeToggle.addEventListener('click', toggleTheme);
  }
  initTheme();

  // View Management
  function switchView(view) {
    state.currentView = view;

    if (view === 'dashboard') {
      if (elements.dashboardView) elements.dashboardView.style.display = 'grid';
      if (elements.problemsView) elements.problemsView.style.display = 'none';
      if (elements.viewTitle) elements.viewTitle.textContent = '📊 Dashboard';
    } else {
      if (elements.dashboardView) elements.dashboardView.style.display = 'none';
      if (elements.problemsView) elements.problemsView.style.display = 'block';
      if (elements.viewTitle) elements.viewTitle.textContent = '🔍 Problems';
      render();
    }

    // Update toggle buttons
    document.querySelectorAll('.view-toggle-btn').forEach(btn => {
      btn.classList.toggle('active', btn.getAttribute('data-view') === view);
    });
  }

  // View toggle listeners
  document.querySelectorAll('.view-toggle-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      switchView(btn.getAttribute('data-view'));
    });
  });

  // Dashboard Analytics
  function calculateStats() {
    const items = data.items || [];
    const total = items.length;
    const solved = items.length;

    // Difficulty breakdown
    const difficulties = { Easy: 0, Medium: 0, Hard: 0 };
    items.forEach(item => {
      if (item.difficulty && difficulties[item.difficulty] !== undefined) {
        difficulties[item.difficulty]++;
      }
    });

    // Track breakdown
    const tracks = {};
    items.forEach(item => {
      tracks[item.track] = (tracks[item.track] || 0) + 1;
    });

    // Tag frequency
    const tagFreq = {};
    items.forEach(item => {
      (item.tags || []).forEach(tag => {
        tagFreq[tag] = (tagFreq[tag] || 0) + 1;
      });
    });

    // Recent activity (last 10)
    const recent = [...items].sort((a, b) => b.id - a.id).slice(0, 10);

    // Calculate streak (mock for now - would need actual solve dates)
    const streak = calculateStreak(items);

    return {
      total, solved, difficulties, tracks, tagFreq, recent, streak
    };
  }

  function calculateStreak(items) {
    // Mock streak calculation
    // In production, you'd parse git history or track solve dates
    return Math.min(items.length, 7);
  }

  function animateCounter(element, target, duration = 1000) {
    const start = 0;
    const startTime = performance.now();

    function update(currentTime) {
      const elapsed = currentTime - startTime;
      const progress = Math.min(elapsed / duration, 1);
      const current = Math.floor(progress * target);
      element.textContent = current;

      if (progress < 1) {
        requestAnimationFrame(update);
      } else {
        element.textContent = target;
      }
    }

    requestAnimationFrame(update);
  }

  function renderDashboard() {
    if (!elements.dashboardView) return;

    const stats = calculateStats();
    const progressPercent = stats.total > 0 ? Math.round((stats.solved / stats.total) * 100) : 0;

    elements.dashboardView.innerHTML = `
      <!-- Total Progress Card -->
      <div class="progress-card">
        <h3>Total Progress</h3>
        <div class="progress-value animate-count" data-target="${stats.solved}">${stats.solved}</div>
        <div class="progress-label">Problems Solved</div>
        <div class="progress-bar-container">
          <div class="progress-bar" style="width: ${progressPercent}%"></div>
        </div>
      </div>

      <!-- Streak Card -->
      <div class="progress-card">
        <h3>Current Streak</h3>
        <div class="streak-display">
          <div class="streak-icon">🔥</div>
          <div class="streak-info">
            <div class="streak-number animate-count" data-target="${stats.streak}">${stats.streak}</div>
            <div class="streak-text">days in a row</div>
          </div>
        </div>
      </div>

      <!-- Track Progress Card -->
      <div class="progress-card">
        <h3>Tracks</h3>
        <div style="display: flex; flex-direction: column; gap: 8px; margin-top: 10px;">
          ${Object.entries(stats.tracks).map(([track, count]) => `
            <div style="display: flex; justify-content: space-between; align-items: center;">
              <span style="font-size: 14px; color: var(--muted);">${escapeHtml(track)}</span>
              <span style="font-size: 18px; font-weight: 600; color: var(--accent);">${count}</span>
            </div>
          `).join('')}
        </div>
      </div>

      <!-- Charts Grid -->
      <div class="charts-grid">
        <!-- Difficulty Distribution -->
        <div class="chart-card">
          <h3 class="chart-title">Difficulty Distribution</h3>
          <div class="difficulty-bars">
            <div class="difficulty-bar-item">
              <div class="difficulty-bar-label easy">Easy</div>
              <div class="difficulty-bar-track">
                <div class="difficulty-bar-fill easy" style="width: ${stats.total > 0 ? (stats.difficulties.Easy / stats.total * 100) : 0}%">
                  ${stats.difficulties.Easy}
                </div>
              </div>
            </div>
            <div class="difficulty-bar-item">
              <div class="difficulty-bar-label medium">Medium</div>
              <div class="difficulty-bar-track">
                <div class="difficulty-bar-fill medium" style="width: ${stats.total > 0 ? (stats.difficulties.Medium / stats.total * 100) : 0}%">
                  ${stats.difficulties.Medium}
                </div>
              </div>
            </div>
            <div class="difficulty-bar-item">
              <div class="difficulty-bar-label hard">Hard</div>
              <div class="difficulty-bar-track">
                <div class="difficulty-bar-fill hard" style="width: ${stats.total > 0 ? (stats.difficulties.Hard / stats.total * 100) : 0}%">
                  ${stats.difficulties.Hard}
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Top Tags Cloud -->
        <div class="chart-card">
          <h3 class="chart-title">Popular Tags</h3>
          <div class="tag-cloud">
            ${Object.entries(stats.tagFreq)
              .sort((a, b) => b[1] - a[1])
              .slice(0, 15)
              .map(([tag, count]) => {
                const size = 12 + Math.min(count * 2, 12);
                return `<span class="tag-cloud-item" style="font-size: ${size}px;">${escapeHtml(tag)} (${count})</span>`;
              }).join('')}
          </div>
        </div>

        <!-- Recent Activity -->
        <div class="chart-card">
          <h3 class="chart-title">Recent Activity</h3>
          <div class="recent-list">
            ${stats.recent.map(item => `
              <div class="recent-item" onclick="openItemById(${item.id}, '${item.track}', '${item.type}')">
                <div class="recent-item-icon">✅</div>
                <div class="recent-item-content">
                  <div class="recent-item-title">${String(item.id).padStart(4, '0')} - ${escapeHtml(item.title || 'Untitled')}</div>
                  <div class="recent-item-meta">${escapeHtml(item.track)} · ${(item.type || '').toUpperCase()} · ${escapeHtml(item.difficulty || '')}</div>
                </div>
              </div>
            `).join('')}
          </div>
        </div>
      </div>
    `;

    // Animate counters
    document.querySelectorAll('.animate-count').forEach(el => {
      const target = parseInt(el.getAttribute('data-target') || el.textContent);
      animateCounter(el, target);
    });
  }

  function renderFeatures() {
    const featuresGrid = document.getElementById('featuresGrid');
    if (!featuresGrid) return;

    const features = [
      {
        icon: '<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="16 18 22 12 16 6"></polyline><polyline points="8 6 2 12 8 18"></polyline></svg>',
        title: 'GraphQL API Integration',
        description: 'Scrapes problem metadata from LeetCode using official GraphQL endpoint. Fetches ID, title, difficulty, tags, and code templates automatically.',
        tech: 'Python + Requests + GraphQL'
      },
      {
        icon: '<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path><polyline points="14 2 14 8 20 8"></polyline><line x1="12" y1="18" x2="12" y2="12"></line><line x1="9" y1="15" x2="15" y2="15"></line></svg>',
        title: 'Automated File Generation',
        description: 'Creates solution files with proper headers, updates CSV trackers, rebuilds JSON plans, and generates markdown checklists—all from one command.',
        tech: 'CLI Wizard + Multi-Format'
      },
      {
        icon: '<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z"></path><polyline points="7.5 4.21 12 6.81 16.5 4.21"></polyline><polyline points="7.5 19.79 7.5 14.6 3 12"></polyline><polyline points="21 12 16.5 14.6 16.5 19.79"></polyline><polyline points="3.27 6.96 12 12.01 20.73 6.96"></polyline><line x1="12" y1="22.08" x2="12" y2="12"></line></svg>',
        title: 'Registry-Based Architecture',
        description: 'Extensible track system using JSON registry. Supports multiple problem sets (LeetCode 75, Top 150, SQL 50) with automatic language detection.',
        tech: 'JSON Config + Dynamic Loading'
      },
      {
        icon: '<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="12" y1="1" x2="12" y2="23"></line><path d="M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"></path></svg>',
        title: 'Git Workflow Automation',
        description: 'Auto-generates conventional commit messages, stages files, commits, and optionally pushes to remote—all with proper formatting and co-author attribution.',
        tech: 'Git + Shell Scripts'
      },
      {
        icon: '<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="3" width="18" height="18" rx="2" ry="2"></rect><line x1="3" y1="9" x2="21" y2="9"></line><line x1="9" y1="21" x2="9" y2="9"></line></svg>',
        title: 'Real-Time Analytics',
        description: 'Interactive dashboard with difficulty breakdown, tag frequency analysis, progress tracking, and problem search—all built with vanilla JavaScript.',
        tech: 'Vanilla JS + GitHub Pages'
      },
      {
        icon: '<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"></circle><polyline points="12 6 12 12 16 14"></polyline></svg>',
        title: '5-10min → 30sec Setup',
        description: 'Reduced problem setup time by 90%. One URL paste replaces manual data entry, file creation, tracker updates, and git operations.',
        tech: 'End-to-End Automation'
      }
    ];

    featuresGrid.innerHTML = features.map(feature => `
      <div class="feature-card">
        <div class="feature-icon">${feature.icon}</div>
        <h3 class="feature-title">${escapeHtml(feature.title)}</h3>
        <p class="feature-description">${escapeHtml(feature.description)}</p>
        <div class="feature-tech">${escapeHtml(feature.tech)}</div>
      </div>
    `).join('');
  }

  function updateHeroStats() {
    const stats = calculateStats();
    const heroTotal = document.getElementById('heroTotalProblems');
    const heroTracks = document.getElementById('heroTracks');

    if (heroTotal) {
      animateCounter(heroTotal, stats.solved);
    }
    if (heroTracks) {
      animateCounter(heroTracks, Object.keys(stats.tracks).length);
    }
  }

  // Make openItemById globally accessible
  window.openItemById = function(id, track, type) {
    state.track = track;
    state.type = type;
    if (elements.trackSel) elements.trackSel.value = track;
    if (elements.typeSel) elements.typeSel.value = type;

    switchView('problems');
    render();

    const idx = state.list.findIndex(x => x.id === id && x.track === track && x.type === type);
    if (idx >= 0) {
      setTimeout(() => openItem(idx), 100);
    }
  };

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

    const fragment = document.createDocumentFragment();

    filteredTagList.forEach(tag => {
      const el = document.createElement("span");
      el.className = "tag" + (state.tags.has(tag) ? " active" : "");
      el.textContent = tag;
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

  const debouncedTagSearch = debounce(() => {
    if (!elements.tagSearch || !data.tags) return;
    const q = elements.tagSearch.value.toLowerCase().trim();
    filteredTagList = data.tags.filter(t => t.toLowerCase().includes(q));
    renderTags();
  }, 200);

  if (elements.tagSearch) elements.tagSearch.oninput = debouncedTagSearch;
  renderTags();

  const debouncedSearch = debounce(() => {
    if (!elements.qInput) return;
    state.q = elements.qInput.value.toLowerCase();
    render();
  }, 300);

  if (elements.qInput) elements.qInput.oninput = debouncedSearch;

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
    elements.refreshBtn.onclick = () => {
      // Clear all caches before reload
      if ('caches' in window) {
        caches.keys().then(names => {
          names.forEach(name => caches.delete(name));
        }).then(() => {
          window.location.reload(true);
        });
      } else {
        window.location.reload(true);
      }
    };
  }

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

  function render(){
    if (!elements.cards) return;

    state.list = filterItems();

    if (elements.statsEl) {
      elements.statsEl.textContent = `${state.list.length} / ${data.items ? data.items.length : 0} shown`;
    }

    const fragment = document.createDocumentFragment();
    state.list.forEach((item, i) => {
      fragment.appendChild(createCard(item, i));
    });

    elements.cards.innerHTML = '';
    elements.cards.appendChild(fragment);
  }

  // Initial render
  renderFeatures();
  updateHeroStats();
  renderDashboard();
  render();

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

  function tryOpenFromHash(){
    const h = new URLSearchParams(location.hash.replace(/^#/, ""));
    const val = h.get("item");
    if (!val) return;

    const [track, type, idStr] = val.split(":");
    const id = Number(idStr);

    if (elements.trackSel) { elements.trackSel.value = track || ""; state.track = elements.trackSel.value; }
    if (elements.typeSel) { elements.typeSel.value = type || ""; state.type = elements.typeSel.value; }

    switchView('problems');
    render();
    const idx = state.list.findIndex(x => x.track === track && x.type === type && x.id === id);
    if (idx >= 0) openItem(idx);
  }

  window.addEventListener("hashchange", tryOpenFromHash);
  tryOpenFromHash();
})();
