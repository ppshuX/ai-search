const API_BASE = import.meta.env.VITE_API_BASE || 'http://127.0.0.1:8000/api'

const decoder = new TextDecoder()

function emitEvent(rawEvent, handlers) {
  const lines = rawEvent.split('\n').filter(Boolean)
  const eventLine = lines.find((line) => line.startsWith('event: '))
  const dataLines = lines.filter((line) => line.startsWith('data: '))

  if (!eventLine || dataLines.length === 0) return

  const event = eventLine.slice(7)
  const dataText = dataLines.map((line) => line.slice(6)).join('\n')
  const data = JSON.parse(dataText)
  handlers[event]?.(data)
}

export async function streamSearch(query, handlers = {}) {
  const response = await fetch(`${API_BASE}/search/stream`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ query }),
  })

  if (!response.ok || !response.body) {
    throw new Error(`请求失败：HTTP ${response.status}`)
  }

  const reader = response.body.getReader()
  let buffer = ''

  while (true) {
    const { value, done } = await reader.read()
    if (done) break

    buffer += decoder.decode(value, { stream: true })
    const events = buffer.split('\n\n')
    buffer = events.pop() || ''

    for (const event of events) {
      if (event.trim()) emitEvent(event, handlers)
    }
  }

  if (buffer.trim()) emitEvent(buffer, handlers)
}
