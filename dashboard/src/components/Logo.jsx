// DRISHTI logo - vector recreation of the lotus-eye mark.
// Palette: navy #0E1A2F (petals), blue #2563EB (iris), white (sclera).
// <Logo size={40} /> renders the mark; <Logo withWordmark /> adds text.

export default function Logo({ size = 36, withWordmark = false, light = false }) {
  return (
    <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
      <svg width={size} height={size} viewBox="0 0 64 64" fill="none">
        {/* outer petals */}
        <path d="M32 40 C18 36 10 28 8 16 C20 18 28 24 32 34 Z" fill="#0E1A2F" />
        <path d="M32 40 C46 36 54 28 56 16 C44 18 36 24 32 34 Z" fill="#0E1A2F" />
        {/* mid petals */}
        <path d="M32 42 C22 38 17 30 16 20 C25 23 30 29 32 36 Z" fill="#16294A" />
        <path d="M32 42 C42 38 47 30 48 20 C39 23 34 29 32 36 Z" fill="#16294A" />
        {/* center petal */}
        <path d="M32 4 C26 14 24 24 32 38 C40 24 38 14 32 4 Z" fill="#0E1A2F" />
        {/* eye */}
        <path d="M23 27 C26 22 38 22 41 27 C38 32 26 32 23 27 Z" fill="#FFFFFF" />
        <circle cx="32" cy="27" r="4.2" fill="#2563EB" />
        <circle cx="33.4" cy="25.6" r="1.3" fill="#FFFFFF" />
        <circle cx="32" cy="27" r="1.6" fill="#0E1A2F" />
      </svg>
      {withWordmark && (
        <div style={{ lineHeight: 1 }}>
          <div style={{
            fontSize: size * 0.52, fontWeight: 700, letterSpacing: 1,
            color: light ? "#fff" : "#0E1A2F",
          }}>
            drishti
          </div>
          <div style={{ fontSize: size * 0.22, color: "#64748B", letterSpacing: 2 }}>
            MoSJE · SIH 26095
          </div>
        </div>
      )}
    </div>
  );
}
