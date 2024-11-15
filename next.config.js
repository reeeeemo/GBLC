/** @type {import('next').NextConfig} */
const nextConfig = {
    reactStrictMode: true,
    async rewrites() {
        return [
            {
                source: '/api/:path*',
                destination: process.env.NODE_ENV === 'development'
                    ? 'http://127.0.0.1:5328/:path*'  // Local development
                    : '/api/:path*'  // Production/Vercel
            }
        ]
    }
}

module.exports = nextConfig