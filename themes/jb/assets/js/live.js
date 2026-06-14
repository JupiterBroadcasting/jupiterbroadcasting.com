document.addEventListener("DOMContentLoaded", function () {
  const audioPlayer = document.querySelector("#audio-player audio");
  const videoEl = document.querySelector("#hls-video");
  const toggleButton = document.querySelector("#toggle-button");
  const videoSrc = videoEl.dataset.videoSrc;

  function initHls() {
    if (typeof Hls !== "undefined" && Hls.isSupported()) {
      let hls = new Hls();
      hls.loadSource(videoSrc);
      hls.attachMedia(videoEl);
      hls.on(Hls.Events.ERROR, function (event, data) {
        if (data.fatal) {
          console.error("HLS fatal error:", data.type, data.details);
        }
      });
      return hls;
    } else if (videoEl.canPlayType("application/vnd.apple.mpegurl")) {
      videoEl.src = videoSrc;
    }
    return null;
  }

  let hls = initHls();

  function toggleStream() {
    let currentMode = audioPlayer.parentNode.style.display != 'none' ? 'audio' : 'video';

    if (currentMode == 'audio') {
      audioPlayer.pause();
      audioPlayer.parentNode.style.display = 'none';

      videoEl.parentNode.style.display = '';
      videoEl.play().catch(function (e) { console.warn("Autoplay prevented:", e); });
      toggleButton.textContent = "Switch to Audio";
    } else {
      videoEl.pause();
      videoEl.parentNode.style.display = 'none';

      audioPlayer.parentNode.style.display = '';
      audioPlayer.play().catch(function (e) { console.warn("Autoplay prevented:", e); });
      toggleButton.textContent = "Switch to Video";
    }
    toggleButton.setAttribute("aria-checked", currentMode == 'audio');
  }

  if (toggleButton) {
    toggleButton.addEventListener("click", toggleStream);
  }
});
