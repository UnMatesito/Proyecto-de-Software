<template> <!-- component -->
<div class=" bg-white">
  <label class="relative inline-flex cursor-pointer">
    <input @click="active = !active" id="switch" type="checkbox" class="peer sr-only" />
    <label for="switch" class="hidden"></label>
    <div class="peer h-6 w-11 rounded-full border 
    bg-red-400 
    after:absolute 
    after:left-[2px] 
    after:top-0.5 
    after:h-5 
    after:w-5 
    after:rounded-full 
    after:border 
    after:border-gray-300 
    after:bg-white 
    after:transition-all 
    after:content-[''] 
    peer-checked:bg-proyecto-primary
    peer-checked:after:translate-x-full 
    peer-checked:after:content-[<i class='fa-solid fa-xmark'></i>] 
    peer-checked:after:border-white 
    peer-focus:ring-green-300">
    </div>
    <span v-if="!active" class="text-white text-xs font-semibold bg-red-500 p-1 rounded-full border">
        Desactivado
    </span>
    <span v-if="active" class="text-white text-xs font-semibold bg-green-500 p-1 rounded-full border">
        Activado
    </span>
  </label>
</div>


</template>

<script setup>
    import { ref } from 'vue'
    const active = ref(false)
    const props = defineProps(["isActive"])
</script>