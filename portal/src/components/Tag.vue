<template>
        <div class="flex gap-2 text-blue-700 flex-wrap border-t-2 pt-1">
                <span v-for="tag in tags_to_show" class="inline-flex items-center bg-blue-300 text-sky-950 text-xs font-bold px-2.5 py-0.5 border-2 rounded-full ">{{ tag }}</span>
                <span v-if="tags_left > 0" class="inline-flex items-center bg-blue-300 text-sky-950 text-xs font-bold px-2.5 py-0.5 border-2 rounded-full ">{{ `+${tags_left}` }}</span>
        </div>
</template>

<script setup>
    //Si se quieren mostrar todos los tagas el props max no se manda, si queres poner un limite mandalo en max
    //Por ejemplo max = 5
    const props = defineProps({
        tags: Array,
        max: {
            type: Number,
            default: 0
        }
    })
    const tags_to_show = props.max > 0 ? props.tags.slice(0, props.max) : props.tags
    const tags_left = props.tags.length > props.max & props.max ? props.tags.length - props.max : 0
</script>