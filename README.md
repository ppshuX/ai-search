# ppshu-ai-search

AI 搜索引擎网站：用户输入自然语言问题，后端通过 Tavily 联网检索最新网页，将搜索结果注入 DeepSeek V4 Prompt，使用 SSE 流式输出带引用的综合回答，并展示完整搜索结果、搜索历史和相关问题。

## 技术栈

- 后端：Python、FastAPI、LangChain、langchain-tavily、OpenAI SDK 兼容 DeepSeek API
- 前端：Vue 3、Vite、Markdown It、highlight.js、lucide-vue-next
- 搜索：Tavily Search API
- 模型：DeepSeek V4，默认 `deepseek-v4-flash`

## 配置

复制环境变量模板：

```powershell
Copy-Item backend\.env.example backend\.env
```

真实联网模式需要填入：

```env
TAVILY_API_KEY=tvly-your-key
DEEPSEEK_API_KEY=sk-your-key
DEEPSEEK_BASE_URL=https://api.deepseek.com
DEEPSEEK_MODEL=deepseek-v4-flash
APP_DEMO_MODE=live
```

默认 `APP_DEMO_MODE=auto`，没有 API Key 时会进入本地演示模式，便于先跑通页面和 SSE。

## 启动后端

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

## 启动前端

```powershell
cd frontend
npm install
npm run dev
```

访问：

```text
http://localhost:5173
```

如后端地址不同，可在 `frontend/.env` 设置：

```env
VITE_API_BASE=http://localhost:8000/api
```

## API

`POST /api/search/stream`

请求体：

```json
{"query":"DeepSeek V4 有哪些新特性？"}
```

返回 `text/event-stream`，事件包括：

- `search_start`：开始检索
- `results`：完整搜索结果列表
- `answer_delta`：AI 回答增量文本
- `related_questions`：3 到 5 个相关问题
- `done`：完成
- `error`：错误信息

## 测试

```powershell
cd backend
.\.venv\Scripts\python.exe -m compileall app

cd ..\frontend
npm run build

cd ..
node scripts\e2e-check.cjs
```

`scripts/e2e-check.cjs` 会启动本地前后端，用系统 Chrome 验证搜索、流式回答、引用来源、完整搜索结果、搜索历史、相关问题和移动端横向溢出。
