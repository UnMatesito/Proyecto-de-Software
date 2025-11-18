import axios from 'axios';

// Helper para leer cookies
function getCookie(name) {
  const value = `; ${document.cookie}`;
  const parts = value.split(`; ${name}=`);
  if (parts.length === 2) return parts.pop().split(";").shift();
}

function attachCsrfToken(config) {
  const method = config.method?.toLowerCase();

  if (!method || !['post', 'put', 'delete', 'patch'].includes(method)) {
    return config;
  }

  const isRefreshRequest = config.url?.includes('/auth/token/refresh');
  const csrfCookieName = isRefreshRequest
    ? 'csrf_refresh_token'
    : 'csrf_access_token';
  const csrfToken = getCookie(csrfCookieName);

  if (csrfToken) {
    config.headers['X-CSRF-TOKEN'] = csrfToken;
  }

  return config;
}

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'https://admin-grupo09.proyecto2025.linti.unlp.edu.ar/api',
  withCredentials: true,
});


api.interceptors.request.use(config => {
    return attachCsrfToken(config);

}, (error) => {
    return Promise.reject(error);
});


let refreshRequest = null;

api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const { response, config } = error;

    if (!response || !config) {
      return Promise.reject(error);
    }

    const isRefreshRequest = config.url?.includes('/auth/token/refresh');

    if (response.status === 401 && !config._retry && !isRefreshRequest) {
      config._retry = true;

      if (!refreshRequest) {
        refreshRequest = api
          .post('/auth/token/refresh')
          .finally(() => {
            refreshRequest = null;
          });
      }

      try {
        await refreshRequest;
        return api(config);
      } catch (refreshError) {
        return Promise.reject(refreshError);
      }
    }

    return Promise.reject(error);
  }
);

export default api;
