<script setup>
import { ExternalLink, ListChecks } from 'lucide-vue-next'

defineProps({
  results: { type: Array, default: () => [] },
})
</script>

<template>
  <section class="results-panel">
    <div class="section-heading">
      <ListChecks :size="20" aria-hidden="true" />
      <h2>完整搜索结果</h2>
      <span>{{ results.length }} 条</span>
    </div>

    <div class="result-list">
      <a v-for="result in results" :key="result.id" class="result-item" :href="result.url" target="_blank" rel="noreferrer">
        <div class="result-topline">
          <span class="result-index">{{ result.id }}</span>
          <span class="result-url">{{ result.url }}</span>
          <ExternalLink :size="14" aria-hidden="true" />
        </div>
        <h3>{{ result.title }}</h3>
        <p>{{ result.content }}</p>
      </a>
    </div>
  </section>
</template>
