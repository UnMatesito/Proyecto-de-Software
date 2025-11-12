
<script setup>
import router from '@/router';
import IconArrowLeft from './icons/IconArrowLeft.vue';
    import IconArrowRight from './icons/IconArrowRight.vue';
    import { ref, watch} from 'vue'
    import { useRoute } from 'vue-router'
    const route = useRoute()
    const props = defineProps(["page", "per_page", "total", "pages" , "fetchSites"])
    const pageToShow = props.pages <= 4 ? props.pages : [1, 2, 3, 4, "...", props.pages]
    const query = ref({})
    const classContentHover =  [
                'hover:bg-proyecto-primary',
                'hover:text-white', 
                'transition-all', 
                'duration-200', 
                'ease-in-out',
                'cursor-pointer'

                ] 
    const classContentSelected = [
                'bg-proyecto-primary',
                'text-white', 
                'cursor-pointer'
    ]
    watch(
        () => route.query,
        (newValue, oldValue) => {
            query.value = newValue
                        console.log(query.value)

        }
    )
</script>

<template>
    <nav class="flex items-center gap-2">
        <div v-if="page > 1" class="w-10 h-10 border-2  rounded-md p-1 fill-gray-500 cursor-pointer hover:bg-proyecto-primary hover:fill-white transition-all duration-300 ease-in-out ">
            <IconArrowLeft></IconArrowLeft>
        </div>
        <router-link v-for="value in pageToShow" 
            :to="{query: { ...query, page:value }}"
            v-on="value != '...' ? {click: fetchSites} : {}"
            class="
            w-10 h-10 
            border-2 
            rounded-md 
            text-center 
            flex 
            justify-center 
            items-center 
            text-grey-700"
            :class="
                value !== '...' ? classContentHover : '',
                value == page ? classContentSelected : ''
            ">
            {{ value }}
        </router-link>
        <div v-if="page < pages" class="w-10 h-10 border-2  rounded-md p-1 fill-gray-600 cursor-pointer hover:bg-proyecto-primary hover:fill-white transition-all duration-300 ease-in-out ">
            <IconArrowRight></IconArrowRight>
        </div>
    </nav>
</template>
