<script setup>
import { computed, ref } from 'vue'
import { Clock, RotateCcw, Sparkles, Trash2 } from 'lucide-vue-next'
import AnswerPanel from './components/AnswerPanel.vue'
import ResultsList from './components/ResultsList.vue'
import SearchBox from './components/SearchBox.vue'
import { streamSearch } from './utils/api'
import { clearHistory, loadHistory, saveHistoryItem } from './utils/history'

const query = ref('')
const activeQuery = ref('')
const answer = ref('')
const results = ref([])
const relatedQuestions = ref([])
const history = ref(loadHistory())
const loading = ref(false)
const error = ref('')

const hasSearched = computed(() => activeQuery.value || answer.value || results.value.length)
const sources = computed(() => results.value.map((item) => ({ id: item.id, title: item.title, url: item.url })))

async function submitSearch(nextQuery = query.value) {
  const trimmed = nextQuery.trim()
  if (!trimmed || loading.value) return

  query.value = trimmed
  activeQuery.value = trimmed
  answer.value = ''
  results.value = []
  relatedQuestions.value = []
  error.value = ''
  loading.value = true
  history.value = saveHistoryItem(trimmed)

  try {
    await streamSearch(trimmed, {
      results(data) {
        results.value = data.results || []
      },
      answer_delta(data) {
        answer.value += data.delta || ''
      },
      related_questions(data) {
        relatedQuestions.value = data.questions || []
      },
      error(data) {
        error.value = data.message || '搜索失败'
        loading.value = false
      },
      done() {
        loading.value = false
      },
    })
  } catch (caught) {
    error.value = caught instanceof Error ? caught.message : '搜索失败'
    loading.value = false
  }
}

function resetHome() {
  activeQuery.value = ''
  answer.value = ''
  results.value = []
  relatedQuestions.value = []
  error.value = ''
}

function clearAllHistory() {
  clearHistory()
  history.value = []
}
</script>

<template>
  <main :class="['app-shell', { searched: hasSearched }]">
    <section v-if="!hasSearched" class="home-view">
      <div class="brand-mark">
        <Sparkles :size="24" aria-hidden="true" />
      </div>
      <h1>ppshu-ai-search</h1>
      <p>输入问题，实时搜索最新网页，由 DeepSeek V4 综合生成带引用的答案。</p>
      <SearchBox v-model="query" :loading="loading" @submit="submitSearch()" />

      <div v-if="history.length" class="history-strip" aria-label="搜索历史">
        <button v-for="item in history.slice(0, 5)" :key="item" type="button" @click="submitSearch(item)">
          <Clock :size="15" aria-hidden="true" />
          <span>{{ item }}</span>
        </button>
      </div>
    </section>

    <section v-else class="results-view">
      <header class="topbar">
        <button class="wordmark" type="button" @click="resetHome">
          ppshu-ai-search
        </button>
        <SearchBox v-model="query" compact :loading="loading" @submit="submitSearch()" />
      </header>

      <div class="content-grid">
        <aside class="side-rail">
          <div class="rail-section">
            <div class="rail-heading">
              <Clock :size="17" aria-hidden="true" />
              <span>历史</span>
              <button v-if="history.length" class="icon-button" type="button" aria-label="清空历史" @click="clearAllHistory">
                <Trash2 :size="15" aria-hidden="true" />
              </button>
            </div>
            <button v-for="item in history" :key="item" class="history-item" type="button" @click="submitSearch(item)">
              <RotateCcw :size="14" aria-hidden="true" />
              <span>{{ item }}</span>
            </button>
          </div>
        </aside>

        <div class="main-column">
          <div class="query-line">
            <span>搜索问题</span>
            <h1>{{ activeQuery }}</h1>
          </div>

          <div v-if="error" class="error-banner">{{ error }}</div>

          <AnswerPanel :answer="answer" :sources="sources" :loading="loading" />

          <section v-if="relatedQuestions.length" class="related-panel">
            <div class="section-heading">
              <Sparkles :size="19" aria-hidden="true" />
              <h2>相关问题</h2>
            </div>
            <div class="related-list">
              <button v-for="item in relatedQuestions" :key="item" type="button" @click="submitSearch(item)">
                {{ item }}
              </button>
            </div>
          </section>

          <ResultsList :results="results" />
        </div>
      </div>
    </section>
  </main>
</template>
