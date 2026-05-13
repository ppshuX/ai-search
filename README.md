# ppshu-ai-search

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python 3.11+](https://img.shields.io/badge/Python-3.11+-green.svg)](https://www.python.org/)
[![Vue 3](https://img.shields.io/badge/Vue-3-42b883.svg)](https://vuejs.org/)

`ppshu-ai-search` 是一个 AI 搜索引擎示例项目。用户输入自然语言问题后，后端会先通过 Tavily 获取联网搜索结果，再把搜索上下文交给 DeepSeek OpenAI 兼容接口生成带引用编号的综合回答，并通过 SSE 流式返回给前端。

项目同时提供本地演示模式：没有配置 API Key 时也能跑通页面、流式输出、搜索结果、引用来源、搜索历史和相关问题等核心交互。

<img width="640" height="365" alt="image" src="https://github.com/user-attachments/assets/646d5d2c-e19c-4bf4-897b-99c47f1d9903" />

## 功能特性

- 自然语言搜索：输入任意问题后触发联网搜索和 AI 综合回答。
- SSE 流式输出：回答内容按增量片段实时显示，降低等待感。
- 引用来源：搜索结果会被编号，回答中使用 `[1]`、`[2]` 这类编号标注来源。
- 完整结果列表：前端展示 Tavily 返回的网页标题、链接、摘要和来源编号。
- 相关问题：回答生成后继续生成 3 到 5 个相关追问。
- 搜索历史：浏览器本地保存最近 10 条搜索记录，支持一键复用和清空。
- 演示模式：缺少 Tavily 或 DeepSeek Key 时自动使用内置演示数据。
- 端到端检查：`scripts/e2e-check.cjs` 会启动前后端并用 Chrome 验证主要 UI 流程。

<img width="640" height="420" alt="image" src="https://github.com/user-attachments/assets/dc685add-fc32-46ac-8497-f771e8d69763" />


## 技术栈

后端：

- Python
- FastAPI
- Pydantic
- Uvicorn
- LangChain Tavily
- OpenAI Python SDK，用于调用 DeepSeek 的 OpenAI 兼容接口

前端：

- Vue 3
- Vite
- Markdown It
- highlight.js
- lucide-vue-next

外部服务：

- Tavily Search API
- DeepSeek API

## 目录

- [功能特性](#功能特性)
- [技术栈](#技术栈)
- [项目结构](#项目结构)
- [环境要求](#环境要求)
- [快速启动](#快速启动)
- [环境变量说明](#环境变量说明)
- [API 说明](#api-说明)
- [测试与检查](#测试与检查)
- [常见问题](#常见问题)
- [开发说明](#开发说明)
- [License](#license)

## 项目结构

```text
.
├── backend
│   ├── app
│   │   ├── api
│   │   │   └── routes.py          # HTTP API 与 SSE 事件流
│   │   ├── services
│   │   │   ├── ai_service.py      # DeepSeek 调用、回答生成、相关问题生成
│   │   │   └── search_service.py  # Tavily 搜索与演示搜索数据
│   │   ├── config.py              # 环境变量与应用配置
│   │   ├── main.py                # FastAPI 应用入口
│   │   └── models.py              # 请求与响应数据模型
│   ├── .env.example               # 后端环境变量模板
│   └── requirements.txt
├── frontend
│   ├── src
│   │   ├── components             # 搜索框、回答面板、结果列表
│   │   ├── utils                  # SSE API、Markdown、搜索历史
│   │   ├── App.vue
│   │   └── main.js
│   ├── package.json
│   └── vite.config.js
├── scripts
│   └── e2e-check.cjs              # 本地端到端检查脚本
└── README.md
```

## 环境要求

- Python 3.11 或更高版本
- Node.js 20 或更高版本
- npm
- Google Chrome，端到端检查脚本会使用系统 Chrome
- Tavily API Key，真实联网搜索模式需要
- DeepSeek API Key，真实 AI 回答模式需要

## 快速启动

### 1. 配置后端环境变量

复制环境变量模板：

```powershell
Copy-Item backend\.env.example backend\.env
```

如果只想先本地跑通，可以保持 `APP_DEMO_MODE=auto`，并暂时不填写 API Key。此时后端会使用演示搜索结果和演示回答。

真实联网模式需要在 `backend/.env` 中填写：

```env
APP_DEMO_MODE=live

TAVILY_API_KEY=tvly-your-key
TAVILY_MAX_RESULTS=8
TAVILY_SEARCH_DEPTH=advanced

DEEPSEEK_API_KEY=sk-your-key
DEEPSEEK_BASE_URL=https://api.deepseek.com
DEEPSEEK_MODEL=deepseek-v4-flash
DEEPSEEK_TEMPERATURE=0.2
```

### 2. 启动后端

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

健康检查：

```powershell
Invoke-RestMethod http://localhost:8000/api/health
```

正常情况下会返回类似：

```json
{
  "ok": true,
  "app": "ppshu-ai-search",
  "demoMode": true,
  "model": "deepseek-v4-flash"
}
```

### 3. 启动前端

新开一个终端：

```powershell
cd frontend
npm install
npm run dev
```

访问：

```text
http://localhost:5173
```

如果后端地址不是默认的 `http://127.0.0.1:8000/api`，可以在 `frontend/.env` 中设置：

```env
VITE_API_BASE=http://localhost:8000/api
```

## 环境变量说明

后端环境变量位于 `backend/.env`。

| 变量 | 默认值 | 说明 |
| --- | --- | --- |
| `APP_DEMO_MODE` | `auto` | 运行模式。`auto` 表示缺少 Key 时自动演示；`live` 表示强制真实模式；`true`、`1`、`yes` 表示强制演示模式。 |
| `CORS_ORIGINS` | `http://localhost:5173,http://127.0.0.1:5173` | 允许访问后端的前端源，多个地址用英文逗号分隔。 |
| `TAVILY_API_KEY` | 空 | Tavily Search API Key。 |
| `TAVILY_MAX_RESULTS` | `8` | 每次搜索最多返回的结果数量。 |
| `TAVILY_SEARCH_DEPTH` | `advanced` | Tavily 搜索深度。常用值为 `basic` 或 `advanced`。 |
| `DEEPSEEK_API_KEY` | 空 | DeepSeek API Key。 |
| `DEEPSEEK_BASE_URL` | `https://api.deepseek.com` | DeepSeek OpenAI 兼容接口地址。 |
| `DEEPSEEK_MODEL` | `deepseek-v4-flash` | 用于生成回答的模型名。 |
| `DEEPSEEK_TEMPERATURE` | `0.2` | 回答生成温度，数值越高输出越发散。 |

前端环境变量位于 `frontend/.env`。

| 变量 | 默认值 | 说明 |
| --- | --- | --- |
| `VITE_API_BASE` | `http://127.0.0.1:8000/api` | 前端请求后端 API 的基础地址。 |

## API 说明

### `GET /api/health`

用于检查后端是否启动，以及当前是否处于演示模式。

响应示例：

```json
{
  "ok": true,
  "app": "ppshu-ai-search",
  "demoMode": false,
  "model": "deepseek-v4-flash"
}
```

### `POST /api/search/stream`

执行搜索并以 `text/event-stream` 返回流式结果。

请求体：

```json
{
  "query": "DeepSeek V4 有哪些新特性？"
}
```

`query` 长度限制：

- 最短 1 个字符
- 最长 500 个字符

SSE 事件：

| 事件名 | 说明 |
| --- | --- |
| `search_start` | 搜索开始，返回当前 query。 |
| `results` | 返回完整搜索结果列表。 |
| `answer_delta` | 返回 AI 回答的增量文本片段。前端会持续拼接这些片段。 |
| `related_questions` | 返回相关追问列表。 |
| `done` | 当前搜索流程完成。 |
| `error` | 搜索或生成过程中出现错误。 |

事件格式示例：

```text
event: answer_delta
data: {"delta":"这是一个流式片段"}
```

前端通过 `frontend/src/utils/api.js` 读取 SSE 响应，并按事件名调用对应 handler。

## 运行模式

### 演示模式

当 `APP_DEMO_MODE=auto` 且没有同时配置 `TAVILY_API_KEY` 和 `DEEPSEEK_API_KEY` 时，后端会自动进入演示模式。

演示模式的特点：

- 搜索结果来自 `backend/app/services/search_service.py` 中的内置 `DEMO_RESULTS`。
- 回答由 `backend/app/services/ai_service.py` 本地模拟流式输出。
- 不消耗外部 API 额度。
- 适合调试页面、SSE 事件处理和基础交互。

### 真实模式

真实模式需要：

- `APP_DEMO_MODE=live`
- `TAVILY_API_KEY` 有效
- `DEEPSEEK_API_KEY` 有效

真实模式流程：

1. 后端接收搜索请求。
2. `SearchService` 调用 Tavily 获取搜索结果。
3. 后端先通过 `results` 事件把搜索结果发给前端。
4. `AIService` 将搜索结果整理为上下文并调用 DeepSeek。
5. DeepSeek 的流式回答被转换成多个 `answer_delta` SSE 事件。
6. 回答结束后生成相关问题并发送 `related_questions`。
7. 最后发送 `done`。

## 测试与检查

### 后端语法检查

```powershell
cd backend
.\.venv\Scripts\python.exe -m compileall app
```

### 前端构建检查

```powershell
cd frontend
npm run build
```

### 端到端检查

```powershell
cd .
node scripts\e2e-check.cjs
```

端到端脚本会：

- 启动后端 `http://127.0.0.1:8000`
- 启动前端 `http://127.0.0.1:5173`
- 打开系统 Chrome
- 执行一次搜索
- 检查回答、引用、来源、搜索结果、相关问题和搜索历史
- 检查桌面端和移动端是否出现横向溢出

注意：脚本默认使用 `backend/.venv/Scripts/python.exe`，因此需要先完成后端虚拟环境安装。

## 常见问题

### 页面能打开，但搜索失败

先检查后端是否启动：

```powershell
Invoke-RestMethod http://localhost:8000/api/health
```

如果后端端口不是 `8000`，请同步更新 `frontend/.env` 中的 `VITE_API_BASE`。

### 强制真实模式后报 API Key 错误

确认 `backend/.env` 中已经填写：

```env
APP_DEMO_MODE=live
TAVILY_API_KEY=...
DEEPSEEK_API_KEY=...
```

如果只想本地调试页面，把 `APP_DEMO_MODE` 改回：

```env
APP_DEMO_MODE=auto
```

### 前端请求被 CORS 拦截

把当前前端地址加入 `backend/.env`：

```env
CORS_ORIGINS=http://localhost:5173,http://127.0.0.1:5173
```

修改后需要重启后端。

### 端到端脚本找不到 Chrome

脚本中的 Chrome 路径是：

```text
C:\Program Files\Google\Chrome\Application\chrome.exe
```

如果你的 Chrome 安装在其他位置，需要修改 `scripts/e2e-check.cjs` 中的 `chromePath`。

### 修改环境变量后没有生效

后端配置在启动时读取 `.env`，修改后请重启 `uvicorn`。

## 开发说明

- 后端 API 前缀由 `backend/app/config.py` 中的 `api_prefix` 控制，当前为 `/api`。
- 前端默认 API 地址在 `frontend/src/utils/api.js` 中，优先读取 `VITE_API_BASE`。
- 搜索历史保存在浏览器 `localStorage`，key 为 `ppshu-ai-search-history`。
- Markdown 渲染关闭了 HTML，避免直接渲染模型返回的 HTML 内容。
- 如果模型回答没有引用编号，后端和前端都会提供最多前三个来源的兜底引用展示。

## License

[MIT](LICENSE)

