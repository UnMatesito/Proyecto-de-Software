/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
      "/admin/src/**/*.{html,js}",
      "/admin/static/js/**/*.js"
    ],
  theme: {
    extend: {
      colors: {
          'proyecto-text': '#2b2b2b',
          'proyecto-bg': 'fbf4f4',
          'proyecto-primary': '#1a4d70',
          'proyecto-secondary': '#e9dcc9',
          'proyecto-accent': '#c46d45'
      }
    }
  },
  plugins: [
    require('flowbite/plugin'),
    require('@tailwindcss/forms'),
    require('@tailwindcss/typography')
  ]
}
