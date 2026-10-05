document.addEventListener(
  "yt-player-updated",
  (e) => {
    window.postMessage(
      { type: "yt-player-updated", payload: e.detail.getVideoData().title },
      "*"
    );
  },
  { capture: true }
);
