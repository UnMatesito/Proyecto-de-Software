import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import api from '../api/axios.js';
import router from '@/router';


const authErrorMessages = {
  cancelled: "El inicio de sesión fue cancelado.",
  user_blocked: "No se pudo iniciar sesión. Esta cuenta se encuentra bloqueada.",
  unknown_failure: "Ocurrió un error inesperado durante el inicio de sesión."
};

export const useAuthStore = defineStore('auth', () => {
  const user = ref(JSON.parse(localStorage.getItem('user_data') || 'null'));
  const authError = ref(null);
  const isAuthenticated = computed(() => !!user.value);

  function saveUser(userData) {
    user.value = userData;
    localStorage.setItem('user_data', JSON.stringify(userData));
  }

  async function logout(){
    try {
      await api.post('/auth/google/logout');
    } catch (error) {
      console.error("authStore: Error llamando al endpoint de logout", error);
    } finally {
      logoutLocal();
    }
  }

  function logoutLocal() {
    user.value = null;
    localStorage.removeItem('user_data');
    router.push('/').then(() => {
      window.location.reload(); // Recargar después de navegar
    });
  }

  async function fetchUser() {
    try {
        const response = await api.get('/me');
        console.log("Usuario recibido:", response.data);
        saveUser(response.data);
    } catch (error) {
        console.error("authStore: fetchUser() error (normal si no hay sesión):", error);
        
        user.value = null;
        localStorage.removeItem('user_data');
    }
  }

  function checkLoginErrors() {
    const route = router.currentRoute.value;
    const errorCode = route.query.error_code;
    
    if (errorCode && authErrorMessages[errorCode]) {
      authError.value = authErrorMessages[errorCode];
    }
  }

  function clearAuthError() {
    authError.value = null;
    
    const route = router.currentRoute.value;
    const newQuery = { ...route.query };
    delete newQuery.error_code;
    router.replace({ query: newQuery });
  }

  async function checkAuthStatus() {
      checkLoginErrors();

      if (authError.value) {
        return; 
      }
      
      await fetchUser();
  }

  return {
    isAuthenticated,
    logout,
    checkAuthStatus,
    fetchUser,
    user,
    authError,
    clearAuthError
  };
});
