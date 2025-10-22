<template>
    <nav>
        <ul class="flex gap-2">
            <li class="border-l-2 border-r-2 border-b-2 p-2">
                <button id="states-button" data-dropdown-toggle="dropdown-states" class="shrink-0 z-10 inline-flex items-center py-2.5 px-4 text-sm font-medium text-center text-gray-500 bg-gray-100 border border-gray-300 rounded-s-lg hover:bg-gray-200 focus:ring-4 focus:outline-none focus:ring-gray-100 dark:bg-gray-700 dark:hover:bg-gray-600 dark:focus:ring-gray-700 dark:text-white dark:border-gray-600" type="button"></button>
                <ul class="">
                    <li>A</li>
                    <li>b</li>
                    <li>c</li>
                </ul>
            </li>
            <li>
                <input type="text" name="" id="">
            </li>
            <li>
                <input type="checkbox" name="" id="">
            </li>
        </ul>
    </nav>
</template>

<script setup>
    defineProps(["province", "states"])
</script>