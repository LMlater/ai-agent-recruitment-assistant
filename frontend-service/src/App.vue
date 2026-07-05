<template>
  <div class="workspace">
    <header class="header">
      <div>
        <h1 class="brand-title">SmartCreditMultiAgent</h1>
        <div class="brand-subtitle">信贷审批辅助工作台</div>
      </div>
      <div class="capability-tags">
        <el-tag effect="plain">CSV批量导入</el-tag>
        <el-tag effect="plain" type="success">Batch AI Review</el-tag>
        <el-tag effect="plain" type="warning">Tool Trace</el-tag>
        <el-tag effect="plain" type="info">Policy RAG</el-tag>
        <el-tag effect="plain" type="danger">Human-in-the-loop</el-tag>
        <el-tag effect="plain">Real LLM Report</el-tag>
      </div>
    </header>

    <div class="layout">
      <aside class="sidebar">
        <div v-for="item in navItems" :key="item.id" class="nav-item" :class="{ active: activeSection === item.id }" @click="activeSection = item.id">
          {{ item.label }}
        </div>
      </aside>

      <main class="main">
        <div class="grid">
          <section class="section-stack">
            <el-card id="import" shadow="never">
              <template #header>
                <div class="toolbar">
                  <strong>CSV 文件上传</strong>
                  <el-tag type="info">手动上传 fixture</el-tag>
                </div>
              </template>

              <el-alert title="请选择仓库内置样例文件" type="info" :closable="false" show-icon>
                <div class="hint">
                  推荐上传项目内置样例：
                  <span class="path-pill">docs/sample_import/loan_applications_sample.csv</span>
                  <br />
                  这模拟上游业务系统或客户经理批量提交信贷申请文件。浏览器不能自动选择本地文件，需要手动选择 CSV 后上传。
                </div>
              </el-alert>

              <div style="height: 14px"></div>
              <el-form label-position="top">
                <el-form-item label="登录区">
                  <div class="toolbar">
                    <el-input v-model="loginForm.username" placeholder="username" style="width: 180px" />
                    <el-input v-model="loginForm.password" placeholder="password" type="password" show-password style="width: 210px" />
                    <el-button @click="handleInitAdmin">初始化 demo admin</el-button>
                    <el-button type="primary" @click="handleLogin">登录</el-button>
                  </div>
                </el-form-item>

                <el-form-item label="选择 CSV 文件">
                  <div class="toolbar">
                    <input ref="fileInputRef" type="file" accept=".csv,text/csv" @change="handleFileChange" />
                    <el-button type="primary" :loading="uploading" @click="handleUploadCsv">上传 CSV 导入</el-button>
                    <el-button @click="handleDownloadTemplate">下载 CSV 模板</el-button>
                  </div>
                </el-form-item>
              </el-form>

              <el-descriptions v-if="importResult" :column="3" border size="small">
                <el-descriptions-item label="totalRows">{{ importResult.totalRows }}</el-descriptions-item>
                <el-descriptions-item label="successCount">{{ importResult.successCount }}</el-descriptions-item>
                <el-descriptions-item label="failedCount">{{ importResult.failedCount }}</el-descriptions-item>
              </el-descriptions>
              <el-alert v-if="importErrors.length" style="margin-top: 12px" title="导入错误" type="warning" :closable="false">
                <div v-for="error in importErrors" :key="error">{{ error }}</div>
              </el-alert>
            </el-card>

            <el-card id="batch" shadow="never">
              <template #header>
                <div class="toolbar">
                  <strong>批量检测进度</strong>
                  <el-button type="success" :disabled="!batchRows.length || batchRunning" :loading="batchRunning" @click="runBatchAiReview">
                    批量 AI 检测上传文件
                  </el-button>
                </div>
              </template>
              <div class="metrics">
                <div class="metric">
                  <div class="metric-label">total</div>
                  <div class="metric-value">{{ batchSummary.total }}</div>
                </div>
                <div class="metric">
                  <div class="metric-label">success</div>
                  <div class="metric-value">{{ batchSummary.success }}</div>
                </div>
                <div class="metric">
                  <div class="metric-label">failed</div>
                  <div class="metric-value">{{ batchSummary.failed }}</div>
                </div>
                <div class="metric">
                  <div class="metric-label">highRiskCount</div>
                  <div class="metric-value">{{ highRiskCount }}</div>
                </div>
              </div>
              <div class="metrics" style="margin-top: 10px">
                <div class="metric">
                  <div class="metric-label">needMoreInfoCount</div>
                  <div class="metric-value">{{ needMoreInfoCount }}</div>
                </div>
                <div class="metric">
                  <div class="metric-label">approveSuggestionCount</div>
                  <div class="metric-value">{{ approveSuggestionCount }}</div>
                </div>
                <div class="metric">
                  <div class="metric-label">rejectSuggestionCount</div>
                  <div class="metric-value">{{ rejectSuggestionCount }}</div>
                </div>
                <div class="metric">
                  <div class="metric-label">progress</div>
                  <div class="metric-value">{{ completedCount }}/{{ batchSummary.total }}</div>
                </div>
              </div>
              <el-progress style="margin-top: 14px" :percentage="progressPercent" />
              <el-alert v-if="batchRunning" style="margin-top: 12px" type="info" :closable="false" show-icon>
                AI Review 正在执行：规则评分、ML baseline、Policy RAG、合规检查和真实 LLM 报告生成中。真实 LLM 可能需要 30-90 秒；批量检测顺序执行，避免并发触发限流。
              </el-alert>
            </el-card>
          </section>

          <section class="section-stack">
            <el-card id="results" shadow="never">
              <template #header>
                <div class="toolbar">
                  <strong>文件内申请检测结果</strong>
                  <el-button @click="refreshApplications">刷新待审列表</el-button>
                </div>
              </template>

              <el-table :data="batchRows" border stripe height="430" @row-click="selectRow">
                <el-table-column prop="applicationId" label="applicationId" width="120" />
                <el-table-column prop="applicantName" label="客户名" min-width="140" />
                <el-table-column prop="amount" label="贷款金额" width="110" />
                <el-table-column prop="termMonths" label="期限" width="80" />
                <el-table-column prop="purpose" label="用途" min-width="180" />
                <el-table-column label="检测状态" width="110">
                  <template #default="{ row }">
                    <el-tag :type="reviewStatusTag(row.reviewStatus)">{{ row.reviewStatus }}</el-tag>
                  </template>
                </el-table-column>
                <el-table-column prop="riskLevel" label="风险等级" width="100" />
                <el-table-column label="AI建议" width="120">
                  <template #default="{ row }">{{ decisionText(row.aiDecision) }}</template>
                </el-table-column>
                <el-table-column label="耗时" width="90">
                  <template #default="{ row }">{{ row.durationMs ? `${row.durationMs}ms` : "-" }}</template>
                </el-table-column>
                <el-table-column label="操作" width="190" fixed="right">
                  <template #default="{ row }">
                    <el-button size="small" @click.stop="selectRow(row)">查看详情</el-button>
                    <el-button size="small" type="primary" :disabled="batchRunning || isTerminal(row.status)" @click.stop="reviewOne(row)">重新检测本条</el-button>
                  </template>
                </el-table-column>
              </el-table>
            </el-card>
          </section>

          <section id="detail" class="full-width">
            <el-card shadow="never">
              <template #header>
                <div class="toolbar">
                  <strong>申请详情</strong>
                  <el-tag v-if="selectedRow">{{ statusText(selectedRow.status) }}</el-tag>
                  <el-tag v-if="selectedRow?.workflowId" type="success">workflowId: {{ selectedRow.workflowId }}</el-tag>
                </div>
              </template>

              <div v-if="!selectedRow" class="empty">请选择一条申请查看完整报告、Agent Trace、Tool Calls 和 Policy References。</div>
              <div v-else class="detail-panel">
                <div class="detail-grid">
                  <div class="kv">
                    <div class="kv-label">客户/申请</div>
                    <div class="kv-value">{{ selectedRow.applicantName }} / #{{ selectedRow.applicationId }}</div>
                  </div>
                  <div class="kv">
                    <div class="kv-label">风险评分</div>
                    <div class="kv-value">{{ selectedRow.riskScore ?? "-" }} / {{ selectedRow.riskLevel || "-" }}</div>
                  </div>
                  <div class="kv">
                    <div class="kv-label">AI Summary</div>
                    <div class="kv-value">{{ selectedRow.summary || "待检测" }}</div>
                  </div>
                  <div class="kv">
                    <div class="kv-label">suggestedAmount / finalDecision</div>
                    <div class="kv-value">{{ selectedRow.suggestedAmount ?? "-" }} / {{ decisionText(selectedRow.aiDecision) }}</div>
                  </div>
                </div>

                <el-tabs v-model="detailTab">
                  <el-tab-pane label="Agent Trace" name="trace">
                    <div v-if="!agentTimeline.length" class="empty">尚无 Agent Trace。当前路径未进入 SeniorReviewAgent，这是正常条件分支。</div>
                    <div v-for="agent in agentTimeline" :key="agent.agentName" class="timeline-card">
                      <strong>{{ agent.agentName }}</strong>
                      <el-tag style="margin-left: 8px" :type="agent.status === 'SUCCESS' ? 'success' : 'warning'">{{ agent.status || "-" }}</el-tag>
                      <div class="tool-meta">
                        <span>duration: {{ formatDuration(agent.durationMs) }}</span>
                        <span>inputSummary: {{ agent.inputSummary || "-" }}</span>
                      </div>
                      <div class="hint">outputSummary: {{ agent.outputSummary || "该 Agent 暂无输出摘要，但状态已记录。" }}</div>
                    </div>
                    <el-alert v-if="!hasSeniorReview" type="info" :closable="false">
                      当前路径未进入 SeniorReviewAgent，这是正常条件分支。
                    </el-alert>
                  </el-tab-pane>

                  <el-tab-pane label="Tool Calls" name="tools">
                    <div v-if="!toolCalls.length" class="empty">暂无 Tool Calls。</div>
                    <div v-for="(tool, index) in toolCalls" :key="`${tool.toolName}-${index}`" class="tool-card">
                      <strong>{{ tool.toolName }}</strong>
                      <div class="hint">{{ toolDescription(tool.toolName) }}</div>
                      <div class="tool-meta">
                        <span>status: {{ tool.status || "-" }}</span>
                        <span>duration: {{ formatDuration(tool.durationMs) }}</span>
                        <span>inputSummary: {{ tool.inputSummary || "-" }}</span>
                        <span>outputSummary: {{ tool.outputSummary || "-" }}</span>
                      </div>
                      <div v-if="tool.errorMessage" class="danger-note">error: {{ tool.errorMessage }}</div>
                    </div>
                  </el-tab-pane>

                  <el-tab-pane label="Policy References" name="policy">
                    <div v-if="!policyReferences.length" class="empty">暂无 Policy References。</div>
                    <div v-for="policy in policyReferences" :key="policy.policyCode || policy.code || policy.title" class="policy-card">
                      <strong>{{ policy.policyCode || policy.code || "Policy" }}</strong>
                      <div class="hint">{{ policy.title || policy.chunkText || policy.content || policy.text }}</div>
                    </div>
                  </el-tab-pane>

                  <el-tab-pane label="人工审批" name="approval">
                    <div class="toolbar">
                      <el-button type="success" :disabled="!canFinalApprove" @click="handleManualApprove">人工通过</el-button>
                      <el-button type="danger" :disabled="!canFinalApprove" @click="handleManualReject">人工拒绝</el-button>
                      <el-button type="warning" :disabled="!canNeedMoreInfo" @click="handleManualNeedMoreInfo">要求补件</el-button>
                    </div>
                    <el-alert v-if="isTerminal(selectedRow.status)" style="margin-top: 12px" type="warning" :closable="false">
                      该申请已完成最终人工审批，不能继续补件或重复审批。
                    </el-alert>
                    <el-input v-model="manualComment" style="margin-top: 12px" type="textarea" :rows="3" placeholder="人工审批备注" />
                    <div class="toolbar" style="margin-top: 12px">
                      <el-input v-model="materialSummary" placeholder="补件摘要" style="width: 420px" />
                      <el-button @click="handleUpdateMaterials">提交补件摘要</el-button>
                      <el-button type="primary" @click="handleResubmit">重新提交</el-button>
                    </div>
                    <el-divider />
                    <div class="hint">审批历史：{{ approvalHistory.length }} 条；补件记录：{{ materialUpdates.length }} 条。</div>
                  </el-tab-pane>
                </el-tabs>
              </div>
            </el-card>
          </section>
        </div>
      </main>
    </div>
  </div>
</template>

<script setup>
import { computed, ref } from "vue";
import { ElMessage } from "element-plus";
import {
  aiReview,
  downloadCsvTemplate,
  getAgentLogs,
  getAiReports,
  getApplication,
  getApprovalHistory,
  getMaterialUpdates,
  initAdmin,
  listApplications,
  login,
  manualApprove,
  manualNeedMoreInfo,
  manualReject,
  resubmit,
  updateMaterials,
  uploadCsv
} from "./api.js";

const navItems = [
  { id: "import", label: "文件导入" },
  { id: "batch", label: "批量检测结果" },
  { id: "detail", label: "申请详情" },
  { id: "trace", label: "Agent Trace" },
  { id: "approval", label: "人工审批" }
];

const activeSection = ref("import");
const loginForm = ref({ username: "admin", password: "Admin@123456" });
const selectedFile = ref(null);
const fileInputRef = ref(null);
const uploading = ref(false);
const batchRunning = ref(false);
const importResult = ref(null);
const importErrors = ref([]);
const batchRows = ref([]);
const selectedRow = ref(null);
const detailTab = ref("trace");
const approvalHistory = ref([]);
const materialUpdates = ref([]);
const manualComment = ref("manual decision after checking AI report and Agent Trace");
const materialSummary = ref("补充近 6 个月收入流水和资产证明摘要");

const batchSummary = computed(() => ({
  total: batchRows.value.length,
  success: batchRows.value.filter((row) => row.reviewStatus === "检测完成").length,
  failed: batchRows.value.filter((row) => row.reviewStatus === "检测失败").length
}));
const completedCount = computed(() => batchSummary.value.success + batchSummary.value.failed);
const progressPercent = computed(() => (batchSummary.value.total ? Math.round((completedCount.value / batchSummary.value.total) * 100) : 0));
const highRiskCount = computed(() => batchRows.value.filter((row) => row.riskLevel === "HIGH").length);
const needMoreInfoCount = computed(() => batchRows.value.filter((row) => row.aiDecision === "NEED_MORE_INFO").length);
const approveSuggestionCount = computed(() => batchRows.value.filter((row) => row.aiDecision === "APPROVE").length);
const rejectSuggestionCount = computed(() => batchRows.value.filter((row) => row.aiDecision === "REJECT").length);
const normalizedAgentResults = computed(() => normalizeAgentResults(selectedRow.value?.agentResults || []));
const agentTimeline = computed(() => normalizedAgentResults.value);
const hasSeniorReview = computed(() => agentTimeline.value.some((agent) => agent.agentName === "SeniorReviewAgent"));
const toolCalls = computed(() => agentTimeline.value.flatMap((agent) => agent.toolCalls));
const policyReferences = computed(() => selectedRow.value?.policyReferences || []);
const canFinalApprove = computed(() => selectedRow.value?.status === "AI_REVIEWED");
const canNeedMoreInfo = computed(() => ["SUBMITTED", "RESUBMITTED", "AI_REVIEWED"].includes(selectedRow.value?.status));

async function handleInitAdmin() {
  try {
    await initAdmin();
    ElMessage.success("demo admin 已初始化");
  } catch (error) {
    ElMessage.info(`初始化返回：${error.message}`);
  }
}

async function handleLogin() {
  await login(loginForm.value.username, loginForm.value.password);
  ElMessage.success("登录成功");
}

function handleFileChange(event) {
  selectedFile.value = event.target.files?.[0] || null;
}

async function handleDownloadTemplate() {
  await downloadCsvTemplate();
  ElMessage.success("CSV 模板已开始下载");
}

async function handleUploadCsv() {
  if (!selectedFile.value) {
    ElMessage.warning("请先选择 CSV 文件");
    return;
  }
  uploading.value = true;
  try {
    const result = await uploadCsv(selectedFile.value);
    importResult.value = result;
    importErrors.value = result?.errors || [];
    batchRows.value = (result?.imported || []).map((item) => ({
      ...item,
      id: item.applicationId,
      reviewStatus: "待检测",
      status: item.status || "SUBMITTED",
      aiDecision: "",
      riskLevel: "",
      summary: "",
      durationMs: 0,
      workflowId: "",
      agentResults: [],
      policyReferences: []
    }));
    selectedRow.value = batchRows.value[0] || null;
    await refreshApplications();
    ElMessage.success("CSV 导入完成，可开始批量 AI 检测");
  } finally {
    uploading.value = false;
  }
}

async function refreshApplications() {
  const page = await listApplications(1, 20);
  const records = page?.records || [];
  for (const row of batchRows.value) {
    const latest = records.find((item) => String(item.id) === String(row.applicationId));
    if (latest) {
      row.status = latest.status;
      row.riskLevel = latest.riskLevel || row.riskLevel;
      row.aiDecision = latest.aiDecision || row.aiDecision;
    }
  }
}

async function runBatchAiReview() {
  batchRunning.value = true;
  try {
    for (const row of batchRows.value) {
      if (isTerminal(row.status)) {
        row.reviewStatus = "检测失败";
        row.error = "终态申请不可批量重跑 AI 检测";
        continue;
      }
      await reviewOne(row);
    }
    ElMessage.success("批量 AI 检测完成");
  } finally {
    batchRunning.value = false;
  }
}

async function reviewOne(row) {
  if (isTerminal(row.status)) {
    ElMessage.warning("终态申请不可批量重跑 AI 检测");
    return;
  }
  row.reviewStatus = "检测中";
  row.error = "";
  const startedAt = performance.now();
  try {
    const result = await aiReview(row.applicationId);
    row.durationMs = Math.round(performance.now() - startedAt);
    row.reviewStatus = "检测完成";
    row.workflowId = result.workflow_id || result.workflowId;
    row.aiDecision = result.final_decision || result.finalDecision;
    row.riskLevel = result.risk_level || result.riskLevel;
    row.riskScore = result.risk_score ?? result.riskScore;
    row.suggestedAmount = result.suggested_amount ?? result.suggestedAmount;
    row.summary = result.summary;
    row.agentResults = result.agent_results || result.agentResults || [];
    row.policyReferences = extractPolicyReferences(result);
    row.status = "AI_REVIEWED";
    selectedRow.value = row;
    await selectRow(row);
    await refreshApplications();
  } catch (error) {
    row.durationMs = Math.round(performance.now() - startedAt);
    row.reviewStatus = "检测失败";
    row.error = error.message;
    ElMessage.error(`申请 ${row.applicationId} AI 检测失败：${error.message}`);
  }
}

async function selectRow(row) {
  selectedRow.value = row;
  detailTab.value = "trace";
  try {
    const latest = await getApplication(row.applicationId);
    row.status = latest.status || row.status;
    const reports = await getAiReports(row.applicationId);
    const latestReport = Array.isArray(reports) ? reports[0] : null;
    if (latestReport?.reportJson) {
      const reportJson = JSON.parse(latestReport.reportJson);
      row.policyReferences = reportJson.policy_references || reportJson.policyReferences || row.policyReferences || [];
    }
    const logs = await getAgentLogs(row.workflowId || row.applicationId, Boolean(row.workflowId));
    if (!row.agentResults?.length) {
      row.agentResults = normalizeLogs(logs);
    }
    approvalHistory.value = await getApprovalHistory(row.applicationId);
    materialUpdates.value = await getMaterialUpdates(row.applicationId);
  } catch (error) {
    ElMessage.warning(`详情刷新失败：${error.message}`);
  }
}

async function handleManualApprove() {
  const updated = await manualApprove(selectedRow.value.applicationId, manualComment.value);
  selectedRow.value.status = updated.status || "APPROVED";
  ElMessage.success("人工通过已完成");
}

async function handleManualReject() {
  const updated = await manualReject(selectedRow.value.applicationId, manualComment.value);
  selectedRow.value.status = updated.status || "REJECTED";
  ElMessage.success("人工拒绝已完成");
}

async function handleManualNeedMoreInfo() {
  const updated = await manualNeedMoreInfo(selectedRow.value.applicationId, manualComment.value);
  selectedRow.value.status = updated.status || "NEED_MORE_INFO";
  ElMessage.success("已要求补件");
}

async function handleUpdateMaterials() {
  const updated = await updateMaterials(selectedRow.value.applicationId, materialSummary.value);
  selectedRow.value.status = updated.status || "MATERIAL_UPDATED";
  materialUpdates.value = await getMaterialUpdates(selectedRow.value.applicationId);
  ElMessage.success("提交补件摘要完成");
}

async function handleResubmit() {
  const updated = await resubmit(selectedRow.value.applicationId);
  selectedRow.value.status = updated.status || "RESUBMITTED";
  ElMessage.success("重新提交完成，可再次 AI 检测");
}

function extractPolicyReferences(result) {
  const report = result.report || {};
  return report.policy_references || report.policyReferences || [];
}

function normalizeLogs(logs) {
  return (logs || []).map((log) =>
    normalizeAgentResult({
      agentName: log.agentName || log.agent_name || log.name,
      status: log.status,
      inputSummary: log.inputSummary || log.input_summary || "",
      outputSummary: log.outputSummary || log.output_summary || log.summary || log.inputSummary || log.input_summary || "",
      startedAt: log.startedAt || log.started_at || "",
      endedAt: log.endedAt || log.ended_at || "",
      durationMs: log.durationMs ?? log.duration_ms ?? "",
      result: log.result || {}
    })
  );
}

function normalizeAgentResults(agentResults) {
  return (agentResults || []).map(normalizeAgentResult);
}

function normalizeAgentResult(agent) {
  const result = normalizeResult(agent.result);
  return {
    agentName: agent.agentName || agent.agent_name || agent.name || "Agent",
    status: agent.status || "-",
    inputSummary: agent.inputSummary || agent.input_summary || "",
    outputSummary: agent.outputSummary || agent.output_summary || agent.summary || "",
    startedAt: agent.startedAt || agent.started_at || "",
    endedAt: agent.endedAt || agent.ended_at || "",
    durationMs: agent.durationMs ?? agent.duration_ms ?? "",
    result,
    toolCalls: normalizeToolCalls(agent.toolCalls || agent.tool_calls || result.tool_calls || result.toolCalls || [])
  };
}

function normalizeResult(result) {
  if (!result) {
    return {};
  }
  if (typeof result === "string") {
    try {
      return JSON.parse(result);
    } catch {
      return {};
    }
  }
  return result;
}

function normalizeToolCalls(tools) {
  return (tools || []).map(normalizeToolCall);
}

function normalizeToolCall(tool) {
  return {
    toolName: tool.toolName || tool.tool_name || tool.name || "Tool",
    status: tool.status || "-",
    durationMs: tool.durationMs ?? tool.duration_ms ?? tool.duration ?? "",
    inputSummary: tool.inputSummary || tool.input_summary || "",
    outputSummary: tool.outputSummary || tool.output_summary || "",
    errorMessage: tool.errorMessage || tool.error_message || tool.error || ""
  };
}

function formatDuration(duration) {
  if (duration === undefined || duration === null || duration === "") {
    return "-";
  }
  if (typeof duration === "string" && /ms$|s$/i.test(duration)) {
    return duration;
  }
  return `${duration}ms`;
}

function isTerminal(status) {
  return ["APPROVED", "REJECTED"].includes(status);
}

function statusText(status) {
  return {
    SUBMITTED: "待 AI 预审",
    AI_REVIEWED: "AI 已预审",
    NEED_MORE_INFO: "要求补件",
    MATERIAL_UPDATED: "已补件",
    RESUBMITTED: "已重提",
    APPROVED: "人工通过",
    REJECTED: "人工拒绝"
  }[status] || status || "-";
}

function decisionText(decision) {
  return {
    APPROVE: "建议通过",
    REJECT: "建议拒绝",
    NEED_MORE_INFO: "建议补件"
  }[decision] || decision || "-";
}

function reviewStatusTag(status) {
  return {
    待检测: "info",
    检测中: "warning",
    检测完成: "success",
    检测失败: "danger"
  }[status] || "info";
}

function toolDescription(name) {
  return {
    MaterialChecklistTool: "材料完整性检查工具",
    RiskRuleTool: "规则评分工具",
    RiskModelTool: "ML baseline 风险模型工具",
    PolicySearchTool: "Policy RAG 制度检索工具",
    ComplianceGuardrailTool: "合规护栏检查工具",
    SeniorReviewChecklistTool: "高风险高级复核清单工具",
    ReportGenerationTool: "真实 LLM 报告生成工具"
  }[name] || "Agent 工具调用";
}
</script>
