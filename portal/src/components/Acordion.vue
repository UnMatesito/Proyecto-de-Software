<script setup>
import { ref, watchEffect } from 'vue'
const props = defineProps(['content'])
const faqs = ref([])
watchEffect(() => faqs.value = props.content)
const activeFaq = ref(null)
const handleToggle = (faqId) => {
  activeFaq.value = activeFaq.value === faqId ? null : faqId
}
</script>

<template>
  <section class="relative z-20 overflow-hidden w-full rounded-xl bg-white p-2 shadow-md dark:bg-dark-3">
    <div class="w-full">
      <div class="flex flex-wrap">
        <div class="w-full">
          <template v-for="faq in faqs" :key="faq.id">
            <div class="w-full rounded-lg bg-white">
              <button class="faq-btn flex w-full text-left" @click="handleToggle(faq.id)">
                <div class="mr-1 flex h-10 w-full max-w-[40px] items-center justify-center rounded-lg bg-primary/5 text-primary dark:bg-white/5">
                  <svg
                    class="fill-primary stroke-primary duration-200 ease-in-out"
                    :class="{ 'rotate-180': activeFaq === faq.id }"
                    width="14"
                    height="10"
                    viewBox="0 0 17 10"
                    xmlns="http://www.w3.org/2000/svg"
                  >
                    <path
                      d="M7.28687 8.43257L7.29496 8.43985C7.62576 8.73124 8.02464 8.86001 8.41472 8.86001C8.83092 8.86001 9.22376 8.69083 9.53447 8.41713L9.54184 8.41052L15.7631 2.70784L15.7691 2.70231L15.7749 2.69659C16.0981 2.38028 16.1985 1.80579 15.7981 1.41393C15.4803 1.1028 14.9167 1.00854 14.5249 1.38489L8.41472 7.00806L2.29995 1.38063L2.29151 1.37286L2.28271 1.36548C1.93092 1.07036 1.38469 1.06804 1.03129 1.41393L1.01755 1.42738L1.00488 1.44184C0.69687 1.79355 0.695778 2.34549 1.0545 2.69659L1.05999 2.70196L1.06565 2.70717L7.28687 8.43257Z"
                      fill=""
                      stroke=""
                    />
                  </svg>
                </div>
                <div class="w-full">
                  <h4 class="mt-2 text-md font-semibold text-proyecto-accent">
                    {{ faq.header }}
                  </h4>
                </div>
              </button>
              <div v-show="activeFaq === faq.id" class="ml-5">
                <p class="py-3 text-md leading-relaxed text-body-color dark:text-dark-6 break-words hyphens-auto">
                  {{ faq.text }}
                </p>
              </div>
            </div>
          </template>
        </div>
      </div>
    </div>
  </section>
</template>
