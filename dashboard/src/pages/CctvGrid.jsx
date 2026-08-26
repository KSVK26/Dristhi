// DRISHTI - Live CCTV Feed Grid
// 3 self-hosted loops in /dashboard/public/cctv (mp4) + 1 DroidCam tile
// for a real live phone feed. The looping tiles carry a surveillance
// overlay: pulsing REC dot, ticking timestamp, scanline + vignette.
// If a stream fails, the tile shows a clean "Offline" placeholder.

import { useEffect, useRef, useState } from "react";
import Hls from "hls.js";
import { api } from "../api.js";

const isRelative = (u) => typeof u === "string" && u.startsWith("/");

function LoopingTile({ url }) {
  const [failed, setFailed] = useState(false);

  if (failed) {
    return (
      <div className="cctv-placeholder">
        <p>⚠ Stream Offline</p>
        <small>The camera feed could not be reached.</small>
      </div>
    );
  }
  return (
    <video
      src={url}
      autoPlay muted loop playsInline controls
      className="cctv-video"
      onError={() => setFailed(true)}
    />
  );
}

function HlsPlayer({ url }) {
  const ref = useRef(null);
  const [failed, setFailed] = useState(false);

  useEffect(() => {
    const video = ref.current;
    if (!video || !url) return;
    setFailed(false);
    let hls;
    if (Hls.isSupported()) {
      hls = new Hls({ manifestLoadingTimeOut: 8000, levelLoadingTimeOut: 8000 });
      hls.on(Hls.Events.ERROR, (_evt, data) => {
        if (data.fatal) setFailed(true);
      });
      hls.loadSource(url);
      hls.attachMedia(video);
    } else if (video.canPlayType("application/vnd.apple.mpegurl")) {
      video.src = url; // Safari plays HLS natively
    }
    return () => hls && hls.destroy();
  }, [url]);

  if (failed) {
    return (
      <div className="cctv-placeholder">
        <p>⚠ Stream Offline</p>
        <small>The camera feed could not be reached.</small>
      </div>
    );
  }
  return (
    <video
      ref={ref}
      autoPlay muted controls playsInline
      className="cctv-video"
      onError={() => setFailed(true)}
    />
  );
}

function SurveillanceOverlay({ id, label }) {
  // Ticking live timestamp — proves the feed is "live" on stage
  const [now, setNow] = useState(new Date());
  useEffect(() => {
    const t = setInterval(() => setNow(new Date()), 1000);
    return () => clearInterval(t);
  }, []);
  return (
    <>
      <div className="cctv-label">
        <span className="live-dot" /> REC · {now.toLocaleTimeString("en-IN")}
      </div>
      <div className="cctv-corner cam-id">CAM&nbsp;0{id}&nbsp;·&nbsp;{label}</div>
      <div className="cctv-corner cam-tc">DRISHTI&nbsp;CCTV</div>
      <div className="cctv-scanlines" />
    </>
  );
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
          3 self-hosted institute feeds + your phone as a real IP camera
        </span>
      </div>

      <div className="cctv-grid">
        {streams.map((s) => (
          <div key={s.id} className="cctv-tile">
            {s.url === "droidcam" ? (
              <>
                <div className="cctv-label">
                  <span className="live-dot" /> {s.label}
                </div>
                {droidUrl ? (
                  <img src={droidUrl} alt="DroidCam live" className="cctv-video" />
                ) : (
                  <div className="cctv-placeholder">
                    <p>No phone camera connected.</p>
                    <input
                      placeholder="http://192.168.x.x:4747/video"
                      value={droidUrl}
                      onChange={(e) => setDroidUrl(e.target.value)}
                    />
                    <small>Install DroidCam on any phone and paste the URL above</small>
                  </div>
                )}
              </>
            ) : isRelative(s.url) ? (
              <>
                <LoopingTile url={s.url} />
                <SurveillanceOverlay id={s.id} label={s.label} />
              </>
            ) : (
              <>
                <HlsPlayer url={s.url} />
                <div className="cctv-label">
                  <span className="live-dot" /> {s.label}
                </div>
              </>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}