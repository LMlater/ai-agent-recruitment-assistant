package com.smartcredit.agent;

import com.smartcredit.agent.client.AgentReviewClient;
import com.smartcredit.agent.dto.AgentResult;
import com.smartcredit.agent.dto.AgentReviewResponse;
import com.smartcredit.agent.dto.ReviewReport;
import com.smartcredit.audit.AuditLogService;
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
import java.util.List;
import java.util.Map;

import static org.mockito.ArgumentMatchers.any;
import static org.mockito.ArgumentMatchers.eq;
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
        LoanApplication application = new LoanApplication();
        application.setId(7L);
        application.setCustomerId(3L);
        application.setAmount(new BigDecimal("80000"));
        application.setTermMonths(24);
        application.setPurpose("personal consumption");
        application.setStatus(LoanStatus.SUBMITTED.name());

        Customer customer = new Customer();
        customer.setId(3L);
        customer.setAge(32);
        customer.setMonthlyIncome(new BigDecimal("12000"));
        customer.setWorkYears(5);
        customer.setExistingDebt(new BigDecimal("30000"));
        customer.setOverdueCount(0);
        customer.setAssetProofCount(2);

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
                List.of("mock policy"),
                List.of("AI suggestion requires manual approval"),
                List.of("stable income"),
                List.of()
        ));
        response.setAgentResults(List.of(new AgentResult(
                "RiskAgent",
                "SUCCESS",
                "score applicant",
                "LOW risk",
                null,
                LocalDateTime.now(),
                LocalDateTime.now(),
                12L,
                Map.of("risk_score", 86)
        )));

        when(loanApplicationMapper.selectById(7L)).thenReturn(application);
        when(customerMapper.selectById(3L)).thenReturn(customer);
        when(agentReviewClient.review(any())).thenReturn(response);

        agentReviewService.executeAiReview(7L, 99L, "127.0.0.1");

        verify(aiDecisionReportMapper).insert(any(AiDecisionReport.class));
        verify(agentExecutionLogMapper).insert(any(AgentExecutionLog.class));
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
}
