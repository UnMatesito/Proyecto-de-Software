<template>
    
<div class="flex items-center gap-4">
    <img class="w-10 h-10 rounded-full" src="https://e7.pngegg.com/pngimages/84/165/png-clipart-united-states-avatar-organization-information-user-avatar-service-computer-wallpaper-thumbnail.png" alt="avatar-picture">
    <div class="font-medium dark:text-white">
        <div>{{ name }}</div>
        <div class="text-sm text-gray-500 dark:text-gray-400 ">{{ email }}</div>
    </div>
</div>

</template>

<script setup>
    defineProps(["name", "email"])
</script>