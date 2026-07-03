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
        assertTrue(html.contains("data-manual-approval"));
        assertTrue(html.contains("setManualApprovalLocked"));
        assertTrue(html.contains("最终审批已完成，如需重新演示请创建新的 loan application。"));
        assertTrue(html.contains("Raw JSON"));
    }
}
