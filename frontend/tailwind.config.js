/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './pages/**/*.{js,ts,jsx,tsx,mdx}',
    './components/**/*.{js,ts,jsx,tsx,mdx}',
    './app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        background: 'var(--background)',
        foreground: 'var(--foreground)',
        gyoroom: {
          sidebar: '#2c3e50',
          page: '#f0f2f5',
          vacant: '#28a745',
          occupied: '#dc3545',
          reserved: '#007bff',
          arrival: '#ffc107',
          departure: '#17a2b8',
          dirty: '#ff6b81',
          clean: '#1abc9c',
          cleaning: '#f1c40f',
          maintenance: '#95a5a6',
          revenue: '#28a745',
          collection: '#e83e8c',
          adr: '#007bff',
          chart: '#6c5ce7',
        },
      },
    },
  },
  plugins: [],
}

