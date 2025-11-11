<template>
    <div class="flex items-center" :class="classContent">
        <IconStar v-for="star in stars" :class="star <= rating ? 'fill-yellow-300' : 'fill-slate-300'"></IconStar>
    </div>
</template>

<script setup>
    import IconStar from './icons/IconStar.vue';
    const props = defineProps(["rating", "classContent"])
    const stars = 5
</script>
