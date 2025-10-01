document.addEventListener("DOMContentLoaded", function () {
  const audioPlayer = document.querySelector("#audio-player audio");
  const videoPlayer = document.querySelector("#video-player iframe");
  const toggleButton = document.querySelector("#toggle-button");
  const videoSrc = videoPlayer.dataset.videoSrc;

  function toggleStream() {
    currentMode = audioPlayer.parentNode.style.display != 'none' ? 'audio' : 'video';

    if (currentMode == 'audio')
    {
      audioPlayer.pause();
      audioPlayer.parentNode.style.display = 'none';

      videoPlayer.parentNode.style.display = '';
      videoPlayer.src = videoPlayer.getAttribute('src') !== videoSrc ? videoSrc : '';
      toggleButton.textContent = "Switch to Audio";
    }
    else {
      audioPlayer.play();
      audioPlayer.parentNode.style.display = '';

      videoPlayer.parentNode.style.display = 'none';
      videoPlayer.src = "about:blank";
      toggleButton.textContent = "Switch to Video";
    }
    toggleButton.setAttribute("aria-pressed", (mode == 'audio' ? true : false));
  }

  if (toggleButton) {
    toggleButton.addEventListener("click", toggleStream);
  }
});
