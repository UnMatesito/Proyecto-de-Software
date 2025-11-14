<template>
    
    <div role="status" class="  border border-default divide-y divide-default rounded-base shadow-xs animate-pulse  w-full">
        <div v-for="value in 2" class=" items-center justify-between pb-4 w-full">
            <div>
                <div class="flex items-center justify-between">
                    <div class="flex items-center my-4">
                        <svg class="w-8 h-8 text-fg-disabled me-3" aria-hidden="true" xmlns="http://www.w3.org/2000/svg" width="24" height="24" fill="none" viewBox="0 0 24 24"><path stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 21a9 9 0 1 0 0-18 9 9 0 0 0 0 18Zm0 0a8.949 8.949 0 0 0 4.951-1.488A3.987 3.987 0 0 0 13 16h-2a3.987 3.987 0 0 0-3.951 3.512A8.948 8.948 0 0 0 12 21Zm3-11a3 3 0 1 1-6 0 3 3 0 0 1 6 0Z"/></svg>
                        <div>
                            <div class="h-2 bg-gray-300 rounded-full w-32 mb-2"></div>
                            <div class="w-1/2 h-2 bg-gray-300 rounded-full"></div>
                        </div>
                    </div>
                    <div class="h-2.5 bg-gray-300 rounded-full w-12"></div>
                </div>
 
                <div class="w-full">
                    <div class="h-2 bg-gray-300 rounded-full max-w-[80%] mb-2.5"></div>
                    <div class="h-2 bg-gray-300  rounded-full mb-2.5 max-w-[70%]"></div>
                    <div class="h-2 bg-gray-300  rounded-full max-w-[60%] mb-2.5"></div>
                    <div class="h-2 bg-gray-300  rounded-full max-w-[55%] mb-2.5"></div>
                </div>

            </div>
        </div>
    </div>

</template>