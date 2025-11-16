<template>
  <div
    class="flex flex-col gap-2 pb-2 mx-4 rounded-md border-b-2 transition p-3"
    :class="is_own_review ? 'bg-proyecto-accent/5 border-proyecto-accent' : 'border-gray-300'"
    id="reviews"
  >
    <div class="flex justify-between flex-wrap gap-2">

      <div class="flex items-center gap-2">
        <Avatar :name="user_name" :email="user_email" :avatar="user_avatar" />
      </div>

      <!-- Estrellas + fecha -->
      <div class="flex gap-1 sm:flex-col items-end">
        <Stars :rating="rating" class="w-28 flex justify-start" />
        <span class="text-sm text-proyecto-accent dark:text-gray-400 flex items-center">
          <i class="fa-regular fa-clock"></i>
          {{ created_at ? new Date(created_at).toLocaleDateString('es-AR') : '...' }}
        </span>
      </div>
    </div>

    <p class="text-gray-700 w-min:full break-words">
      {{ text }}
    </p>
  </div>
</template>

<script setup>
import Stars from './Stars.vue'
import Avatar from './Avatar.vue'
import IconAvatar from './icons/IconAvatar.vue'

defineProps([
  "user_name",
  "text",
  "user_email",
  "rating",
  "created_at",
  "user_avatar",
  "is_own_review"
])
</script>
