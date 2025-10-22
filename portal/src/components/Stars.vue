<template>
    <div class="flex items-center w-32">
        <IconStar v-for="star in stars" :class="star <= rating ? 'fill-yellow-500' : 'fill-slate-500'"></IconStar>
    </div>
</template>

<script setup>
    import IconStar from './icons/IconStar.vue';
    const props = defineProps(["rating"])
    const stars = 5
    
</script>