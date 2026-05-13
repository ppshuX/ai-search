<script setup>
import { computed } from 'vue'
import { Bot, ExternalLink } from 'lucide-vue-next'
import { md } from '../utils/markdown'

const props = defineProps({
  answer: { type: String, default: '' },
  sources: { type: Array, default: () => [] },
  loading: { type: Boolean, default: false },
})

const rendered = computed(() => md.render(props.answer || ''))
const hasInlineCitation = computed(() => /\[\d+\]/.test(props.answer))
const fallbackCitations = computed(() => props.sources.slice(0, 3).map((source) => `[${source.id}]`).join(' '))
</script>

<template>
  <section class="answer-panel" aria-live="polite">
    <div class="section-heading">
      <Bot :size="20" aria-hidden="true" />
      <h2>AI 综合回答</h2>
      <span v-if="loading" class="status-dot">生成中</span>
    </div>

    <div v-if="answer" class="markdown-body" v-html="rendered"></div>
    <p v-if="answer && sources.length && !hasInlineCitation" class="citation-fallback">
      参考来源：{{ fallbackCitations }}
    </p>
    <div v-else class="empty-answer">正在检索网页并组织答案。</div>

    <div v-if="sources.length" class="source-list">
      <h3>引用来源</h3>
      <a v-for="source in sources" :key="source.id" :href="source.url" target="_blank" rel="noreferrer">
        <span>[{{ source.id }}]</span>
        <strong>{{ source.title }}</strong>
        <ExternalLink :size="15" aria-hidden="true" />
      </a>
    </div>
  </section>
</template>
