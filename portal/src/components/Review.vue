<template>
    <div class="flex flex-col gap-2 border-b-2 border-b-gray-300 pb-2 mx-4" id="reviews">
        <div class="flex justify-between flex-wrap">
            <Avatar :name="user_name" :email="user_email"></Avatar>
            <div class="flex gap-3 flex-col items-end">
                <Stars :rating="rating" :class="'w-28 flex justify-start'"></Stars>
                <span class="text-sm  gap-1 text-proyecto-accent dark:text-gray-400 flex items-center ">
                    <i class="fa-regular fa-clock"></i> {{ created_at ? new Date(created_at).toLocaleDateString('es-AR') : '...' }}
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
    const props = defineProps(["user_name", "text", "user_email", "rating", "created_at"])
    const createdDate = ref("")
   /* createdDate.value = props.created_at.slice(0, props.created_at.indexOf(":")) */
</script>
