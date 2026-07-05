const TOKEN_KEY = "smartcredit.frontend.token";

export function getToken() {
  return localStorage.getItem(TOKEN_KEY) || "";
}

export function setToken(token) {
  if (token) {
    localStorage.setItem(TOKEN_KEY, token);
  } else {
    localStorage.removeItem(TOKEN_KEY);
  }
}

async function request(path, options = {}) {
  const headers = { Accept: "application/json", ...(options.headers || {}) };
  if (options.body !== undefined && !(options.body instanceof FormData)) {
    headers["Content-Type"] = "application/json";
  }
  const token = getToken();
  if (token) {
    headers.Authorization = `Bearer ${token}`;
  }

  const response = await fetch(path, { ...options, headers });
  const text = await response.text();
  const payload = text ? JSON.parse(text) : null;
  if (!response.ok) {
    throw new Error(payload?.message || `HTTP ${response.status}`);
  }
  if (payload && Object.prototype.hasOwnProperty.call(payload, "code")) {
    if (payload.code !== 0) {
      throw new Error(payload.message || "请求失败");
    }
    return payload.data;
  }
  return payload;
}

export async function initAdmin() {
  return request("/api/auth/init-admin", {
    method: "POST",
    body: JSON.stringify({
      username: "admin",
      password: "Admin@123456",
      displayName: "Demo Admin"
    })
  });
}

export async function login(username, password) {
  const data = await request("/api/auth/login", {
    method: "POST",
    body: JSON.stringify({ username, password })
  });
  setToken(data?.token);
  return data;
}

export async function downloadCsvTemplate() {
  const response = await fetch("/api/loan-applications/batch-import-template", {
    headers: { Authorization: `Bearer ${getToken()}` }
  });
  if (!response.ok) {
    throw new Error(`下载 CSV 模板失败：HTTP ${response.status}`);
  }
  const blob = await response.blob();
  const url = window.URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = "loan_applications_template.csv";
  document.body.appendChild(link);
  link.click();
  link.remove();
  window.URL.revokeObjectURL(url);
}

export async function uploadCsv(file) {
  const formData = new FormData();
  formData.append("file", file);
  return request("/api/loan-applications/batch-import", {
    method: "POST",
    body: formData
  });
}

export async function aiReview(applicationId) {
  return request(`/api/loan-applications/${encodeURIComponent(applicationId)}/ai-review`, {
    method: "POST"
  });
}

export async function getApplication(applicationId) {
  return request(`/api/loan-applications/${encodeURIComponent(applicationId)}`);
}

export async function listApplications(page = 1, size = 20) {
  return request(`/api/loan-applications?page=${page}&size=${size}`);
}

export async function getAiReports(applicationId) {
  return request(`/api/loan-applications/${encodeURIComponent(applicationId)}/ai-reports`);
}

export async function getAgentLogs(idOrWorkflowId, byWorkflow = false) {
  if (byWorkflow) {
    return request(`/api/agent-workflows/${encodeURIComponent(idOrWorkflowId)}/logs`);
  }
  return request(`/api/loan-applications/${encodeURIComponent(idOrWorkflowId)}/agent-logs`);
}

export async function manualApprove(applicationId, comment) {
  return request(`/api/approvals/${encodeURIComponent(applicationId)}/approve`, {
    method: "POST",
    body: JSON.stringify({ comment })
  });
}

export async function manualReject(applicationId, comment) {
  return request(`/api/approvals/${encodeURIComponent(applicationId)}/reject`, {
    method: "POST",
    body: JSON.stringify({ comment })
  });
}

export async function manualNeedMoreInfo(applicationId, comment) {
  return request(`/api/approvals/${encodeURIComponent(applicationId)}/need-more-info`, {
    method: "POST",
    body: JSON.stringify({ comment })
  });
}

export async function updateMaterials(applicationId, summary) {
  return request(`/api/loan-applications/${encodeURIComponent(applicationId)}/materials`, {
    method: "POST",
    body: JSON.stringify({ materialSummary: summary })
  });
}

export async function resubmit(applicationId) {
  return request(`/api/loan-applications/${encodeURIComponent(applicationId)}/resubmit`, {
    method: "POST"
  });
}

export async function getApprovalHistory(applicationId) {
  return request(`/api/approvals/${encodeURIComponent(applicationId)}/history`);
}

export async function getMaterialUpdates(applicationId) {
  return request(`/api/loan-applications/${encodeURIComponent(applicationId)}/material-updates`);
}
