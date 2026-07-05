<template>
  <section class="workspace-page">
    <div class="page-heading">
      <div>
        <p class="eyebrow">Workspace</p>
        <h2>批量导入与 AI 检测</h2>
      </div>
      <el-button @click="refreshApplications">刷新待审列表</el-button>
    </div>

    <div class="workspace-grid">
      <section class="section-stack">
        <el-card id="import" shadow="never">
          <template #header>
            <div class="toolbar">
              <strong>CSV 文件上传</strong>
              <el-tag type="info">推荐样例：docs/sample_import/loan_applications_sample.csv</el-tag>
            </div>
          </template>

          <el-alert title="请选择仓库内置样例文件" type="info" :closable="false" show-icon>
            <div class="hint">
              浏览器不能自动选择本地文件，请手动选择 CSV 后上传。导入成功后，工作台会保存本次批量结果，刷新页面也可恢复。
            </div>
          </el-alert>

          <div class="upload-row">
            <input ref="fileInputRef" type="file" accept=".csv,text/csv" @change="handleFileChange" />
            <el-button type="primary" :loading="uploading" @click="handleUploadCsv">上传 CSV 导入</el-button>
            <el-button @click="handleDownloadTemplate">下载 CSV 模板</el-button>
          </div>

          <el-descriptions v-if="importResult" :column="3" border size="small">
            <el-descriptions-item label="总行数">{{ importResult.totalRows }}</el-descriptions-item>
            <el-descriptions-item label="成功">{{ importResult.successCount }}</el-descriptions-item>
            <el-descriptions-item label="失败">{{ importResult.failedCount }}</el-descriptions-item>
          </el-descriptions>

          <el-alert v-if="importErrors.length" class="top-gap" title="导入错误" type="warning" :closable="false">
            <div v-for="error in importErrors" :key="error">{{ error }}</div>
          </el-alert>
        </el-card>

        <el-card id="batch" shadow="never">
          <template #header>
            <div class="toolbar between">
              <strong>批量检测进度</strong>
              <el-button type="success" :disabled="!batchRows.length || batchRunning" :loading="batchRunning" @click="runBatchAiReview">
                批量 AI 检测上传文件
              </el-button>
            </div>
          </template>

          <div class="metrics">
            <div class="metric">
              <div class="metric-label">总数</div>
              <div class="metric-value">{{ batchSummary.total }}</div>
            </div>
            <div class="metric">
              <div class="metric-label">完成</div>
              <div class="metric-value">{{ batchSummary.success }}</div>
            </div>
            <div class="metric">
              <div class="metric-label">失败</div>
              <div class="metric-value">{{ batchSummary.failed }}</div>
            </div>
            <div class="metric">
              <div class="metric-label">高风险</div>
              <div class="metric-value">{{ highRiskCount }}</div>
            </div>
          </div>

          <div class="metrics compact">
            <div class="metric">
              <div class="metric-label">建议补件</div>
              <div class="metric-value">{{ needMoreInfoCount }}</div>
            </div>
            <div class="metric">
              <div class="metric-label">建议通过</div>
              <div class="metric-value">{{ approveSuggestionCount }}</div>
            </div>
            <div class="metric">
              <div class="metric-label">建议拒绝</div>
              <div class="metric-value">{{ rejectSuggestionCount }}</div>
            </div>
            <div class="metric">
              <div class="metric-label">进度</div>
              <div class="metric-value">{{ completedCount }}/{{ batchSummary.total }}</div>
            </div>
          </div>

          <el-progress class="top-gap" :percentage="progressPercent" />
          <el-alert v-if="batchRunning" class="top-gap" type="info" :closable="false" show-icon>
            AI Review 正在顺序执行：规则评分、ML baseline、Policy RAG、合规检查和真实 LLM 报告生成。真实 LLM 可能需要 30-90 秒；批量检测不并发调用。
          </el-alert>
        </el-card>
      </section>

      <section id="results" class="results-panel">
        <el-card shadow="never">
          <template #header>
            <div class="toolbar between">
              <strong>文件内申请检测结果</strong>
              <span class="hint">点击“查看详情”进入独立申请页</span>
            </div>
          </template>

          <el-table :data="batchRows" border stripe height="520" class="result-table" @row-click="selectRow">
            <el-table-column label="申请编号 / 客户编号" min-width="160">
              <template #default="{ row }">
                <strong>#{{ row.applicationId }}</strong>
                <div class="muted">客户：{{ row.customerId || "-" }}</div>
              </template>
            </el-table-column>
            <el-table-column prop="applicantName" label="客户姓名" min-width="120" />
            <el-table-column label="贷款金额" width="110">
              <template #default="{ row }">{{ formatMoney(row.amount) }}</template>
            </el-table-column>
            <el-table-column prop="termMonths" label="期限(月)" width="90" />
            <el-table-column label="贷款用途" min-width="180">
              <template #default="{ row }">
                <span class="ellipsis" :title="row.purpose">{{ row.purpose || "-" }}</span>
              </template>
            </el-table-column>
            <el-table-column label="检测状态" width="120">
              <template #default="{ row }">
                <el-tag :type="reviewStatusTag(row.reviewStatus)">{{ row.reviewStatus }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="riskLevel" label="风险等级" width="100" />
            <el-table-column label="AI 建议" width="120">
              <template #default="{ row }">{{ decisionText(row.aiDecision) }}</template>
            </el-table-column>
            <el-table-column label="耗时" width="90">
              <template #default="{ row }">{{ row.durationMs ? `${row.durationMs}ms` : "-" }}</template>
            </el-table-column>
            <el-table-column label="操作" width="210" fixed="right">
              <template #default="{ row }">
                <el-button size="small" @click.stop="goToDetail(row)">查看详情</el-button>
                <el-button size="small" type="primary" :disabled="batchRunning || isTerminal(row.status)" @click.stop="reviewOne(row)">
                  重新检测本条
                </el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </section>
    </div>
  </section>
</template>

<script setup>
import { computed, nextTick, onMounted, ref, watch } from "vue";
import { useRoute, useRouter } from "vue-router";
import { ElMessage } from "element-plus";
import {
  aiReview,
  downloadCsvTemplate,
  listApplications,
  uploadCsv
} from "../api.js";

const LAST_BATCH_ROWS_KEY = "smartcredit.frontend.lastBatchRows";
const CURRENT_APPLICATION_ID_KEY = "smartcredit.frontend.currentApplicationId";

const router = useRouter();
const route = useRoute();
const selectedFile = ref(null);
const uploading = ref(false);
const batchRunning = ref(false);
const importResult = ref(null);
const importErrors = ref([]);
const batchRows = ref([]);

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

onMounted(() => {
  batchRows.value = loadLastBatchRows();
  scrollToRouteHash();
});

watch(
  () => route.hash,
  () => scrollToRouteHash()
);

function saveLastBatchRows() {
  localStorage.setItem(LAST_BATCH_ROWS_KEY, JSON.stringify(batchRows.value));
}

function loadLastBatchRows() {
  try {
    const raw = localStorage.getItem(LAST_BATCH_ROWS_KEY);
    return raw ? JSON.parse(raw) : [];
  } catch {
    return [];
  }
}

function scrollToRouteHash() {
  if (!route.hash) {
    return;
  }
  nextTick(() => {
    document.getElementById(route.hash.replace("#", ""))?.scrollIntoView({ behavior: "smooth" });
  });
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
    if (batchRows.value[0]?.applicationId) {
      localStorage.setItem(CURRENT_APPLICATION_ID_KEY, String(batchRows.value[0].applicationId));
    }
    saveLastBatchRows();
    await refreshApplications();
    ElMessage.success("CSV 导入完成，可开始批量 AI 检测");
  } finally {
    uploading.value = false;
  }
}

async function refreshApplications() {
  if (!batchRows.value.length) {
    return;
  }
  const page = await listApplications(1, 50);
  const records = page?.records || [];
  for (const row of batchRows.value) {
    const latest = records.find((item) => String(item.id) === String(row.applicationId));
    if (latest) {
      row.status = latest.status;
      row.riskLevel = latest.riskLevel || row.riskLevel;
      row.aiDecision = latest.aiDecision || row.aiDecision;
    }
  }
  saveLastBatchRows();
}

async function runBatchAiReview() {
  batchRunning.value = true;
  try {
    for (const row of batchRows.value) {
      if (isTerminal(row.status)) {
        row.reviewStatus = "检测失败";
        row.error = "终态申请不可批量重跑 AI 检测";
        saveLastBatchRows();
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
    ElMessage.warning("终态申请不可重新检测");
    return;
  }
  row.reviewStatus = "检测中";
  row.error = "";
  saveLastBatchRows();
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
    localStorage.setItem(CURRENT_APPLICATION_ID_KEY, String(row.applicationId));
    await refreshApplications();
    saveLastBatchRows();
  } catch (error) {
    row.durationMs = Math.round(performance.now() - startedAt);
    row.reviewStatus = "检测失败";
    row.error = error.message;
    saveLastBatchRows();
    ElMessage.error(`申请 ${row.applicationId} AI 检测失败：${error.message}`);
  }
}

function selectRow(row) {
  localStorage.setItem(CURRENT_APPLICATION_ID_KEY, String(row.applicationId));
}

function goToDetail(row) {
  selectRow(row);
  router.push(`/applications/${row.applicationId}`);
}

function extractPolicyReferences(result) {
  const report = result.report || {};
  return report.policy_references || report.policyReferences || [];
}

function formatMoney(value) {
  if (value === undefined || value === null || value === "") {
    return "-";
  }
  return Number(value).toLocaleString("zh-CN");
}

function isTerminal(status) {
  return ["APPROVED", "REJECTED"].includes(status);
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
</script>
