/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  swcMinify: true,
  // Removed rewrites to allow direct client-side API calls
  // The frontend will use NEXT_PUBLIC_API_URL directly
};

module.exports = nextConfig;
