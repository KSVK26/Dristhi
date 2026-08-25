// Parse latitude/longitude out of a pasted Google Maps URL.
// Supports the common link shapes Google produces:
//   pin drop share : https://www.google.com/maps?q=28.6139,77.2090
//   browse view    : https://www.google.com/maps/@28.6139,77.2090,17z
//   place params   : https://www.google.com/maps?ll=28.6139,77.2090
//   3D embed style : https://...!3d28.6139!4d77.2090...
// Returns { lat, lng } or null when nothing sensible was found.
export function parseMapsLink(raw) {
  if (!raw) return null;
  const url = String(raw).trim();

  // !3d<lat>!4d<lng>
  const m3d = url.match(/!3d(-?\d{1,3}\.\d+)!4d(-?\d{1,3}\.\d+)/);
  if (m3d) return valid(parseFloat(m3d[1]), parseFloat(m3d[2]));

  // @lat,lng          (also matches /@lat,lng,zoom)
  const mAt = url.match(/@(-?\d{1,3}\.\d+),\s*(-?\d{1,3}\.\d+)/);
  if (mAt) return valid(parseFloat(mAt[1]), parseFloat(mAt[2]));

  // q=lat,lng  |  ll=lat,lng  |  query=lat,lng  |  sll=lat,lng
  const mQ = url.match(/[?&](?:q|ll|query|sll|destination)=(-?\d{1,3}\.\d+),\s*(-?\d{1,3}\.\d+)/);
  if (mQ) return valid(parseFloat(mQ[1]), parseFloat(mQ[2]));

  // bare "28.6139, 77.2090" typed straight into the box
  const mBare = url.match(/^(-?\d{1,3}\.\d+)\s*,\s*(-?\d{1,3}\.\d+)$/);
  if (mBare) return valid(parseFloat(mBare[1]), parseFloat(mBare[2]));

  return null;
}

function valid(lat, lng) {
  if (Math.abs(lat) > 90 || Math.abs(lng) > 180) return null;
  return {
    lat: Number(lat.toFixed(6)),
    lng: Number(lng.toFixed(6)),
  };
}

// Short https://maps.app.goo.gl/xxx links hide the coordinates until the
// redirect is followed — that needs a server round-trip.
export function isShortMapsLink(raw) {
  return /maps\.app\.goo\.gl|goo\.gl\/maps/i.test(String(raw || ""));
}
