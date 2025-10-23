<template>
  <div class="bg-gray-50 min-h-screen flex flex-col items-center justify-center p-8">
    <h1 class="text-2xl font-bold text-blue-700 mb-6">🐱 Carrusel de Gatos con Flowbite</h1>

    <!-- Carrusel -->
    <div id="cat-carousel" class="relative w-full max-w-2xl" data-carousel="slide">
      <!-- Imágenes -->
      <div class="relative h-56 overflow-hidden rounded-lg md:h-96">
        <!-- Imagen 1 -->
        <div class="hidden duration-700 ease-in-out" data-carousel-item="active">
          <img
            src="https://placecats.com/800/400"
            class="absolute block w-full h-full object-cover"
            alt="Gato 1"
          />
        </div>
        <!-- Imagen 2 -->
        <div class="hidden duration-700 ease-in-out" data-carousel-item>
          <img
            src="https://placecats.com/801/400"
            class="absolute block w-full h-full object-cover"
            alt="Gato 2"
          />
        </div>
        <!-- Imagen 3 -->
        <div class="hidden duration-700 ease-in-out" data-carousel-item>
          <img
            src="https://placecats.com/802/400"
            class="absolute block w-full h-full object-cover"
            alt="Gato 3"
          />
        </div>
        <!-- Imagen 4 -->
        <div class="hidden duration-700 ease-in-out" data-carousel-item>
          <img
            src="https://placecats.com/803/400"
            class="absolute block w-full h-full object-cover"
            alt="Gato 4"
          />
        </div>
        <!-- Imagen 5 -->
        <div class="hidden duration-700 ease-in-out" data-carousel-item>
          <img
            src="https://placecats.com/804/400"
            class="absolute block w-full h-full object-cover"
            alt="Gato 5"
          />
        </div>
      </div>

      <!-- Indicadores -->
      <div class="absolute z-30 flex space-x-3 -translate-x-1/2 bottom-5 left-1/2">
        <button type="button" class="w-3 h-3 rounded-full" aria-current="true" aria-label="Slide 1" data-carousel-slide-to="0"></button>
        <button type="button" class="w-3 h-3 rounded-full" aria-label="Slide 2" data-carousel-slide-to="1"></button>
        <button type="button" class="w-3 h-3 rounded-full" aria-label="Slide 3" data-carousel-slide-to="2"></button>
        <button type="button" class="w-3 h-3 rounded-full" aria-label="Slide 4" data-carousel-slide-to="3"></button>
        <button type="button" class="w-3 h-3 rounded-full" aria-label="Slide 5" data-carousel-slide-to="4"></button>
      </div>

      <!-- Controles -->
      <button
        type="button"
        class="absolute top-0 start-0 z-30 flex items-center justify-center h-full px-4 cursor-pointer group focus:outline-none"
        data-carousel-prev
      >
        <span
          class="inline-flex items-center justify-center w-10 h-10 rounded-full bg-white/30 group-hover:bg-white/50 focus:ring-4 focus:ring-white"
        >
          <svg
            class="w-4 h-4 text-white"
            aria-hidden="true"
            xmlns="http://www.w3.org/2000/svg"
            fill="none"
            viewBox="0 0 6 10"
          >
            <path stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 1 1 5l4 4" />
          </svg>
          <span class="sr-only">Anterior</span>
        </span>
      </button>

      <button
        type="button"
        class="absolute top-0 end-0 z-30 flex items-center justify-center h-full px-4 cursor-pointer group focus:outline-none"
        data-carousel-next
      >
        <span
          class="inline-flex items-center justify-center w-10 h-10 rounded-full bg-white/30 group-hover:bg-white/50 focus:ring-4 focus:ring-white"
        >
          <svg
            class="w-4 h-4 text-white"
            aria-hidden="true"
            xmlns="http://www.w3.org/2000/svg"
            fill="none"
            viewBox="0 0 6 10"
          >
            <path stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="m1 9 4-4-4-4" />
          </svg>
          <span class="sr-only">Siguiente</span>
        </span>
      </button>
    </div>

    <!-- Alternativa (comentada): loremflickr -->
    <!--
      <img src="https://loremflickr.com/800/400/cat" alt="Gato alternativo" />
    -->
  </div>
</template>

<script setup>
// No se necesita lógica JS, Flowbite maneja el carrusel automáticamente
</script>
