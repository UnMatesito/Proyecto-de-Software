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
  <div class="mb-12">
    <div class="flex flex-row justify-between items-center mb-4">
        <h2 class="text-4xl text-proyecto-primary font-semibold">{{ title }}</h2>
        <a href="#" class="font-semibold hover:bg-proyecto-primary hover:text-white rounded-full px-4 py-2 transition-colors duration-400">Ver Todos <i class="fa-solid fa-chevron-right ml-1"></i></a>
    </div>
    <ul class="grid grid-cols-4 gap-4 mt-4 justify-items-center">
      <li v-for="site in [1,2,3,4] " :key="site">
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
  </div>
</template>
