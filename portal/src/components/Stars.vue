<template>
    <div class="flex items-center" :class="classContent">
        <IconStar 
            v-for="index in stars" 
            :key="index"
            class="w-4 h-4 sm:w-7 sm:h-7"
            :class="index <= Math.round(rating) ? 'fill-yellow-300' : 'fill-slate-300'"
        ></IconStar>
    </div>
</template>

<script setup>
    import IconStar from './icons/IconStar.vue';
    
    const props = defineProps({
        rating: {
            type: Number,
            default: 0
        },
        classContent: {
            type: String,
            default: ''
        }
    })
    
    const stars = 5
</script>