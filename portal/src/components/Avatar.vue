<template>
    
<div class="flex items-center gap-4">
    <i class="fa-solid fa-circle-user-[proyecto-primary]"></i>
    <div class="font-medium dark:text-white">
        <div>{{ name }}</div>
        <div class="text-sm text-gray-500 dark:text-gray-400 ">{{ email }}</div>
    </div>
</div>

</template>

<script setup>
    defineProps(["name", "email"])
</script>