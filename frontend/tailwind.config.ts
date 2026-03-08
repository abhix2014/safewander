import type { Config } from 'tailwindcss';

const config: Config = {
  content: ['./app/**/*.{js,ts,jsx,tsx}', './components/**/*.{js,ts,jsx,tsx}'],
  theme: {
    extend: {
      colors: {
        saffron: '#FF6B1A',
        ganga: '#00B4D8',
        gold: '#FFB627',
        verified: '#00C896',
        bgPrimary: '#120900',
        bgSecondary: '#0D1A10'
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif']
      }
    }
  },
  plugins: []
};

export default config;
