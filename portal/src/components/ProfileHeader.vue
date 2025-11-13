<template>
  <div class="flex items-center gap-4 mb-4">
    <img :src="user.avatar" alt="Foto de usuario" class="w-16 h-16 rounded-full" />
    <div>
      <h2 class="text-lg font-semibold">{{ user.name }}</h2>
      <p class="text-sm text-gray-500">{{ user.email }}</p>
    </div>
  </div>
</template>

<script setup>
defineProps({
  user: Object
})
</script>
