<template>
  <div class="callback-container">
    <p>Verificando tu inicio de sesión...</p>
    </div>
</template>

<script setup>
import { onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { useAuthStore } from '@/stores/auth';

const router = useRouter();
const authStore = useAuthStore();

onMounted(async () => {
  try {
    await authStore.fetchUser();
    if (authStore.isAuthenticated){
      console.log("Callback exitoso, usuario autenticado:", authStore.user);
      const redirectPath = localStorage.getItem('authRedirect') || '/';
      localStorage.removeItem('authRedirect'); 
      router.push(redirectPath);
    }
    else {
      throw new Error('La autenticación falló después de obtener el usuario.');
    }

  } catch (error) {
    console.error("Callback: Error al verificar la autenticación:", error);
    router.push('/login?error=auth_failed');
  }
});
</script>

<style scoped>
.callback-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 80vh;
  font-size: 1.2rem;
  color: #555;
}
</style>