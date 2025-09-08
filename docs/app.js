(async function main(){
// per-load cache buster so we always bypass stale CDN/browser caches
const BUST = Date.now();
const data = await fetch(`./data/index.json?ts=${BUST}`, {cache:"no-store"}).then(r=>r.json());





  // ---------- owner/repo detection (no hardcoding)
  function detectOwnerRepo(){
    // If hosted on *.github.io/<repo>/...
    if (location.hostname.endsWith("github.io")) {
      const owner = location.hostname.split(".")[0];
      const pathParts = location.pathname.split("/").filter(Boolean);
      const repo = pathParts[0] || "leetcode-grind";
      return { owner, repo };
    }
    // Fallback to defaults (edit if you serve elsewhere)
    return { owner: "mh-13", repo: "leetcode-grind" };
  }
  const OR = detectOwnerRepo();
  const BRANCHES = ["main", "master", "gh-pages"]; // try in this order

  async function fetchRawWithFallback(path){
    let lastErr = null;
    for (const branch of BRANCHES){
      const url = `https://raw.githubusercontent.com/${OR.owner}/${OR.repo}/${branch}/${path}?ts=${Date.now()}`;
      try {
        const res = await fetch(url, {cache:"no-store"});
        if (res.ok) {
          const txt = await res.text();
          return { txt, url, branch };
        }
        lastErr = { status: res.status, url };
      } catch (e) {
        lastErr = { error: e, url };
      }
    }
    throw lastErr || new Error("Raw fetch failed");
  }

  function ghBlobUrl(path, branch="main"){
    return `https://github.com/${OR.owner}/${OR.repo}/blob/${branch}/${path}`;
  }
  function ghRawUrl(path, branch="main"){
    return `https://raw.githubusercontent.com/${OR.owner}/${OR.repo}/${branch}/${path}`;
  }

  // ---------- Elements
  const cardsEl = document.getElementById("cards");
  const trackSel = document.getElementById("track");
  const typeSel  = document.getElementById("type");
  const tagsEl   = document.getElementById("tags");
  const tagSearch = document.getElementById("tagSearch");
  const statsEl  = document.getElementById("stats");
  const resetBtn = document.getElementById("reset");
  const catSel   = document.getElementById("category");
  const qInput   = document.getElementById("q");

  // Modal elements
  const modal    = document.getElementById("modal");
  const codePre  = document.getElementById("codePre");
  const codeEl   = document.getElementById("codeEl");
  const modalTitle = document.getElementById("modalTitle");
  const modalMeta  = document.getElementById("modalMeta");
  const closeBtn = document.getElementById("closeBtn");
  const copyBtn  = document.getElementById("copyBtn");
  const ghBtn    = document.getElementById("ghBtn");
  const rawBtn   = document.getElementById("rawBtn");

  // ---------- State
  const state = { track:"", type:"", category:"", tags:new Set(), q:"", list:[], selectedIndex:-1, lastBranchTried:"main" };

  // ---------- Filters
  trackSel.innerHTML = `<option value="">All</option>` + data.tracks.map(t=>`<option>${t}</option>`).join("");
  catSel.innerHTML   = `<option value="">All</option>` + data.categories.map(c=>`<option>${c}</option>`).join("");
  trackSel.onchange  = ()=>{ state.track = trackSel.value; render(); };
  typeSel.onchange   = ()=>{ state.type = typeSel.value; render(); };
  catSel.onchange    = ()=>{ state.category = catSel.value; render(); };

  // Tags
  let filteredTagList = data.tags.slice();
  function renderTags(){
    tagsEl.innerHTML = "";
    filteredTagList.forEach(tag=>{
      const b = document.createElement("span");
      b.className = "tag" + (state.tags.has(tag) ? " active":"");
      b.textContent = tag;
      b.onclick = ()=>{
        if (state.tags.has(tag)) state.tags.delete(tag);
        else state.tags.add(tag);
        renderTags(); render();
      };
      tagsEl.appendChild(b);
    });
  }
  tagSearch.oninput = ()=>{
    const q = tagSearch.value.toLowerCase().trim();
    filteredTagList = data.tags.filter(t=>t.toLowerCase().includes(q));
    renderTags();
  };
  renderTags();

  // Text search
  qInput.oninput = ()=>{
    state.q = qInput.value.toLowerCase();
    render();
  };

  // Reset
  resetBtn.onclick = ()=>{
    state.track=""; trackSel.value="";
    state.type="";  typeSel.value="";
    state.category=""; catSel.value="";
    state.tags.clear(); tagSearch.value="";
    state.q=""; qInput.value="";
    filteredTagList = data.tags.slice(); renderTags();
    render();
  };

  // ---------- Filter + render
  function matchQuery(x){
    if (!state.q) return true;
    const hay = `${x.id} ${x.title} ${x.slug} ${x.tags.join(" ")}`.toLowerCase();
    return hay.includes(state.q);
  }
  function filterItems(){
    const t = state.track, ty = state.type, c = state.category, tags = [...state.tags];
    return data.items.filter(x=>{
      if (t && x.track !== t) return false;
      if (ty && x.type !== ty) return false;
      if (c && x.category !== c) return false;
      if (tags.length && !tags.every(tag=>x.tags.includes(tag))) return false;
      if (!matchQuery(x)) return false;
      return true;
    });
  }
  function cardHTML(x, idx){
    const chips = x.tags.slice(0,6).map(t=>`<span class="chip">${t}</span>`).join("");
    const meta  = [x.track, x.type.toUpperCase(), x.difficulty || "", x.category || ""].filter(Boolean).join(" · ");
    return `
      <div class="card" data-idx="${idx}">
        <h3>${String(x.id).padStart(4,"0")} — ${x.title}</h3>
        <div class="meta">${meta}</div>
        <div class="chips">${chips}</div>
      </div>`;
  }
  function render(){
    state.list = filterItems();
    statsEl.textContent = `${state.list.length} / ${data.items.length} shown`;
    cardsEl.innerHTML = state.list.map((x, i)=>cardHTML(x, i)).join("");
  }
  render();

  // ---------- Open modal on card click
  cardsEl.addEventListener("click", async (e)=>{
    const card = e.target.closest(".card");
    if (!card) return;
    const idx = Number(card.getAttribute("data-idx"));
    openItem(idx);
  });

  function langClass(item){
    return item.type === "py" ? "language-python" : (item.type === "sql" ? "language-sql" : "language-none");
  }

  async function openItem(idx){
    if (idx < 0 || idx >= state.list.length) return;
    state.selectedIndex = idx;
    const item = state.list[idx];

    modalTitle.textContent = `#${String(item.id).padStart(4,"0")} — ${item.title}`;
    modalMeta.textContent = [item.track, item.type.toUpperCase(), item.difficulty || "", item.category || "", (item.link || "")]
      .filter(Boolean).join(" · ");

    codeEl.className = langClass(item);
    codeEl.textContent = "Loading…";
    showModal(true);

    try {
      const { txt, url, branch } = await fetchRawWithFallback(item.path);
      state.lastBranchTried = branch;
      codeEl.textContent = txt;
      // links
      ghBtn.href  = ghBlobUrl(item.path, branch);
      rawBtn.href = url;
      // highlight
      if (window.Prism) Prism.highlightElement(codeEl);
      // deep link
      location.hash = `item=${encodeURIComponent(item.track)}:${item.type}:${item.id}`;
    } catch (err) {
      const attempted = BRANCHES.map(b=>ghRawUrl(item.path, b)).join("\n");
      codeEl.className = "language-none";
      codeEl.textContent = `404: Not Found\n\nTried:\n${attempted}\n\nCheck:\n• File path & name (4-digit id + slug)\n• Branch exists (main/master/gh-pages)\n• Pushed to GitHub`;
      ghBtn.href  = ghBlobUrl(item.path, "main");
      rawBtn.href = ghRawUrl(item.path, "main");
      console.warn("Fetch error:", err);
    }
  }

  function showModal(v){
    modal.classList.toggle("hidden", !v);
    modal.setAttribute("aria-hidden", String(!v));
    if (v) codePre.scrollTop = 0;
  }

  // Actions
  closeBtn.onclick = ()=>{ showModal(false); location.hash = ""; };
  copyBtn.onclick = async ()=>{
    try { await navigator.clipboard.writeText(codeEl.textContent || ""); copyBtn.textContent = "Copied ✓"; }
    catch { copyBtn.textContent = "Copy Failed"; }
    setTimeout(()=> copyBtn.textContent = "Copy", 1200);
  };

  // Keyboard nav
  window.addEventListener("keydown", (e)=>{
    if (modal.classList.contains("hidden")) return;
    if (e.key === "Escape"){ showModal(false); location.hash = ""; }
    if (e.key === "ArrowRight"){ openItem(Math.min(state.selectedIndex+1, state.list.length-1)); }
    if (e.key === "ArrowLeft"){ openItem(Math.max(state.selectedIndex-1, 0)); }
  });

  // Click backdrop to close
  modal.addEventListener("click",(e)=>{ if (e.target === modal) { showModal(false); location.hash = ""; } });

  // Deep link (#item=track:type:id)
  function tryOpenFromHash(){
    const h = new URLSearchParams(location.hash.replace(/^#/, ""));
    const val = h.get("item"); if (!val) return;
    const [track, type, idStr] = val.split(":");
    const id = Number(idStr);
    trackSel.value = track || ""; state.track = trackSel.value;
    typeSel.value  = type || "";  state.type  = typeSel.value;
    render();
    const idx = state.list.findIndex(x=> x.track === track && x.type === type && x.id === id);
    if (idx >= 0) openItem(idx);
  }
  window.addEventListener("hashchange", tryOpenFromHash);
  tryOpenFromHash();
})();
