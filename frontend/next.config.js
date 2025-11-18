/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  swcMinify: true,
  // API proxying is handled by Next.js API Routes in app/api/v1/[[...path]]/route.ts
  // This allows Vercel deployment to proxy HTTPS -> HTTP backend requests
};

module.exports = nextConfig;
