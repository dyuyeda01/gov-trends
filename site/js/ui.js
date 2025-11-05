window.ui = {
  renderContractorCards(containerId, contractors) {
    const el = document.getElementById(containerId);
    el.innerHTML = "";
    contractors.forEach(c => {
      const card = document.createElement("div");
      card.className = "card";
      card.innerHTML = `
        <div class="text-sm text-slate-400">Ticker: ${c.ticker}</div>
        <div class="text-xl font-semibold">${c.name}</div>
        <div class="text-sm text-slate-400 mt-1">${c.sector || ""}</div>
      `;
      el.appendChild(card);
    });
  }
};
