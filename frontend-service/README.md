# frontend-service

Formal SmartCreditMultiAgent workspace built with Vue 3, Vite, and Element Plus.

## Local Start

```bash
cd frontend-service
npm install
npm run dev
```

Open:

```text
http://localhost:5173
```

The Vite dev server proxies `/api` to `http://localhost:8080` and `/agent-api` to `http://localhost:8001`.

## Demo Flow

1. Start `agent-service`.
2. Start `backend-service`.
3. Start this frontend workspace.
4. Login with the local demo admin.
5. Upload `docs/sample_import/loan_applications_sample.csv`.
6. Click `批量 AI 检测上传文件`.
7. Open each row to inspect Agent Trace, Tool Calls, Policy References, AI report summary, and manual approval controls.

AI review is executed sequentially for uploaded rows to avoid overloading a real LLM provider.
