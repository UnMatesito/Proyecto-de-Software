<script setup>
import { computed } from 'vue';

const props = defineProps({
  page: {
    type: Number,
    default: 1,
  },
  totalPages: {
    type: Number,
    default: 1,
  },
  pageSize: {
    type: Number,
    default: null,
  },
  pageSizeOptions: {
    type: Array,
    default: () => [],
  },
});

const emit = defineEmits(['page-change', 'page-size-change']);

const normalizedTotalPages = computed(() => {
  return props.totalPages && props.totalPages > 0 ? props.totalPages : 1;
});

const pagesToDisplay = computed(() => {
  const total = normalizedTotalPages.value;
  const current = props.page >= 1 ? props.page : 1;

  if (total <= 7) {
    return Array.from({ length: total }, (_, index) => ({
      type: 'page',
      value: index + 1,
      key: `page-${index + 1}`,
    }));
  }

  const pages = [{ type: 'page', value: 1, key: 'page-1' }];
  let start = Math.max(2, current - 1);
  let end = Math.min(total - 1, current + 1);

  if (start > 2) {
    pages.push({ type: 'ellipsis', key: 'ellipsis-start' });
  }

  for (let page = start; page <= end; page += 1) {
    pages.push({ type: 'page', value: page, key: `page-${page}` });
  }

  if (end < total - 1) {
    pages.push({ type: 'ellipsis', key: 'ellipsis-end' });
  }

  pages.push({ type: 'page', value: total, key: `page-${total}` });

  return pages;
});

const showPageSizeSelector = computed(
  () => Array.isArray(props.pageSizeOptions) && props.pageSizeOptions.length > 0,
);

function emitPageChange(newPage) {
  if (newPage === props.page || newPage < 1 || newPage > normalizedTotalPages.value) {
    return;
  }
  emit('page-change', newPage);
}

function goToPrevious() {
  emitPageChange(props.page - 1);
}

function goToNext() {
  emitPageChange(props.page + 1);
}

function onPageSizeChange(event) {
  const newSize = Number(event.target.value);
  if (!Number.isNaN(newSize)) {
    emit('page-size-change', newSize);
  }
}
</script>

<template>
  <div class="flex w-full flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
    <div v-if="showPageSizeSelector" class="flex items-center gap-2 text-sm text-gray-600">
      <label class="font-medium text-gray-700">Reseñas por página</label>
      <select
        :value="pageSize"
        class="rounded-md border border-gray-300 px-3 py-2 text-sm shadow-sm focus:border-proyecto-primary focus:outline-none"
        @change="onPageSizeChange"
      >
        <option
          v-for="option in pageSizeOptions"
          :key="`page-size-${option}`"
          :value="option"
        >
          {{ option }}
        </option>
      </select>
    </div>

    <div class="flex items-center justify-center gap-1">
      <button
        type="button"
        class="rounded-md border border-gray-300 px-3 py-2 text-sm font-medium text-gray-600 transition hover:bg-gray-100 disabled:cursor-not-allowed disabled:opacity-50"
        :disabled="page <= 1"
        @click="goToPrevious"
      >
        Anterior
      </button>

      <template v-for="item in pagesToDisplay" :key="item.key">
        <button
          v-if="item.type === 'page'"
          type="button"
          class="rounded-md border px-3 py-2 text-sm font-medium transition"
          :class="[
            item.value === page
              ? 'border-proyecto-primary bg-proyecto-primary text-white'
              : 'border-gray-300 text-gray-600 hover:bg-gray-100',
          ]"
          @click="emitPageChange(item.value)"
        >
          {{ item.value }}
        </button>
        <span
          v-else
          class="px-3 py-2 text-sm font-medium text-gray-400"
        >
          …
        </span>
      </template>

      <button
        type="button"
        class="rounded-md border border-gray-300 px-3 py-2 text-sm font-medium text-gray-600 transition hover:bg-gray-100 disabled:cursor-not-allowed disabled:opacity-50"
        :disabled="page >= normalizedTotalPages"
        @click="goToNext"
      >
        Siguiente
      </button>
    </div>
  </div>
</template>
