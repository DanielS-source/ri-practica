/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./src/**/*.{html,ts}",
  ],
  theme: {
    extend: {
      fontFamily: {
        roboto: ['Roboto', 'sans'],
      },
      colors: {
        primary: '#d7d7da',
        p_contrast: '#c6c6c9',
        accent: '#c2185b',
        warn: '#d5404e',
        detail: '#3b362f'
      },
    },
  },
  plugins: [],
}

