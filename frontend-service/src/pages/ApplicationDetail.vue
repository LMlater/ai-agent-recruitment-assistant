<template>
  <section class="detail-shell">
    <div class="detail-topbar">
      <el-button @click="router.push('/workspace#results')">返回工作台</el-button>
      <div>
        <p class="eyebrow">Application #{{ applicationId }}</p>
        <h2>单笔申请详情</h2>
      </div>
      <div class="detail-status">
        <el-tag>{{ statusText(application?.status) }}</el-tag>
        <el-tag v-if="workflowId" type="success">workflowId: {{ workflowId }}</el-tag>
      </div>
    </div>

    <el-skeleton v-if="loading" :rows="8" animated />

    <template v-else>
      <div class="detail-overview">
        <el-card shadow="never">
          <template #header><strong>客户和贷款申请概览</strong></template>
          <div class="kv-grid">
            <div class="kv">
              <span>客户姓名</span>
              <strong>{{ application?.applicantName || application?.customerName || "-" }}</strong>
            </div>
            <div class="kv">
              <span>申请编号 / 客户编号</span>
              <strong>#{{ applicationId }} / {{ application?.customerId || "-" }}</strong>
            </div>
            <div class="kv">
              <span>贷款金额</span>
              <strong>{{ formatMoney(application?.amount) }}</strong>
            </div>
            <div class="kv">
              <span>贷款用途</span>
              <strong>{{ application?.purpose || "-" }}</strong>
            </div>
          </div>
        </el-card>

        <el-card shadow="never">
          <template #header><strong>AI Summary</strong></template>
          <p class="summary-text">{{ latestReport.summary || application?.summary || "暂无 AI 摘要，请先在工作台执行 AI 检测。" }}</p>
          <div class="score-row">
            <div>
              <span>风险评分</span>
              <strong>{{ latestReport.riskScore ?? application?.riskScore ?? "-" }}</strong>
            </div>
            <div>
              <span>风险等级</span>
              <strong>{{ latestReport.riskLevel || application?.riskLevel || "-" }}</strong>
            </div>
            <div>
              <span>AI 建议</span>
              <strong>{{ decisionText(latestReport.aiDecision || application?.aiDecision) }}</strong>
            </div>
          </div>
        </el-card>
      </div>

      <el-tabs v-model="activeTab" class="detail-tabs" @tab-change="syncTabToQuery">
        <el-tab-pane label="AI 报告" name="summary">
          <pre class="json-block">{{ reportText }}</pre>
        </el-tab-pane>

        <el-tab-pane label="Agent Trace" name="trace">
          <div v-if="!agentTimeline.length" class="empty">暂无 Agent Trace。当前路径未进入 SeniorReviewAgent 时，这是正常条件分支。</div>
          <div v-for="agent in agentTimeline" :key="agent.agentName" class="timeline-card">
            <strong>{{ agent.agentName }}</strong>
            <el-tag class="inline-tag" :type="agent.status === 'SUCCESS' ? 'success' : 'warning'">{{ agent.status || "-" }}</el-tag>
            <div class="tool-meta">
              <span>duration: {{ formatDuration(agent.durationMs) }}</span>
              <span>inputSummary: {{ agent.inputSummary || "-" }}</span>
              <span>outputSummary: {{ agent.outputSummary || "-" }}</span>
            </div>
          </div>
        </el-tab-pane>

        <el-tab-pane label="Tool Calls" name="tools">
          <div v-if="!toolCalls.length" class="empty">暂无 Tool Calls。</div>
          <div v-for="(tool, index) in toolCalls" :key="`${tool.toolName}-${index}`" class="tool-card">
            <strong>{{ tool.toolName }}</strong>
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

        <el-tab-pane label="审批历史" name="history">
          <div v-if="!approvalHistory.length" class="empty">暂无审批历史。</div>
          <el-timeline v-else>
            <el-timeline-item v-for="item in approvalHistory" :key="item.id || item.createdAt" :timestamp="item.createdAt">
              <strong>{{ item.action || item.status }}</strong>
              <div class="hint">{{ item.comment || "-" }}</div>
            </el-timeline-item>
          </el-timeline>
        </el-tab-pane>

        <el-tab-pane label="补件复审" name="materials">
          <div v-if="!materialUpdates.length" class="empty">暂无补件记录。</div>
          <div v-for="item in materialUpdates" :key="item.id || item.createdAt" class="policy-card">
            <strong>{{ item.status || "材料更新" }}</strong>
            <div class="hint">{{ item.materialSummary || item.summary || "-" }}</div>
          </div>
          <div class="toolbar top-gap">
            <el-input v-model="materialSummary" placeholder="补件摘要" class="wide-input" />
            <el-button @click="handleUpdateMaterials">提交补件摘要</el-button>
            <el-button type="primary" @click="handleResubmit">重新提交</el-button>
          </div>
        </el-tab-pane>

        <el-tab-pane label="人工审批" name="approval">
          <div class="approval-panel">
            <el-alert title="AI 不自动终审" type="warning" :closable="false" show-icon>
              最终 APPROVED / REJECTED / NEED_MORE_INFO 必须由人工确认。
            </el-alert>
            <div class="toolbar top-gap">
              <el-button type="success" :disabled="!canFinalApprove" @click="handleManualApprove">人工通过</el-button>
              <el-button type="danger" :disabled="!canFinalApprove" @click="handleManualReject">人工拒绝</el-button>
              <el-button type="warning" :disabled="!canNeedMoreInfo" @click="handleManualNeedMoreInfo">要求补件</el-button>
            </div>
            <el-input v-model="manualComment" class="top-gap" type="textarea" :rows="3" placeholder="人工审批备注" />
          </div>
        </el-tab-pane>
      </el-tabs>
    </template>
  </section>
</template>

<script setup>
import { computed, onMounted, ref, watch } from "vue";
import { useRoute, useRouter } from "vue-router";
import { ElMessage } from "element-plus";
import {
  getAgentLogs,
  getAiReports,
  getApplication,
  getApprovalHistory,
  getMaterialUpdates,
  manualApprove,
  manualNeedMoreInfo,
  manualReject,
  resubmit,
  updateMaterials
} from "../api.js";

const CURRENT_APPLICATION_ID_KEY = "smartcredit.frontend.currentApplicationId";
const route = useRoute();
const router = useRouter();
const applicationId = computed(() => route.params.applicationId);
const loading = ref(false);
const activeTab = ref("summary");
const application = ref(null);
const reports = ref([]);
const logs = ref([]);
const approvalHistory = ref([]);
const materialUpdates = ref([]);
const manualComment = ref("manual decision after checking AI report and Agent Trace");
const materialSummary = ref("补充近 6 个月收入流水和资产证明摘要");

const latestReport = computed(() => normalizeReport(reports.value[0]));
const workflowId = computed(() => latestReport.value.workflowId || application.value?.workflowId || "");
const agentTimeline = computed(() => normalizeLogs(logs.value));
const toolCalls = computed(() => agentTimeline.value.flatMap((agent) => agent.toolCalls));
const policyReferences = computed(() => latestReport.value.policyReferences || []);
const canFinalApprove = computed(() => application.value?.status === "AI_REVIEWED");
const canNeedMoreInfo = computed(() => ["SUBMITTED", "RESUBMITTED", "AI_REVIEWED"].includes(application.value?.status));
const reportText = computed(() => (reports.value[0] ? JSON.stringify(reports.value[0], null, 2) : "暂无 AI 报告"));

onMounted(loadDetail);

watch(
  () => route.query.tab,
  (tab) => {
    activeTab.value = normalizeTab(tab);
  },
  { immediate: true }
);

async function loadDetail() {
  loading.value = true;
  try {
    await fetchApplicationDetail(applicationId.value);
  } finally {
    loading.value = false;
  }
}

async function fetchApplicationDetail(applicationId) {
  localStorage.setItem(CURRENT_APPLICATION_ID_KEY, String(applicationId));
  application.value = await getApplication(applicationId);
  reports.value = await getAiReports(applicationId);
  const latestWorkflowId = workflowId.value;
  logs.value = await getAgentLogs(latestWorkflowId || applicationId, Boolean(latestWorkflowId));
  approvalHistory.value = await getApprovalHistory(applicationId);
  materialUpdates.value = await getMaterialUpdates(applicationId);
}

function syncTabToQuery(tab) {
  router.replace({ path: route.path, query: tab === "summary" ? {} : { tab } });
}

function normalizeTab(tab) {
  const allowed = ["summary", "trace", "tools", "policy", "history", "materials", "approval"];
  return allowed.includes(tab) ? tab : "summary";
}

function normalizeReport(report) {
  if (!report) {
    return {};
  }
  const parsed = parseJson(report.reportJson) || report.report || report;
  return {
    summary: parsed.summary || report.summary,
    riskScore: parsed.risk_score ?? parsed.riskScore ?? report.riskScore,
    riskLevel: parsed.risk_level || parsed.riskLevel || report.riskLevel,
    aiDecision: parsed.final_decision || parsed.finalDecision || parsed.aiDecision || report.aiDecision,
    workflowId: parsed.workflow_id || parsed.workflowId || report.workflowId,
    policyReferences: parsed.policy_references || parsed.policyReferences || []
  };
}

function normalizeLogs(items) {
  return (items || []).map((item) => {
    const result = parseJson(item.result) || item.result || {};
    return {
      agentName: item.agentName || item.agent_name || item.name || "Agent",
      status: item.status,
      inputSummary: item.inputSummary || item.input_summary || "",
      outputSummary: item.outputSummary || item.output_summary || item.summary || "",
      durationMs: item.durationMs ?? item.duration_ms ?? "",
      toolCalls: normalizeToolCalls(item.toolCalls || item.tool_calls || result.tool_calls || result.toolCalls || [])
    };
  });
}

function normalizeToolCalls(items) {
  return (items || []).map((item) => ({
    toolName: item.toolName || item.tool_name || item.name || "Tool",
    status: item.status || "-",
    durationMs: item.durationMs ?? item.duration_ms ?? item.duration ?? "",
    inputSummary: item.inputSummary || item.input_summary || "",
    outputSummary: item.outputSummary || item.output_summary || "",
    errorMessage: item.errorMessage || item.error_message || item.error || ""
  }));
}

function parseJson(value) {
  if (!value || typeof value !== "string") {
    return null;
  }
  try {
    return JSON.parse(value);
  } catch {
    return null;
  }
}

async function handleManualApprove() {
  const updated = await manualApprove(applicationId.value, manualComment.value);
  application.value.status = updated.status || "APPROVED";
  approvalHistory.value = await getApprovalHistory(applicationId.value);
  ElMessage.success("人工通过已完成");
}

async function handleManualReject() {
  const updated = await manualReject(applicationId.value, manualComment.value);
  application.value.status = updated.status || "REJECTED";
  approvalHistory.value = await getApprovalHistory(applicationId.value);
  ElMessage.success("人工拒绝已完成");
}

async function handleManualNeedMoreInfo() {
  const updated = await manualNeedMoreInfo(applicationId.value, manualComment.value);
  application.value.status = updated.status || "NEED_MORE_INFO";
  approvalHistory.value = await getApprovalHistory(applicationId.value);
  ElMessage.success("已要求补件");
}

async function handleUpdateMaterials() {
  const updated = await updateMaterials(applicationId.value, materialSummary.value);
  application.value.status = updated.status || "MATERIAL_UPDATED";
  materialUpdates.value = await getMaterialUpdates(applicationId.value);
  ElMessage.success("提交补件摘要完成");
}

async function handleResubmit() {
  const updated = await resubmit(applicationId.value);
  application.value.status = updated.status || "RESUBMITTED";
  ElMessage.success("重新提交完成，可回到工作台再次 AI 检测");
}

function formatDuration(duration) {
  if (duration === undefined || duration === null || duration === "") {
    return "-";
  }
  return typeof duration === "string" && /ms$|s$/i.test(duration) ? duration : `${duration}ms`;
}

function formatMoney(value) {
  if (value === undefined || value === null || value === "") {
    return "-";
  }
  return Number(value).toLocaleString("zh-CN");
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
</script>
