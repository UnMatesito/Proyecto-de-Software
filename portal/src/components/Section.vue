<script setup>

import Card from "@/components/Card.vue";
const props = defineProps({
    title: {
      type: String,
      required: true
    }
  });
</script>

<template>
  <div class="mb-8">
    <div class="flex flex-row justify-between items-center mb-4">
        <h2 class="text-2xl sm:text-4xl text-proyecto-primary font-semibold">{{ title }}</h2>
        <a href="#" class="text-sm sm:text-md font-semibold hover:bg-proyecto-primary hover:text-white rounded-full px-2.5 sm:px-4 py-1 sm:py-2 transition-colors duration-400">Ver Todos <i class="fa-solid fa-chevron-right ml-1"></i></a>
    </div>
    <!-- Cambiar la condición v-if por la lógica correspondiente para mostrar los sitios -->
    <ul v-if="true" class="flex gap-3 sm:gap-4 overflow-x-auto scroll-smooth pb-4 scrollbar-hide lg:px-2">
      <li v-for="site in [1,2,3,4,5,6,7,8,9,10] " :key="site" class="flex-none w-40 sm:w-48 md:w-56 lg:w-64">
        <Card
          name="Obelisco"
          province="Buenos Aires"
          city="Ciudad Autónoma de Buenos Aires"
          :tags="['Monumento', 'Histórico', 'Turismo', 'Cultura', 'Arquitectura', 'Icono']"
          state_of_conservation="Excelente"
          inauguration_year="1936"
          category="Monumento"
          imagen="https://www.infobae.com/resizer/v2/https%3A%2F%2Fs3.amazonaws.com%2Farc-wordpress-client-uploads%2Finfobae-wp%2Fwp-content%2Fuploads%2F2019%2F02%2F13105727%2FMarcha-Movimientos-sociales-Obelisco-3.jpeg?auth=98ea526ca284a14796ed1e27f354b65dc880d7115c2a54ed2e28ebf23b40563f&smart=true&width=1200&height=675&quality=85"
        ></Card>
      </li>
    </ul>
    <div v-else class="h-[200px] flex justify-center items-center">
      <p class="px-5 py-2 text-white bg-proyecto-primary/80 text-center rounded-full inline-flex font-semibold shadow-md select-none"> No hay Contenido</p>
    </div>
  </div>
</template>
