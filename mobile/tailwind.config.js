/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./src/pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/components/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        sahel: {
          50: '#fbf8ee',
          100: '#f5eece',
          200: '#eddca1',
          300: '#e3c26d',
          400: '#dbaa45',
          500: '#c88c2b',
          600: '#ad6e22',
          700: '#8c501f',
          800: '#734020',
          900: '#61361f',
        },
        savanna: {
          50: '#f2f9f3',
          100: '#e1f2e3',
          200: '#c4e5c8',
          300: '#97d1a0',
          400: '#64b570',
          500: '#40994d',
          600: '#2f7c3b',
          700: '#276231',
          800: '#234e2a',
          900: '#1e4125',
          950: '#0c2312',
        },
      },
    },
  },
  plugins: [],
};
