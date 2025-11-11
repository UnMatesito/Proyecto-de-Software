<template>
    <div class="flex flex-col gap-2 border-b-2 border-b-gray-300 pb-2" id="reviews">
        <div class="flex justify-between flex-wrap">
            <Avatar :name="name" :email="email"></Avatar>
            <div class="flex gap-3 flex-col">
                <Stars :rating="rating" :class="'w-28 flex justify-start'"></Stars>
                <span class="text-sm  gap-3 text-gray-500 dark:text-gray-400">
                     {{ created_at ? created_at.slice(0, props.created_at.indexOf("T")).replaceAll("-", "/")  : '...'}}
                </span>
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
    const props = defineProps(["name", "text", "email", "rating", "created_at"])
    const createdDate = ref("")
    console.log(props.created_at)
    console.log(props)
   /* createdDate.value = props.created_at.slice(0, props.created_at.indexOf(":")) */
</script>er