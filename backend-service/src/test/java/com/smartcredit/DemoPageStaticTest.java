package com.smartcredit;

import org.junit.jupiter.api.Test;

import java.nio.file.Files;
import java.nio.file.Path;

import static org.junit.jupiter.api.Assertions.assertTrue;

class DemoPageStaticTest {

    @Test
    void demoPageContainsRequiredDemoWorkflowHooks() throws Exception {
        Path demoPage = Path.of("src/main/resources/static/demo.html");

        assertTrue(Files.exists(demoPage));
        String html = Files.readString(demoPage);

        assertTrue(html.contains("基于 Spring Boot + FastAPI + LangGraph 的多 Agent 智能信贷审批辅助系统"));
        assertTrue(html.contains("function unwrapResult"));
        assertTrue(html.contains("/api/auth/init-admin"));
        assertTrue(html.contains("/api/loan-applications"));
        assertTrue(html.contains("/api/agent-workflows/"));
        assertTrue(html.contains("/api/approvals/"));
        assertTrue(html.contains("/api/v1/debug/llm-config"));
        assertTrue(html.contains("客户申请端"));
        assertTrue(html.contains("银行审批工作台"));
        assertTrue(html.contains("生成一笔脱敏演示申请"));
        assertTrue(html.contains("仅用于本地面试 Demo"));
        assertTrue(html.contains("真实业务中客户和贷款申请来自业务系统"));
        assertTrue(html.contains("继续尝试登录"));
        assertTrue(html.contains("translateSummary"));
        assertTrue(html.contains("Raw JSON 折叠面板"));
        assertTrue(html.contains("LLM Provider"));
        assertTrue(html.contains("LLM Used"));
        assertTrue(html.contains("LLM Error"));
        assertTrue(html.contains("function uniquePolicyReferences"));
        assertTrue(html.contains("seenPolicyCodes"));
        assertTrue(html.contains("state.llmInfo.provider || \"mock\""));
        assertTrue(html.contains("action: label"));
        assertTrue(html.contains("error: error.message"));
        assertTrue(html.contains("人工审批边界提示"));
        assertTrue(html.contains("explainAiReviewError"));
        assertTrue(html.contains("data-manual-approval"));
        assertTrue(html.contains("setManualApprovalLocked"));
        assertTrue(html.contains("最终审批已完成，如需重新演示请准备新的演示申请。"));
        assertTrue(html.contains("Raw JSON"));
        assertTrue(html.contains("function renderToolCalls"));
        assertTrue(html.contains("function toolNameDescription"));
        assertTrue(html.contains("function toolCallsForAgent"));
        assertTrue(html.contains("MaterialChecklistTool"));
        assertTrue(html.contains("RiskRuleTool"));
        assertTrue(html.contains("RiskModelTool"));
        assertTrue(html.contains("PolicySearchTool"));
        assertTrue(html.contains("ComplianceGuardrailTool"));
        assertTrue(html.contains("ReportGenerationTool"));
        assertTrue(html.contains("SeniorReviewChecklistTool"));
        assertTrue(html.contains("材料完整性检查工具"));
        assertTrue(html.contains("暂无工具调用记录"));
        assertTrue(html.contains("read-only/auditable assistance"));
        assertTrue(html.contains("Agent does not call final approval write tools"));
    }
}
