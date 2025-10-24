<template>
    <div class="flex flex-col gap-2">
        <div class="flex justify-between">
            <Avatar :name="name" :email="email"></Avatar>
            <div class="flex items-center gap-3 flex-col">
                <span class="text-sm  gap-3 text-gray-500 dark:text-gray-400">
                    Subido {{ created_at.slice(0, props.created_at.indexOf("T")).replaceAll("-", "/") }}
                </span>
                <Stars :rating="rating"></Stars>
            </div>
        </div>
        <p class="text-gray-700 w-min:full ">
            {{ text }}
        </p>
    </div>
</template>


<script setup>
    import Stars from './Stars.vue';
    import Avatar from './Avatar.vue';
    import { ref } from 'vue'
    const props = defineProps(["name", "text", "email", "reting", "created_at"])
    const createdDate = ref("")
    console.log(props.created_at)
    createdDate.value = props.created_at.slice(0, props.created_at.indexOf(":"))
</script>er