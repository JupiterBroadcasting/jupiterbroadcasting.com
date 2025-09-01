document.addEventListener("DOMContentLoaded", function () {
  const audioPlayer = document.querySelector("#audio-player audio");
  const videoPlayer = document.querySelector("#video-player iframe");
  const audioContainer = document.querySelector("#audio-player");
  const videoContainer = document.querySelector("#video-player");
  const toggleButton = document.querySelector("#toggle-button");
  const videoSrc = videoPlayer.dataset.videoSrc;

  let isAudio = true;
  let audioWasPlaying = false;

  function toggleStream() {
    if (isAudio) {
      // Pause audio and switch to video
      audioWasPlaying = !audioPlayer.paused;
      audioPlayer.pause();
      audioContainer.classList.add("live-hidden");
      videoContainer.classList.remove("live-hidden");
      // Load video if not loaded
      if (videoPlayer.getAttribute("src") !== videoSrc) {
        videoPlayer.src = videoSrc;
      }
      toggleButton.textContent = "Switch to Audio";
    } else {
      // Pause video and switch to audio.
      // To save bandwidth, we unload the iframe.
      videoPlayer.src = "about:blank";
      videoContainer.classList.add("live-hidden");
      audioContainer.classList.remove("live-hidden");
      if (audioWasPlaying) {
        audioPlayer.play();
      }
      toggleButton.textContent = "Switch to Video";
    }
    isAudio = !isAudio;
    toggleButton.setAttribute("aria-pressed", !isAudio);
  }

  if (toggleButton) {
    toggleButton.addEventListener("click", toggleStream);
  }
});
