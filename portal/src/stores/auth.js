import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import api from '../api/axios.js';
import router from '@/router';

export const useAuthStore = defineStore('auth', () => {
  const user = ref(JSON.parse(localStorage.getItem('user_data') || 'null'));
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
    router.push('/')
  }

  async function fetchUser() {

    try {
        const response = await api.get('/me');

        console.log("Usuario recibido:", response.data);

        saveUser(response.data);

    } catch (error) {
        console.error("authStore: fetchUser() error:", error);
        logoutLocal();
    }
  }

  async function checkAuthStatus() {
      const storedUser = localStorage.getItem('user_data');
      if (storedUser) {
        try {
          user.value = JSON.parse(storedUser);
          await fetchUser();
        }
        catch (e) {
          console.error("authStore: Datos de usuario corruptos, limpiando.", e);
          logoutLocal();
      }
    } else {
        console.log("No user data in localStorage.");
      }
  }

  return {isAuthenticated, logout, checkAuthStatus, fetchUser, user };
});
