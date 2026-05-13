const { spawn, spawnSync } = require('node:child_process')
const http = require('node:http')
const path = require('node:path')
const { createRequire } = require('node:module')

const root = path.resolve(__dirname, '..')
const backendDir = path.join(root, 'backend')
const frontendDir = path.join(root, 'frontend')
const requireFromFrontend = createRequire(path.join(frontendDir, 'package.json'))
const { chromium } = requireFromFrontend('playwright-core')
const chromePath = 'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe'
const children = []

function start(cmd, args, cwd) {
  const child = spawn(cmd, args, {
    cwd,
    env: process.env,
    shell: false,
    stdio: ['ignore', 'pipe', 'pipe'],
  })
  child.stdout.on('data', (data) => process.stdout.write(`[${path.basename(cwd)}] ${data}`))
  child.stderr.on('data', (data) => process.stderr.write(`[${path.basename(cwd)}] ${data}`))
  children.push(child)
  return child
}

function request(url) {
  return new Promise((resolve, reject) => {
    const req = http.get(url, (res) => {
      res.resume()
      res.on('end', () => resolve(res.statusCode))
    })
    req.on('error', reject)
    req.setTimeout(2000, () => req.destroy(new Error('timeout')))
  })
}

async function waitFor(url) {
  const started = Date.now()
  while (Date.now() - started < 45000) {
    try {
      const status = await request(url)
      if (status && status < 500) return
    } catch {
      // keep polling
    }
    await new Promise((resolve) => setTimeout(resolve, 500))
  }
  throw new Error(`not ready: ${url}`)
}

async function run() {
  let browser
  try {
    console.log('starting services')
    start(path.join(backendDir, '.venv', 'Scripts', 'python.exe'), [
      '-m',
      'uvicorn',
      'app.main:app',
      '--host',
      '127.0.0.1',
      '--port',
      '8000',
    ], backendDir)
    start('cmd.exe', ['/c', 'npm run dev -- --host 127.0.0.1 --port 5173'], frontendDir)

    await waitFor('http://127.0.0.1:8000/api/health')
    await waitFor('http://127.0.0.1:5173')

    browser = await chromium.launch({ executablePath: chromePath, headless: true })
    const page = await browser.newPage({ viewport: { width: 1440, height: 900 } })
    const consoleErrors = []
    page.on('console', (msg) => {
      if (msg.type() === 'error') consoleErrors.push(msg.text())
    })
    page.on('pageerror', (err) => consoleErrors.push(err.message))

    await page.goto('http://127.0.0.1:5173', { waitUntil: 'domcontentloaded', timeout: 20000 })
    await page.waitForSelector('.home-view textarea#search-input', { timeout: 10000 })
    await page.fill('textarea#search-input', 'DeepSeek V4 features')
    await page.click('button.submit-button')
    await page.waitForSelector('.results-view', { timeout: 15000 })
    await page.waitForFunction(
      () => document.querySelectorAll('.result-item').length > 0 || !!document.querySelector('.error-banner'),
      null,
      { timeout: 120000 },
    )

    const firstError = await page.locator('.error-banner').count()
      ? await page.locator('.error-banner').innerText()
      : ''
    if (firstError) throw new Error(`UI error: ${firstError}`)

    await page.waitForFunction(
      () => (document.querySelector('.markdown-body')?.innerText || '').length > 50 || !!document.querySelector('.error-banner'),
      null,
      { timeout: 180000 },
    )

    const secondError = await page.locator('.error-banner').count()
      ? await page.locator('.error-banner').innerText()
      : ''
    if (secondError) throw new Error(`UI error: ${secondError}`)

    await page.waitForFunction(() => document.querySelectorAll('.related-list button').length >= 1, null, {
      timeout: 120000,
    })

    const answerText = await page.locator('.answer-panel').innerText()
    const checks = {
      title: await page.title(),
      answerLength: answerText.length,
      hasCitation: /\[\d+\]/.test(answerText),
      sources: await page.locator('.source-list a').count(),
      results: await page.locator('.result-item').count(),
      related: await page.locator('.related-list button').count(),
      history: await page.locator('.history-item').count(),
      desktopOverflow: await page.evaluate(
        () => document.documentElement.scrollWidth > document.documentElement.clientWidth + 1,
      ),
      consoleErrors: consoleErrors.filter((message) => !message.includes('net::ERR_CONNECTION_CLOSED')),
    }

    await page.click('.related-list button')
    await page.waitForFunction(() => document.querySelectorAll('.history-item').length >= 2, null, {
      timeout: 30000,
    })

    const mobile = await browser.newPage({ viewport: { width: 390, height: 844 }, isMobile: true })
    await mobile.goto('http://127.0.0.1:5173', { waitUntil: 'domcontentloaded', timeout: 20000 })
    const mobileOverflow = await mobile.evaluate(
      () => document.documentElement.scrollWidth > document.documentElement.clientWidth + 1,
    )

    if (checks.title !== 'ppshu-ai-search') throw new Error(`bad title: ${checks.title}`)
    if (!checks.hasCitation || checks.sources < 1 || checks.results < 1 || checks.related < 1 || checks.history < 1) {
      throw new Error(`bad checks: ${JSON.stringify(checks)}`)
    }
    if (checks.desktopOverflow) throw new Error('desktop overflow')
    if (checks.consoleErrors.length) throw new Error(`console errors: ${checks.consoleErrors.join(' | ')}`)
    if (mobileOverflow) throw new Error('mobile overflow')

    console.log(`FINAL_LIVE_E2E_CHECKS=${JSON.stringify(checks, null, 2)}`)
  } finally {
    if (browser) await browser.close().catch(() => {})
    for (const child of children) {
      if (process.platform === 'win32') {
        spawnSync('taskkill', ['/PID', String(child.pid), '/T', '/F'], { stdio: 'ignore' })
      } else {
        child.kill()
      }
    }
  }
}

run()
  .then(() => {
    process.exitCode = 0
  })
  .catch((err) => {
    console.error(err)
    process.exitCode = 1
  })
