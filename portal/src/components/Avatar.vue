<template>
    
<div class="flex items-center gap-2">
    <IconAvatar class="fill-proyecto-primary w-9"></IconAvatar>
    <div class="font-medium dark:text-white">
        <div>{{ name }}</div>
        <div class="text-sm text-gray-500 dark:text-gray-400 ">{{ email }}</div>
    </div>
</div>

</template>

<script setup>
    import IconAvatar from './icons/IconAvatar.vue';
    defineProps(["name", "email"])
</script>