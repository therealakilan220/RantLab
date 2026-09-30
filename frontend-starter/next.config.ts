import type { NextConfig } from "next";

// The browser only ever calls relative /api/... URLs. Next.js forwards them to FastAPI,
// so there is no CORS problem and one HTTPS tunnel (to port 3000) is enough for phones.
const nextConfig: NextConfig = {
  experimental: {
    // Local LLM answers can take 20 s or more; the default proxy timeout is 30 s.
    proxyTimeout: 120_000,
  },
  async rewrites() {
    const backend = process.env.BACKEND_URL ?? "http://localhost:8000";
    return [{ source: "/api/:path*", destination: `${backend}/api/:path*` }];
  },
};

export default nextConfig;
