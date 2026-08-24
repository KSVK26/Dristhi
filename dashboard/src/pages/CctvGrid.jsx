// DRISHTI - Live CCTV Feed Grid
// Plays the stream URLs served by the backend using hls.js.
// Tile 4 is a placeholder for a DroidCam phone acting as an on-site IP camera:
//   1. Install "DroidCam" on any phone (free)
//   2. Note its WiFi URL, e.g. http://192.168.1.5:4747/video
//   3. Paste it into the input below to watch a REAL live site feed.

import { useEffect, useRef, useState } from "react";
import Hls from "hls.js";
import { api } from "../api.js";

function HlsPlayer({ url }) {
  const ref = useRef(null);

  useEffect(() => {
    const video = ref.current;
    if (!video || !url) return;
    let hls;
    if (Hls.isSupported()) {
      hls = new Hls();
      hls.loadSource(url);
      hls.attachMedia(video);
    } else if (video.canPlayType("application/vnd.apple.mpegurl")) {
      video.src = url; // Safari plays HLS natively
    }
    return () => hls && hls.destroy();
  }, [url]);

  return <video ref={ref} autoPlay muted controls playsInline className="cctv-video" />;
}

export default function CctvGrid() {
  const [streams, setStreams] = useState([]);
  const [droidUrl, setDroidUrl] = useState("");

  useEffect(() => {
    api("/cctv/streams").then(setStreams).catch(console.error);
  }, []);

  return (
    <div>
      <div className="toolbar">
        <h2>📹 Live CCTV Surveillance</h2>
        <span className="muted">
          Simulated institute feeds + your own phone as a real IP camera
        </span>
      </div>

      <div className="cctv-grid">
        {streams.map((s) => (
          <div key={s.id} className="cctv-tile">
            <div className="cctv-label">
              <span className="live-dot" /> {s.label}
            </div>
            {s.url === "droidcam" ? (
              droidUrl ? (
                <img src={droidUrl} alt="DroidCam live" className="cctv-video" />
              ) : (
                <div className="cctv-placeholder">
                  <p>No phone camera connected.</p>
                  <input
                    placeholder="http://192.168.x.x:4747/video"
                    value={droidUrl}
                    onChange={(e) => setDroidUrl(e.target.value)}
                  />
                  <small>Paste your DroidCam URL above</small>
                </div>
              )
            ) : (
              <HlsPlayer url={s.url} />
            )}
          </div>
        ))}
      </div>
    </div>
  );
}