# Etapa base
FROM node:22-alpine

# Directorio de trabajo dentro del contenedor
WORKDIR /portal

# Copiar los archivos de configuración necesarios para instalar dependencias
COPY package*.json ./

# Instalar dependencias (solo si el volumen está vacío)
RUN npm install

# Exponer el puerto de Vite
EXPOSE 5173

# Comando por defecto: iniciar Vite en modo desarrollo
CMD ["npm", "run", "dev"]
