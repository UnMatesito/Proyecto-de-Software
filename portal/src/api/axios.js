import axios from 'axios'

const api = axios.create({
  // TODO: Cambiar a la URL del backend cuando esté desplegado
  baseURL: import.meta.env.VITE_API_URL || 'https://admin-grupo09.proyecto2025.linti.unlp.edu.ar'
})

export default api
