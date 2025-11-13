import axios from 'axios';

// Helper para leer cookies
function getCookie(name) {
  const value = `; ${document.cookie}`;
  const parts = value.split(`; ${name}=`);
  if (parts.length === 2) return parts.pop().split(";").shift();
}

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'https://admin-grupo09.proyecto2025.linti.unlp.edu.ar/api',
  withCredentials: true,
});


api.interceptors.request.use(config => {
    const csrfToken = getCookie("csrf_access_token");
    
    if (csrfToken && ['post', 'put', 'delete', 'patch'].includes(config.method.toLowerCase())) {
        config.headers['X-CSRF-TOKEN'] = csrfToken;
    }
    return config;

}, (error) => {
    return Promise.reject(error);
});


export default api;
