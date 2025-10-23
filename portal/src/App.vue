<template>
  <div class="min-h-screen shadow-md">
    <!-- Header/Navbar -->
    <header class="bg-white shadow-sm sticky top-0 w-full z-10">
      <nav class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div>
          <div class="flex justify-between h-16 items-center">
            <div class="flex items-center">
              <h1 class="text-2xl font-bold text-proyecto-primary">
                Portal Público
              </h1>
            </div>
            <div class="flex space-x-4">
              <RouterLink
                to="/"
                class="px-3 py-2 rounded-md text-sm font-medium hover:bg-proyecto-secondary transition"
              >
                Inicio
              </RouterLink>
              <RouterLink
                to="/about"
                class="px-3 py-2 rounded-md text-sm font-medium hover:bg-proyecto-secondary transition"
              >
                Acerca de
              </RouterLink>
              <RouterLink
                to="/sites"
                class="px-3 py-2 rounded-md text-sm font-medium hover:bg-proyecto-secondary transition"
              >
                Sitios históricos
              </RouterLink>
            </div>
            <ButtonPrimary icon_left='fa-regular fa-user mr-2' text='Iniciar Sesión' />
          </div>
        </div>
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
import ButtonPrimary from "@/components/buttons/ButtonPrimary.vue";
</script>
