package com.smartcredit.agent;

import com.smartcredit.agent.client.AgentReviewClient;
import com.smartcredit.agent.dto.AgentResult;
import com.smartcredit.agent.dto.AgentReviewResponse;
import com.smartcredit.agent.dto.PolicyReference;
import com.smartcredit.agent.dto.ReviewReport;
import com.smartcredit.audit.AuditLogService;
import com.smartcredit.common.BusinessException;
import com.smartcredit.customer.Customer;
import com.smartcredit.customer.CustomerMapper;
import com.smartcredit.loan.LoanApplication;
import com.smartcredit.loan.LoanApplicationMapper;
import com.smartcredit.loan.LoanStatus;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;

import java.math.BigDecimal;
import java.time.LocalDateTime;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertTrue;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.mockito.ArgumentCaptor.forClass;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.ArgumentMatchers.eq;
import static org.mockito.Mockito.never;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;

@ExtendWith(MockitoExtension.class)
class AgentReviewServiceTest {

    @Mock
    private LoanApplicationMapper loanApplicationMapper;

    @Mock
    private CustomerMapper customerMapper;

    @Mock
    private AgentReviewClient agentReviewClient;

    @Mock
    private AiDecisionReportMapper aiDecisionReportMapper;

    @Mock
    private AgentExecutionLogMapper agentExecutionLogMapper;

    @Mock
    private AuditLogService auditLogService;

    @InjectMocks
    private AgentReviewService agentReviewService;

    @Test
    void executeAiReviewStoresReportAndMovesApplicationOnlyToAiReviewed() {
        LoanApplication application = applicationWithStatus(LoanStatus.SUBMITTED);
        AgentReviewResponse response = reviewResponse();

        when(loanApplicationMapper.selectById(7L)).thenReturn(application);
        when(customerMapper.selectById(3L)).thenReturn(customer());
        when(agentReviewClient.review(any())).thenReturn(response);

        agentReviewService.executeAiReview(7L, 99L, "127.0.0.1");

        var reportCaptor = forClass(AiDecisionReport.class);
        verify(aiDecisionReportMapper).insert(reportCaptor.capture());
        assertTrue(reportCaptor.getValue().getReportJson().contains("\"policy_code\":\"R-001\""));
        assertTrue(reportCaptor.getValue().getReportJson().contains("\"document_name\":\"risk_control_policy.md\""));
        var logCaptor = forClass(AgentExecutionLog.class);
        verify(agentExecutionLogMapper).insert(logCaptor.capture());
        assertTrue(logCaptor.getValue().getOutputSummary().contains("llm_provider=mock"));
        assertTrue(logCaptor.getValue().getOutputSummary().contains("llm_used=true"));
        assertTrue(logCaptor.getValue().getOutputSummary().contains("tools=ReportGenerationTool:SUCCESS(12ms)"));
        verify(loanApplicationMapper).updateAiReviewResult(
                eq(7L),
                eq(LoanStatus.AI_REVIEWED.name()),
                eq(86),
                eq("LOW"),
                eq("APPROVE"),
                eq("AI suggests manual approval review.")
        );
        verify(auditLogService).record(
                eq(99L),
                eq("AI_REVIEW"),
                eq("loan_application"),
                eq(7L),
                any(),
                eq("127.0.0.1")
        );
    }

    @Test
    void executeAiReviewAllowsAiReviewedForDemoReevaluation() {
        when(loanApplicationMapper.selectById(7L)).thenReturn(applicationWithStatus(LoanStatus.AI_REVIEWED));
        when(customerMapper.selectById(3L)).thenReturn(customer());
        when(agentReviewClient.review(any())).thenReturn(reviewResponse());

        agentReviewService.executeAiReview(7L, 99L, "127.0.0.1");

        verify(loanApplicationMapper).updateAiReviewResult(
                eq(7L),
                eq(LoanStatus.AI_REVIEWED.name()),
                eq(86),
                eq("LOW"),
                eq("APPROVE"),
                eq("AI suggests manual approval review.")
        );
    }

    @Test
    void executeAiReviewAllowsResubmittedAndMovesApplicationToAiReviewed() {
        when(loanApplicationMapper.selectById(7L)).thenReturn(applicationWithStatus(LoanStatus.RESUBMITTED));
        when(customerMapper.selectById(3L)).thenReturn(customer());
        when(agentReviewClient.review(any())).thenReturn(reviewResponse());

        agentReviewService.executeAiReview(7L, 99L, "127.0.0.1");

        verify(loanApplicationMapper).updateAiReviewResult(
                eq(7L),
                eq(LoanStatus.AI_REVIEWED.name()),
                eq(86),
                eq("LOW"),
                eq("APPROVE"),
                eq("AI suggests manual approval review.")
        );
    }

    @Test
    void executeAiReviewRejectsMaterialUpdatedAndNeedMoreInfoBeforeResubmission() {
        for (LoanStatus status : List.of(LoanStatus.MATERIAL_UPDATED, LoanStatus.NEED_MORE_INFO)) {
            when(loanApplicationMapper.selectById(7L)).thenReturn(applicationWithStatus(status));

            assertThrows(BusinessException.class, () -> agentReviewService.executeAiReview(7L, 99L, "127.0.0.1"));

            verify(agentReviewClient, never()).review(any());
        }
    }

    @Test
    void executeAiReviewKeepsDecisionMetadataWhenToolCallsAreMissing() {
        LoanApplication application = applicationWithStatus(LoanStatus.SUBMITTED);
        AgentReviewResponse response = reviewResponseWithoutToolCalls();

        when(loanApplicationMapper.selectById(7L)).thenReturn(application);
        when(customerMapper.selectById(3L)).thenReturn(customer());
        when(agentReviewClient.review(any())).thenReturn(response);

        agentReviewService.executeAiReview(7L, 99L, "127.0.0.1");

        var logCaptor = forClass(AgentExecutionLog.class);
        verify(agentExecutionLogMapper).insert(logCaptor.capture());
        assertTrue(logCaptor.getValue().getOutputSummary().contains("llm_provider=mock"));
        assertFalse(logCaptor.getValue().getOutputSummary().contains("tools="));
    }

    @Test
    void executeAiReviewStoresFailedToolCallSummaryWithoutFullToolOutput() {
        LoanApplication application = applicationWithStatus(LoanStatus.SUBMITTED);
        AgentReviewResponse response = reviewResponseWithFailedToolCall();

        when(loanApplicationMapper.selectById(7L)).thenReturn(application);
        when(customerMapper.selectById(3L)).thenReturn(customer());
        when(agentReviewClient.review(any())).thenReturn(response);

        agentReviewService.executeAiReview(7L, 99L, "127.0.0.1");

        var logCaptor = forClass(AgentExecutionLog.class);
        verify(agentExecutionLogMapper).insert(logCaptor.capture());
        assertTrue(logCaptor.getValue().getOutputSummary().contains("tools=RiskModelTool:FAILED(5ms,error=model unavailable)"));
        assertFalse(logCaptor.getValue().getOutputSummary().contains("raw_probability_vector"));
    }

    @Test
    void executeAiReviewRejectsStatusesOutsideSubmittedOrAiReviewed() {
        for (LoanStatus status : List.of(LoanStatus.DRAFT, LoanStatus.MATERIAL_UPDATED, LoanStatus.APPROVED, LoanStatus.REJECTED, LoanStatus.NEED_MORE_INFO)) {
            when(loanApplicationMapper.selectById(7L)).thenReturn(applicationWithStatus(status));

            assertThrows(BusinessException.class, () -> agentReviewService.executeAiReview(7L, 99L, "127.0.0.1"));

            verify(agentReviewClient, never()).review(any());
        }
    }

    private LoanApplication applicationWithStatus(LoanStatus status) {
        LoanApplication application = new LoanApplication();
        application.setId(7L);
        application.setCustomerId(3L);
        application.setAmount(new BigDecimal("80000"));
        application.setTermMonths(24);
        application.setPurpose("personal consumption");
        application.setStatus(status.name());
        return application;
    }

    private Customer customer() {
        Customer customer = new Customer();
        customer.setId(3L);
        customer.setAge(32);
        customer.setMonthlyIncome(new BigDecimal("12000"));
        customer.setWorkYears(5);
        customer.setExistingDebt(new BigDecimal("30000"));
        customer.setOverdueCount(0);
        customer.setAssetProofCount(2);
        return customer;
    }

    private AgentReviewResponse reviewResponse() {
        AgentReviewResponse response = new AgentReviewResponse();
        response.setWorkflowId("workflow-1");
        response.setFinalDecision("APPROVE");
        response.setRiskLevel("LOW");
        response.setRiskScore(86);
        response.setSuggestedAmount(new BigDecimal("80000"));
        response.setSummary("AI suggests manual approval review.");
        response.setReport(new ReviewReport(
                Map.of("complete", true),
                Map.of("risk_level", "LOW"),
                List.of(new PolicyReference(
                        "R-001",
                        "risk_control_policy.md",
                        "R-001 Debt-to-Income Ratio Control",
                        "Debt-to-income ratio above 80% requires high-risk manual review.",
                        new BigDecimal("0.82")
                )),
                List.of("AI suggestion requires manual approval"),
                List.of("stable income"),
                List.of()
        ));
        response.setAgentResults(List.of(new AgentResult(
                "DecisionAgent",
                "SUCCESS",
                "Summarize upstream agent outputs",
                "Generated APPROVE recommendation using LLM report generation",
                null,
                LocalDateTime.now(),
                LocalDateTime.now(),
                12L,
                Map.of(
                        "decision_report_generation", decisionReportGeneration(),
                        "tool_calls", List.of(toolCall("ReportGenerationTool", "SUCCESS", 12L, null))
                )
        )));
        return response;
    }

    private AgentReviewResponse reviewResponseWithoutToolCalls() {
        AgentReviewResponse response = reviewResponse();
        response.getAgentResults().get(0).setResult(Map.of("decision_report_generation", decisionReportGeneration()));
        return response;
    }

    private AgentReviewResponse reviewResponseWithFailedToolCall() {
        AgentReviewResponse response = reviewResponse();
        response.getAgentResults().get(0).setResult(Map.of(
                "tool_calls",
                List.of(toolCall("RiskModelTool", "FAILED", 5L, "model unavailable"))
        ));
        return response;
    }

    private Map<String, Object> decisionReportGeneration() {
        Map<String, Object> generation = new HashMap<>();
        generation.put("llm_used", true);
        generation.put("llm_provider", "mock");
        generation.put("llm_error", null);
        return generation;
    }

    private Map<String, Object> toolCall(String toolName, String status, Long durationMs, String errorMessage) {
        Map<String, Object> toolCall = new HashMap<>();
        toolCall.put("tool_name", toolName);
        toolCall.put("status", status);
        toolCall.put("duration_ms", durationMs);
        toolCall.put("input_summary", "input fields only");
        toolCall.put("output_summary", "short summary");
        toolCall.put("error_message", errorMessage);
        toolCall.put("raw_probability_vector", List.of(0.1, 0.9));
        return toolCall;
    }
}
