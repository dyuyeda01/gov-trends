function groupBy(arr, key) {
  return arr.reduce((acc, x) => {
    const k = x[key];
    (acc[k] ||= []).push(x);
    return acc;
  }, {});
}

window.charts = {
  renderStocksLine(canvasId, rows) {
    const byDate = {};
    rows.forEach(r => {
      (byDate[r.date] ||= []).push(r.close);
    });
    const labels = Object.keys(byDate).sort();
    const data = labels.map(d => {
      const vals = byDate[d];
      return vals.reduce((a,b)=>a+b,0)/vals.length;
    });
    new Chart(document.getElementById(canvasId), {
      type: "line",
      data: { labels, datasets: [{ label: "Avg Close", data, borderWidth: 2 }] },
      options: { responsive: true }
    });
  },

  renderStocksMulti(canvasId, rows) {
    const byTicker = groupBy(rows, "ticker");
    const labels = [...new Set(rows.map(r => r.date))].sort();
    const datasets = Object.entries(byTicker).map(([ticker, series]) => {
      const map = Object.fromEntries(series.map(s => [s.date, s.close]));
      return { label: ticker, data: labels.map(d => map[d] ?? null), borderWidth: 1 };
    });
    new Chart(document.getElementById(canvasId), {
      type: "line",
      data: { labels, datasets },
      options: { responsive: true }
    });
  },

  renderWorkforceLine(canvasId, rows) {
    const series = groupBy(rows, "series_id");
    const labels = [...new Set(rows.map(r => r.date))].sort();
    const datasets = Object.entries(series).map(([sid, vals]) => {
      const map = Object.fromEntries(vals.map(v => [v.date, v.value]));
      return { label: sid, data: labels.map(d => map[d] ?? null), borderWidth: 2 };
    });
    new Chart(document.getElementById(canvasId), {
      type: "line",
      data: { labels, datasets },
      options: { responsive: true }
    });
  },

  renderBudgetsBar(canvasId, rows) {
    const byAgency = groupBy(rows, "agency_name");
    const latest = Object.values(byAgency).map(a => a.sort((x,y)=>x.fiscal_year-y.fiscal_year).at(-1));
    const top = latest
      .filter(Boolean)
      .sort((a,b)=> (b.outlay_amount||0) - (a.outlay_amount||0))
      .slice(0,15);
    const labels = top.map(x => x.agency_name);
    const data = top.map(x => Math.round((x.outlay_amount || 0) / 1e9)); // billions
    new Chart(document.getElementById(canvasId), {
      type: "bar",
      data: { labels, datasets: [{ label: "Outlays (B$)", data }] },
      options: { indexAxis: "y", responsive: true }
    });
  }
};
