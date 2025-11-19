<template>
    <div class="w-full max-w-4xl mx-auto mt-16 bg-white shadow-lg rounded-2xl p-10">
    <h1 class="text-3xl font-bold mb-8 text-center">
      Escribir una reseña
    </h1>

    <form @submit.prevent="handleSubmit" class="space-y-6 ">
      <!-- Rating con estrellas -->
      <div class="text-center">
        <label class="block mb-3 font-semibold text-lg">Puntuación</label>
        <div class="flex justify-center space-x-2">
          <span
            v-for="n in 5"
            :key="n"
            @click="setRating(n)"
            @mouseover="hoverRating = n"
            @mouseleave="hoverRating = 0"
            class="cursor-pointer text-4xl transition-transform duration-150"
            :class="[
              n <= (hoverRating || review.rating)
                ? 'text-yellow-400 scale-110'
                : 'text-gray-300',
            ]"
          >
            ★
          </span>
        </div>
      </div>

      <!-- Texto de reseña -->
      <div>
        <label class="block mb-2 font-semibold text-lg">Tu reseña</label>
        <textarea
          v-model="review.text"
          class="border rounded-lg w-full p-3 text-gray-800 focus:outline-none focus:ring-2 focus:ring-blue-400"
          rows="6"
          placeholder="Contanos tu experiencia..."
          required
          minlength="20"
          maxlength="1000"
        ></textarea>
      </div>

      <!-- Mensajes -->
      <div v-if="error" class="text-red-500 text-center font-medium">
        {{ error }}
      </div>
      <div v-if="success" class="text-green-600 text-center font-medium">
        {{ success }}
      </div>

      <!-- Botones -->
      <div class="flex justify-between mt-8">
        <button
          type="button"
          @click="goBack"
          class="text-gray-600 hover:text-gray-900 transition-colors text-lg"
        >
          ← Volver
        </button>

        <ButtonPrimary :text=" 'Publicar'  "  class="max-w-36 w-auto" type="submit"> </ButtonPrimary>

      </div>
    </form>
  </div>
</template>

<script setup>
import ButtonPrimary from '@/components/buttons/ButtonPrimary.vue'
import { ref, onBeforeUnmount } from "vue";
import { useRoute, useRouter } from "vue-router";

import api from "@/api/axios.js";


const route = useRoute();
const router = useRouter();
const siteId = Number(route.params.site_id);

const review = ref({
  rating: "",
  text: "",
});

const error = ref("");
const success = ref("");
const hoverRating = ref(0);


const setRating = (n) => {
  review.value.rating = n;
};

let redirectTimeoutId = null;

const clearRedirectTimeout = () => {
  if (redirectTimeoutId) {
    clearTimeout(redirectTimeoutId);
    redirectTimeoutId = null;
  }
};

const handleSubmit = async () => {
  error.value = "";
  success.value = "";
  if (!review.value.rating || review.value.rating < 1 || review.value.rating > 5) {
    error.value = "Seleccioná una puntuación válida (1 a 5 estrellas).";
    return;
  }

  if (review.value.text.length < 20 || review.value.text.length > 1000) {
    error.value = "El texto debe tener entre 20 y 1000 caracteres.";
    return;
  }

try {
  const payload = {
    rating: review.value.rating,
    comment: review.value.text,
  };

  await api.post(`/sites/${siteId}/reviews`, payload);

  success.value = "Tu reseña fue enviada correctamente.";
  redirectTimeoutId = setTimeout(() => {
    redirectTimeoutId = null;
    router.push(`/sites/${siteId}`);
  }, 2500);

} catch (e) {
  console.error("Error creando reseña:", e);

  if (e.response?.data?.error) {
    const backendError = e.response.data.error;
    const details = backendError.details
      ? Object.values(backendError.details).flat().join(", ")
      : backendError.message;

    error.value = details || "Error al guardar la reseña.";
  } else {
    error.value = "Error de conexión con el servidor.";
  }
}



};


const goBack = () => {
  clearRedirectTimeout();
  router.push(`/sites/${siteId}`);
};

onBeforeUnmount(() => {
  clearRedirectTimeout();
});
</script>

<style scoped>
/* Transición suave para las estrellas */
span {
  transition: color 0.2s, transform 0.15s ease-in-out;
}
</style>
