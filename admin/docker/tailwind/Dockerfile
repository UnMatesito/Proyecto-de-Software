FROM node:18-alpine

WORKDIR /admin/tailwind

# Copiamos package.json y configuraciones
COPY docker/tailwind/package.json ./
COPY docker/tailwind/tailwind.config.js ./
COPY docker/tailwind/input.css ./
COPY docker/tailwind/postcss.config.js ./

RUN npm install

# Comando para correr Tailwind en modo watch
CMD ["npx", "tailwindcss", "-i", "./input.css", "-o", "/admin/static/css/styles.css", "--watch", "--poll"]
