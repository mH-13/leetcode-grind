(async function(){
  const res = await fetch("./data/index.json", {cache:"no-store"});
  const data = await res.json();

  const cardsEl = document.getElementById("cards");
  const trackSel = document.getElementById("track");
  const typeSel  = document.getElementById("type");
  const tagsEl   = document.getElementById("tags");
  const tagSearch = document.getElementById("tagSearch");
  const statsEl  = document.getElementById("stats");
  const resetBtn = document.getElementById("reset");

  // State
  const state = { track:"", type:"", tags:new Set() };

  // Build track options
  trackSel.innerHTML = `<option value="">All</option>` + data.tracks.map(t=>`<option>${t}</option>`).join("");
  trackSel.onchange = ()=>{ state.track = trackSel.value; render(); };

  // Build tag list
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

  // Type filter
  typeSel.onchange = ()=>{ state.type = typeSel.value; render(); };

  // Reset
  resetBtn.onclick = ()=>{
    state.track=""; trackSel.value="";
    state.type="";  typeSel.value="";
    state.tags.clear();
    tagSearch.value="";
    filteredTagList = data.tags.slice(); renderTags();
    render();
  };

  function ghUrl(item){
    return `https://github.com/mh-13/leetcode-grind/blob/main/${item.path}`;
  }

  function render(){
    const activeTags = [...state.tags];
    const items = data.items.filter(x=>{
      if (state.track && x.track !== state.track) return false;
      if (state.type && x.type !== state.type) return false;
      if (activeTags.length && !activeTags.every(t=>x.tags.includes(t))) return false;
      return true;
    });

    statsEl.textContent = `${items.length} / ${data.items.length} shown`;

    cardsEl.innerHTML = items.map(x=>{
      const chips = x.tags.map(t=>`<span class="chip">${t}</span>`).join("");
      return `
      <div class="card" onclick="window.open('${ghUrl(x)}','_blank')">
        <h3>${String(x.id).padStart(4,"0")} — ${x.title}</h3>
        <div class="meta">
          <span>${x.track}</span>
          <span>${x.type.toUpperCase()}</span>
          <span>${x.time || ""}${x.space ? " · "+x.space:""}</span>
        </div>
        <div class="chips">${chips}</div>
      </div>`;
    }).join("");
  }

  render();
})();
