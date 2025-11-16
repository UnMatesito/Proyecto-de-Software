<template>
  <div class="flex items-center gap-2">
    <!-- Si hay avatar, mostrar imagen -->
    <img
      :src="avatar"
      :alt="name"
      class="w-9 h-9 rounded-full object-cover"
    />


    <div class="font-medium dark:text-white">
      <div>{{ name }}</div>
      <div class="text-xs sm:text-sm text-gray-500 dark:text-gray-400">{{ email }}</div>
    </div>
  </div>
</template>

<script setup>
defineProps({
  name: String,
  email: String,
  avatar: {
    type: String,
    default: null
  }
})
</script>
