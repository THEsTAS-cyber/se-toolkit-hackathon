import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  output: "standalone",
  async rewrites() {
    return [
      {
        source: "/api/games",
        destination: `${process.env.BACKEND_URL || "http://backend:8000"}/api/games`,
      },
      {
        source: "/api/games/:path*",
        destination: `${process.env.BACKEND_URL || "http://backend:8000"}/api/games/:path*`,
      },
    ];
  },
};

export default nextConfig;
