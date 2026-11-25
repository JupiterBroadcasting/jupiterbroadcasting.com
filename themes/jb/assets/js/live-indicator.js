document.addEventListener("DOMContentLoaded", async () => {
  const nav = document.getElementById("mainnavigation");
  if (!nav || !nav.dataset.liveUrl) return;
  try {
    const response = await fetch(nav.dataset.liveUrl);
    if (!response.ok) return;
    const text = await response.text();
    // A live HLS playlist has no #EXT-X-ENDLIST
    if (text.includes("#EXTM3U") && !text.includes("#EXT-X-ENDLIST")) {
      nav.classList.add("is-live");
    }
  } catch (err) {
    // offline or CORS-blocked: leave the navbar unhighlighted
  }
});
