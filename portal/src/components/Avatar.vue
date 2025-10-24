<template>
    
<div class="flex items-center gap-4">
    <img class="w-10 h-10 rounded-full" src="https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcTSYbP-248zDkKcJG_swsx0pK2Hhe8hwE0fHQ&s" alt="">
    <div class="font-medium dark:text-white">
        <div>{{ name }}</div>
        <div class="text-sm text-gray-500 dark:text-gray-400 ">{{ email }}</div>
    </div>
</div>

</template>

<script setup>
    defineProps(["name", "email"])
</script>