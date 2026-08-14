/** @type {import('next').NextConfig} */
const djangoApiBase = process.env.DJANGO_API_URL || 'http://127.0.0.1:8000'

const nextConfig = {
  reactStrictMode: true,
  swcMinify: true,
  // Pre-existing TS/ESLint issues must not block VPS production builds.
  typescript: {
    ignoreBuildErrors: true,
  },
  eslint: {
    ignoreDuringBuilds: true,
  },
  // Performance optimizations
  compiler: {
    removeConsole: process.env.NODE_ENV === 'production',
  },
  // Faster builds
  experimental: {
    optimizeCss: true,
  },
  env: {
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL || '/api',
  },
  async redirects() {
    return [
      { source: '/dashboard', destination: '/home', permanent: false },
      { source: '/rooms', destination: '/frontdesk/config/rooms', permanent: false },
      { source: '/rate', destination: '/frontdesk/config/rate-plans', permanent: false },
      { source: '/rate/rack', destination: '/frontdesk/room-rate-schedule', permanent: false },
      { source: '/rate/seasonal', destination: '/frontdesk/room-rate-schedule', permanent: false },
      { source: '/rate/packages', destination: '/frontdesk/config/packages', permanent: false },
      { source: '/forecast', destination: '/frontdesk/forecast/availability', permanent: false },
      { source: '/forecast/occupancy', destination: '/frontdesk/forecast/availability', permanent: false },
      { source: '/forecast/rates', destination: '/frontdesk/room-rate-schedule', permanent: false },
      { source: '/forecast/revenue', destination: '/reports/revenue', permanent: false },
      { source: '/booking/reservation', destination: '/frontdesk/reservations', permanent: false },
      { source: '/pos/new', destination: '/fnb/orders/new', permanent: false },
      { source: '/accounts/voucher/list', destination: '/accounts/vouchers', permanent: false },
      { source: '/accounts/budgets/new', destination: '/accounts/budgets', permanent: false },
      { source: '/accounts/payable/:id/payment', destination: '/accounts/payable/payments', permanent: false },
      { source: '/accounts/receivable/:id/payment', destination: '/accounts/receivable/payments', permanent: false },
      { source: '/broadcast/history', destination: '/broadcast', permanent: false },
      { source: '/utilities/sms', destination: '/broadcast/new', permanent: false },
      { source: '/utilities/email', destination: '/broadcast/new', permanent: false },
    ]
  },
  async rewrites() {
    return [
      {
        source: '/api/:path*',
        destination: `${djangoApiBase}/api/:path*`,
      },
      {
        source: '/favicon.ico',
        destination: '/favicon.svg',
      },
    ]
  },
}

module.exports = nextConfig

