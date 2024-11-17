/** @type {import('next').NextConfig} */
const nextConfig = {
    reactStrictMode: true,
    // Keep your existing rewrites
    async rewrites() {
        return [
            {
                source: '/api/:path*',
                destination: process.env.NODE_ENV === 'development'
                    ? 'http://127.0.0.1:5328/:path*'  // Local development
                    : '/api/:path*'  // Production/Vercel
            }
        ]
    },
    // hot reloading
    webpack: (config) => {
        config.watchOptions = {
            poll: 1000,
            aggregateTimeout: 300,
            ignored: /node_modules/
        }
        return config
    },
    // Add development-specific settings
    pageExtensions: ['js', 'jsx', 'ts', 'tsx'],
}

module.exports = nextConfig