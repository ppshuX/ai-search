<script setup>
import { ArrowRight, LoaderCircle, Search } from 'lucide-vue-next'

defineProps({
  modelValue: { type: String, default: '' },
  loading: { type: Boolean, default: false },
  compact: { type: Boolean, default: false },
})

const emit = defineEmits(['update:modelValue', 'submit'])
</script>

<template>
  <form :class="['search-box', { compact }]" @submit.prevent="emit('submit')">
    <Search class="search-icon" :size="22" aria-hidden="true" />
    <label class="sr-only" for="search-input">搜索问题</label>
    <textarea
      id="search-input"
      :value="modelValue"
      :rows="compact ? 1 : 2"
      placeholder="输入任何问题，联网搜索并生成带引用的回答"
      @input="emit('update:modelValue', $event.target.value)"
      @keydown.enter.exact.prevent="emit('submit')"
    />
    <button class="submit-button" type="submit" :disabled="loading || !modelValue.trim()" aria-label="开始搜索">
      <LoaderCircle v-if="loading" class="spin" :size="20" aria-hidden="true" />
      <ArrowRight v-else :size="20" aria-hidden="true" />
    </button>
  </form>
</template>
