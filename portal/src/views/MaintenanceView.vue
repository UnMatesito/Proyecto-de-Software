<template>
  <section class="flex flex-col items-center justify-center text-center py-20 space-y-8">
    <div class="max-w-2xl space-y-6">
      <h2 class="text-4xl font-bold text-proyecto-primary">
        Portal en mantenimiento
      </h2>
      <p class="text-lg text-gray-700 leading-relaxed whitespace-pre-line">
        {{ message }}
      </p>
      <p class="text-sm text-gray-500">
        Te invitamos a regresar en unos minutos. Estamos trabajando para volver lo antes posible.
      </p>
    </div>
    <RouterLink
      to="/"
      class="inline-flex items-center px-6 py-3 rounded-lg bg-proyecto-primary text-white font-semibold shadow-sm hover:bg-proyecto-accent transition"
    >
      Volver al inicio
    </RouterLink>
  </section>
</template>

<script setup>
import { computed } from 'vue'
import { RouterLink } from 'vue-router'
import { maintenanceState } from '@/utils/maintenanceState'
const DEFAULT_MESSAGE = 'El portal se encuentra temporalmente en mantenimiento.'
const message = computed(
  () => maintenanceState.message?.trim() || DEFAULT_MESSAGE,
)
</script>
