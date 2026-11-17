import path from "node:path";
import type { NextConfig } from "next";

// The browser always calls /api/* on the Next.js origin; Next forwards it to the
// Python API. Same-origin means no CORS issues and auth cookies just work later.
// Override API_URL when the backend runs somewhere else.
const apiUrl = process.env.API_URL ?? "http://127.0.0.1:8000";

const nextConfig: NextConfig = {
  cacheComponents: true,
  partialPrefetching: true,
  turbopack: {
    // apps/web has its own lockfile; the repo root has one for dev tooling.
    root: path.join(__dirname),
    rules: {
      "*.css": {
        loaders: ["@tailwindcss/turbopack"],
        as: "*.css",
      },
    },
  },
  async rewrites() {
    return [{ source: "/api/:path*", destination: `${apiUrl}/api/:path*` }];
  },
};

export default nextConfig;
