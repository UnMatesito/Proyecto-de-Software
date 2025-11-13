<template>
  <div v-if="authStore.authError" class="auth-error-banner">
    <span>{{ authStore.authError }}</span>
    <button @click="authStore.clearAuthError()">×</button>
  </div>
  <div class="min-h-screen shadow-md">
    <!-- Header/Navbar -->
    <header class="bg-white shadow-sm sticky top-0 w-full z-50" style="z-index: 1200;">
      <nav class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-2">
        <div>
          <div class="flex justify-between h-16 items-center">
            <!-- Logo + Título -->
            <div class="flex items-center">
              <div class="h-14 w-14 sm:mr-2">
                <img src="../src/assets/images/logo.svg" alt="logo histori.ar" class="h-full w-full">
              </div>
              <h1 class="text-xl lg:text-2xl font-bold text-proyecto-primary hidden sm:block">Portal Público</h1>
            </div>

            <!-- Botón hamburguesa (visible solo en móvil) -->
            <button data-collapse-toggle="navbar-hamburger" type="button"
              class="inline-flex items-center justify-center p-2 w-10 h-10 text-sm text-gray-600 rounded-lg hover:bg-gray-100
              focus:outline-none focus:ring-2 focus:ring-gray-200 lg:hidden transition-colors duration-300"
              @click="open = !open"
              aria-controls="navbar-hamburger"
              :aria-expanded="open.toString()" >
              <span class="sr-only">Abrir menú principal</span>
              <i class="fa-solid fa-bars text-proyecto-primary text-lg"></i>
            </button>

            <!-- Menú de escritorio -->
            <div class="lg:flex space-x-4 hidden">
              <RouterLink
                to="/"
                exact-active-class="bg-proyecto-accent/80 text-white"
                class="px-3 py-2 rounded-md text-xs sm:text-sm font-medium hover:bg-proyecto-secondary hover:text-proyecto-text transition"
              >
                Inicio
              </RouterLink>
              <RouterLink
                to="/about"
                exact-active-class="bg-proyecto-accent/80 text-white"
                class="px-3 py-2 rounded-md text-xs sm:text-sm font-medium hover:bg-proyecto-secondary transition"
              >
                Acerca de
              </RouterLink>
              <RouterLink
                to="/sites"
                exact-active-class="bg-proyecto-accent/80 text-white"
                class="px-3 py-2 rounded-md text-xs sm:text-sm font-medium hover:bg-proyecto-secondary transition"
              >
                Sitios históricos
              </RouterLink>
            </div>

            <!-- Botón de login (solo escritorio) -->
            <div v-if="!authStore.isAuthenticated" class="hidden lg:flex">
              <button
                @click="loginWithGoogle"
                class="flex items-center bg-white border border-gray-400 rounded-lg px-3 py-2 hover:shadow transition hover:bg-gray-100"
              >
                <img
                  src="https://www.svgrepo.com/show/355037/google.svg"
                  alt="Google"
                  class="w-5 h-5 mr-2"
                />
                <span class="text-gray-600 text-sm font-medium">Continuar con Google</span>
              </button>
            </div>

            <!-- Info de Usuario Logueado (Escritorio) -->
            <RouterLink
              v-else
              to="/profile"
              class="hidden lg:flex items-center gap-2 cursor-pointer group"
            >
              <div class="flex items-center gap-2 group-hover:opacity-80 transition-opacity duration-200">
                <img
                  :src="authStore.user?.avatar"
                  class="w-8 h-8 rounded-full"
                  alt="avatar"
                  referrerpolicy="no-referrer"
                />
                <span class="text-gray-700 font-medium">{{ authStore.user?.name }}</span>
              </div>
              <button
                @click.prevent="authStore.logout"
                class="text-sm text-white font-medium bg-proyecto-primary hover:bg-proyecto-primary/80 rounded-md px-3 py-2 transition-colors duration-200 ml-2 z-10 relative"
              >
                Cerrar sesión
              </button>
            </RouterLink>

          </div>
        </div>

        <!-- Menú hamburguesa abierto (solo móvil) -->
        <Transition
          enter-active-class="transition-all ease-out duration-300"
          enter-from-class="opacity-0 -translate-y-2"
          enter-to-class="opacity-100 translate-y-0"
          leave-active-class="transition-all ease-in duration-200"
          leave-from-class="opacity-100 translate-y-0"
          leave-to-class="opacity-0 -translate-y-2"
        >
          <div
            v-show="open"
            class="absolute left-0 right-0 top-full w-full bg-white border-t border-gray-200 shadow-lg lg:hidden z-20"
            id="navbar-hamburger">
            <div class="px-4 py-3">
              <ul class="flex flex-col font-medium rounded-lg gap-y-1">
              <RouterLink to="/" v-slot="{ isExactActive }">
                <li
                  @click="open = false"
                  :class="[
                    'flex flex-row justify-center items-center rounded-lg transition-colors px-3 py-2',
                    isExactActive ? 'bg-proyecto-accent/80 text-white' : 'hover:bg-proyecto-secondary text-gray-900'
                  ]"
                >
                  Inicio
                  <i :class="['fa-solid fa-home  text-lg ml-2', isExactActive ? 'fa-bounce' : '']"></i>
                </li>
              </RouterLink>
              <RouterLink to="/about" v-slot="{ isExactActive }">
                <li
                  @click="open = false"
                  :class="[
                    'flex flex-row justify-center items-center rounded-lg transition-colors px-3 py-2',
                    isExactActive ? 'bg-proyecto-accent/80 text-white' : 'hover:bg-proyecto-secondary text-gray-900'
                  ]"
                >
                  Acerca de
                  <i :class="['fa-solid fa-circle-info text-lg ml-2', isExactActive ? 'fa-bounce' : '']"></i>
                </li>
              </RouterLink>
              <RouterLink to="/sites" v-slot="{ isExactActive }">
                <li
                  @click="open = false"
                  :class="[
                    'flex flex-row justify-center items-center rounded-lg transition-colors px-3 py-2',
                    isExactActive ? 'bg-proyecto-accent/80 text-white' : 'hover:bg-proyecto-secondary text-gray-900'
                  ]"
                >
                  Sitios históricos
                  <i :class="['fa-solid fa-landmark text-lg ml-2', isExactActive ? 'fa-bounce' : '']"></i>
                </li>
              </RouterLink>
            </ul>

            <!-- Botón Login Móvil -->
            <div v-if="!authStore.isAuthenticated">
              <button
                @click="loginWithGoogle"
                class="flex items-center bg-white border border-gray-300 rounded-lg px-3 py-2 w-full justify-center mt-3 hover:shadow transition"
              >
                <img
                  src="https://www.svgrepo.com/show/355037/google.svg"
                  alt="Google"
                  class="w-5 h-5 mr-2"
                />
                <span class="text-gray-600 text-sm font-medium">Continuar con Google</span>
              </button>
            </div>

            <!-- Info Usuario Móvil -->
              <div v-else class="flex flex-col items-center gap-2 mt-3">
                <RouterLink to="/profile" @click="open = false" class="flex flex-col items-center gap-2 group cursor-pointer w-full max-w-xs">
                   <div class="flex flex-col items-center gap-2 group-hover:opacity-80 transition-opacity duration-200">
                     <img
                       :src="authStore.user?.avatar"
                       class="w-10 h-10 rounded-full"
                       alt="avatar"
                       referrerpolicy="no-referrer"
                      />
                     <span class="text-gray-700 font-medium">{{ authStore.user?.name }}</span>
                   </div>
                </RouterLink>
                <button
                  @click="()=>{ authStore.logout(); open = false; }"
                  class="text-sm text-white font-medium bg-proyecto-primary hover:bg-proyecto-primary/80 rounded-md px-4 py-2 mt-2 transition-colors duration-200 w-full max-w-xs"
                >
                  Cerrar sesión
                </button>
              </div>
            </div>
          </div>
        </Transition>
      </nav>
    </header>


    <!-- Contenido principal -->
    <main class="flex flex-col items-center justify-center min-h-screen bg-proyecto-bg">
      <RouterView />
    </main>

    <!-- Footer opcional -->
    <footer class="bg-white border-t mt-auto">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
        <p class="text-center text-proyecto-primary text-sm">
          Proyecto de Software © {{ new Date().getFullYear() }}
        </p>
      </div>
    </footer>
  </div>
</template>

<script setup>
import { RouterLink, RouterView } from 'vue-router'
// import ButtonPrimary from "@/components/buttons/ButtonPrimary.vue"; // Comentado si no se usa
import { ref, onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { useRouter } from 'vue-router'

const open = ref(false)
const authStore = useAuthStore()
const router = useRouter()

onMounted(async () => {
  await router.isReady();
  authStore.checkAuthStatus();
});

function loginWithGoogle() {
  const currentPath = router.currentRoute.value.fullPath
  const apiUrl = import.meta.env.VITE_API_URL || 'https://admin-grupo09.proyecto2025.linti.unlp.edu.ar/api';
  window.location.href = `${apiUrl}/auth/google/login?next=${encodeURIComponent(currentPath)}`;
}
</script>

<style scoped>
.auth-error-banner {
  background-color: #f8d7da;
  color: #721c24;
  padding: 0.5rem 1rem;
  text-align: center;
  font-weight: 500;
  font-size: 0.9rem;
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 0.5rem;
  border-bottom: 1px solid #f5c6cb;
  position: sticky;
  top: 0;
  z-index: 100;
}

.auth-error-banner button {
  background: none;
  border: none;
  font-size: 1.25rem;
  font-weight: bold;
  color: #721c24;
  cursor: pointer;
  padding: 0 0.5rem;
}
</style>
