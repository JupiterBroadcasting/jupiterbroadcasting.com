document.addEventListener("DOMContentLoaded", function () {
  const audioPlayer = document.querySelector("#audio-player audio");
  const videoEl = document.querySelector("#hls-video");
  const toggleButton = document.querySelector("#toggle-button");
  const videoSrc = videoEl.dataset.videoSrc;
  const offlineOverlay = document.querySelector("#stream-offline");
  const retryButton = document.querySelector("#retry-button");

  let hls = null;
  let retryTimer = null;
  let isOffline = false;
  let connecting = false;
  const RETRY_INTERVAL = 15000;

  function showOffline() {
    if (isOffline) return;
    isOffline = true;
    offlineOverlay.classList.add("is-visible");
  }

  function hideOffline() {
    isOffline = false;
    offlineOverlay.classList.remove("is-visible");
  }

  function destroyHls() {
    if (hls) {
      hls.destroy();
      hls = null;
    }
  }

  function startRetryTimer() {
    stopRetryTimer();
    retryTimer = setInterval(function () {
      attemptConnect();
    }, RETRY_INTERVAL);
  }

  function stopRetryTimer() {
    if (retryTimer) {
      clearInterval(retryTimer);
      retryTimer = null;
    }
  }

  function attemptConnect() {
    if (connecting) return;
    connecting = true;
    destroyHls();

    if (typeof Hls !== "undefined" && Hls.isSupported()) {
      hls = new Hls();

      hls.loadSource(videoSrc);
      hls.attachMedia(videoEl);

      hls.on(Hls.Events.MANIFEST_PARSED, function () {
        connecting = false;
        hideOffline();
        stopRetryTimer();
        videoEl.play().catch(function (e) {
          console.warn("Autoplay prevented:", e);
        });
      });

      hls.on(Hls.Events.ERROR, function (event, data) {
        if (data.fatal) {
          connecting = false;
          console.error("HLS fatal error:", data.type, data.details);
          if (data.type === Hls.ErrorTypes.NETWORK_ERROR) {
            showOffline();
            startRetryTimer();
          } else if (data.type === Hls.ErrorTypes.MEDIA_ERROR) {
            showOffline();
            startRetryTimer();
          } else {
            showOffline();
          }
        }
      });
    } else if (videoEl.canPlayType("application/vnd.apple.mpegurl")) {
      videoEl.src = videoSrc;

      videoEl.addEventListener("error", function handleSafariError() {
        connecting = false;
        showOffline();
        startRetryTimer();
        videoEl.removeEventListener("error", handleSafariError);
      });

      videoEl.addEventListener("loadedmetadata", function handleSafariLoaded() {
        connecting = false;
        hideOffline();
        stopRetryTimer();
        videoEl.removeEventListener("loadedmetadata", handleSafariLoaded);
      });
    }
  }

  attemptConnect();

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

  if (retryButton) {
    retryButton.addEventListener("click", function () {
      stopRetryTimer();
      showOffline();
      attemptConnect();
    });
  }

  window.addEventListener("beforeunload", function () {
    stopRetryTimer();
    destroyHls();
  });
});
