const KEY = 'ppshu-ai-search-history'

export function loadHistory() {
  try {
    return JSON.parse(localStorage.getItem(KEY) || '[]')
  } catch {
    return []
  }
}

export function saveHistoryItem(query) {
  const next = [query, ...loadHistory().filter((item) => item !== query)].slice(0, 10)
  localStorage.setItem(KEY, JSON.stringify(next))
  return next
}

export function clearHistory() {
  localStorage.removeItem(KEY)
}
