<script setup>
const props = defineProps({
  link: { type: String, default: null },
  icon_left: { type: String, default: '' },
  icon_right: { type: String, default: '' },
  text: { type: String, default: '' },
  type: { type: String, default: 'button' }
})
</script>

<template>
  <a v-if="props.link" :href="props.link" class="flex-0 inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-proyecto-primary hover:bg-proyecto-accent focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-proyecto-accent transition">
    <i v-if="props.icon_left" :class="props.icon_left"></i>
    <div v-if="props.text">{{ props.text }}</div>
    <i v-if="props.icon_right" :class="props.icon_right"></i>
  </a>

  <button v-else :type="type" class="flex-0 inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-proyecto-primary hover:bg-proyecto-accent focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-proyecto-accent transition">
    <i v-if="props.icon_left" :class="props.icon_left"></i>
    <div v-if="props.text">{{ props.text }}</div>
    <i v-if="props.icon_right" :class="props.icon_right"></i>
  </button>
</template>


