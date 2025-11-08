<template>
  <div class="max-w-lg mx-auto mt-10 bg-white shadow-md rounded-lg p-6">
    <h1 class="text-2xl font-bold mb-6 text-center">
      {{ existingReview ? "Editar tu reseña" : "Escribir una reseña" }}
    </h1>

    <form @submit.prevent="handleSubmit">
      <div class="mb-4">
        <label class="block mb-2 font-semibold">Puntuación (1–5)</label>
        <select v-model="review.rating" class="border rounded w-full p-2">
          <option disabled value="">Selecciona una puntuación</option>
          <option v-for="n in 5" :key="n" :value="n">{{ n }}</option>
        </select>
      </div>

      <div class="mb-4">
        <label class="block mb-2 font-semibold">Tu reseña</label>
        <textarea
          v-model="review.text"
          class="border rounded w-full p-2"
          rows="5"
          placeholder="Contanos tu experiencia..."
        ></textarea>
      </div>

      <div v-if="error" class="text-red-500 mb-4">{{ error }}</div>
      <div v-if="success" class="text-green-600 mb-4">{{ success }}</div>

      <div class="flex justify-between items-center">
        <button
          type="button"
          @click="goBack"
          class="text-gray-600 hover:underline"
        >
          ← Volver al sitio
        </button>

        <button
          type="submit"
          class="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700"
        >
          {{ existingReview ? "Guardar cambios" : "Publicar reseña" }}
        </button>
      </div>
    </form>
  </div>
</template>

<script setup>
import { ref, onMounted } from "vue";
import { useRoute, useRouter } from "vue-router";
import { createOrUpdateReview, getReviewsBySite } from "@/api/reviews.js";

const route = useRoute();
const router = useRouter();

// el id del sitio viene por parámetro en la ruta
const siteId = Number(route.params.siteId);

const review = ref({
  rating: "",
  text: "",
});

const existingReview = ref(null);
const error = ref("");
const success = ref("");

// al montar, buscamos si el usuario ya tiene reseña previa
onMounted(async () => {
  try {
    const res = await getReviewsBySite(siteId);
    // simulamos que la API marca la reseña del usuario con isUserReview = true
    existingReview.value = res.data.find((r) => r.isUserReview) || null;

    if (existingReview.value) {
      review.value.rating = existingReview.value.rating;
      review.value.text = existingReview.value.text;
    }
  } catch (e) {
    console.error("Error cargando reseña:", e);
  }
});

const handleSubmit = async () => {
  error.value = "";
  success.value = "";

  if (!review.value.rating || review.value.rating < 1 || review.value.rating > 5) {
    error.value = "La puntuación debe estar entre 1 y 5.";
    return;
  }

  if (review.value.text.length < 20 || review.value.text.length > 1000) {
    error.value = "El texto debe tener entre 20 y 1000 caracteres.";
    return;
  }

  try {
    await createOrUpdateReview(siteId, review.value);
    success.value = "Tu reseña fue enviada correctamente.";
    setTimeout(() => router.push(`/sitios/${siteId}`), 1500); // vuelve al detalle del sitio
  } catch (e) {
    error.value = "Error al guardar la reseña. Intentá más tarde.";
  }
};

const goBack = () => {
  router.push(`/sitios/${siteId}`);
};
</script>
