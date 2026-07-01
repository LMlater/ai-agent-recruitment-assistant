# backend-service

Spring Boot service for SmartCreditMultiAgent. It owns login/JWT, customer management, loan applications, Java-to-Python AI review calls, AI report persistence, agent execution logs, manual approval, and audit logs.

## Run

1. Start MySQL and Redis from the repository root:

```bash
docker compose up -d mysql redis
```

2. Start the Python agent service on port 8001.

3. Start this service:

```bash
mvn spring-boot:run
```

Swagger UI is available at `http://localhost:8080/swagger-ui.html`.

## First Requests

Initialize an administrator when the user table is empty:

```bash
curl -X POST http://localhost:8080/api/auth/init-admin \
  -H "Content-Type: application/json" \
  -d "{\"username\":\"admin\",\"password\":\"Admin@123456\",\"displayName\":\"Admin\"}"
```

Login:

```bash
curl -X POST http://localhost:8080/api/auth/login \
  -H "Content-Type: application/json" \
  -d "{\"username\":\"admin\",\"password\":\"Admin@123456\"}"
```

Use the returned JWT as `Authorization: Bearer <token>` for protected APIs.

## Core Flow

1. Create a masked customer under `/api/customers`.
2. Create a loan application under `/api/loan-applications`.
3. Submit it with `/api/loan-applications/{id}/submit`.
4. Run AI assistance with `/api/loan-applications/{id}/ai-review`.
5. Use `/api/approvals/{applicationId}/approve`, `/reject`, or `/need-more-info` for the final human decision.
