import MarkdownIt from 'markdown-it'
import hljs from 'highlight.js'

export const md = new MarkdownIt({
  html: false,
  linkify: true,
  breaks: true,
  highlight(code, language) {
    const validLanguage = language && hljs.getLanguage(language)
    if (validLanguage) {
      return `<pre class="hljs"><code>${hljs.highlight(code, { language }).value}</code></pre>`
    }
    return `<pre class="hljs"><code>${md.utils.escapeHtml(code)}</code></pre>`
  },
})
