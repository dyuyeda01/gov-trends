window.api = {
  base: "./data/",
  async getJSON(name) {
    const res = await fetch(this.base + name, { cache: "no-store" });
    if (!res.ok) throw new Error("Failed to fetch " + name);
    return await res.json();
  },
};
