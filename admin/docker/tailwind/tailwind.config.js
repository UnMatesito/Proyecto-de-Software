/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
      "/admin/src/**/*.{html,js}",
      "/admin/static/js/**/*.js"
    ],
  theme: {
    extend: {
      colors: {
        'proyecto-primary': '#1e40af',
        'proyecto-secondary': '#64748b',
      }
    }
  },
  plugins: [
    require('flowbite/plugin'),
    require('@tailwindcss/forms'),
    require('@tailwindcss/typography')
  ]
}
