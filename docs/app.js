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
  const catSel   = document.getElementById("category");

  const state = { track:"", type:"", category:"", tags:new Set() };

  trackSel.innerHTML = `<option value="">All</option>` + data.tracks.map(t=>`<option>${t}</option>`).join("");
  trackSel.onchange = ()=>{ state.track = trackSel.value; render(); };

  catSel.innerHTML = `<option value="">All</option>` + data.categories.map(c=>`<option>${c}</option>`).join("");
  catSel.onchange = ()=>{ state.category = catSel.value; render(); };

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

  typeSel.onchange = ()=>{ state.type = typeSel.value; render(); };
  resetBtn.onclick = ()=>{
    state.track=""; trackSel.value="";
    state.type="";  typeSel.value="";
    state.category=""; catSel.value="";
    state.tags.clear(); tagSearch.value="";
    filteredTagList = data.tags.slice(); renderTags();
    render();
  };

  function ghUrl(item){
    return `https://github.com/mh-13/leetcode-grind/blob/main/${item.path}`;
  }

  function badge(text){ return `<span class="chip">${text}</span>`; }

  function render(){
    const activeTags = [...state.tags];
    const items = data.items.filter(x=>{
      if (state.track && x.track !== state.track) return false;
      if (state.type && x.type !== state.type) return false;
      if (state.category && x.category !== state.category) return false;
      if (activeTags.length && !activeTags.every(t=>x.tags.includes(t))) return false;
      return true;
    });
    statsEl.textContent = `${items.length} / ${data.items.length} shown`;
    cardsEl.innerHTML = items.map(x=>{
      const chips = x.tags.map(badge).join("");
      const meta = [x.track, x.type.toUpperCase(), x.difficulty || "", x.category || ""].filter(Boolean).join(" · ");
      return `
      <div class="card" onclick="window.open('${ghUrl(x)}','_blank')">
        <h3>${String(x.id).padStart(4,"0")} — ${x.title}</h3>
        <div class="meta">${meta}</div>
        <div class="chips">${chips}</div>
      </div>`;
    }).join("");
  }
  render();
})();
