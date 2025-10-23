<template>
  <fwb-carousel no-indicators :pictures="pictures" />
</template>

<script setup>
import { FwbCarousel } from 'flowbite-vue'

const pictures = [
  {src: '/images/img-1.svg', alt: 'Image 1'},
  {src: '/images/img-2.svg', alt: 'Image 2'},
  {src: '/images/img-3.svg', alt: 'Image 3'},
]
</script>