package com.smartcredit.agent;

import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.datatype.jsr310.JavaTimeModule;
import com.smartcredit.agent.client.AgentReviewClient;
import com.smartcredit.agent.dto.AgentResult;
import com.smartcredit.agent.dto.AgentReviewRequest;
import com.smartcredit.agent.dto.AgentReviewResponse;
import com.smartcredit.audit.AuditLogService;
import com.smartcredit.common.BusinessException;
import com.smartcredit.customer.Customer;
import com.smartcredit.customer.CustomerMapper;
import com.smartcredit.loan.LoanApplication;
import com.smartcredit.loan.LoanApplicationMapper;
import com.smartcredit.loan.LoanStatus;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

@Service
@RequiredArgsConstructor
public class AgentReviewService {
    private final LoanApplicationMapper loanApplicationMapper;
    private final CustomerMapper customerMapper;
    private final AgentReviewClient agentReviewClient;
    private final AiDecisionReportMapper aiDecisionReportMapper;
    private final AgentExecutionLogMapper agentExecutionLogMapper;
    private final AuditLogService auditLogService;
    private final ObjectMapper objectMapper = new ObjectMapper().registerModule(new JavaTimeModule());

    @Transactional
    public AgentReviewResponse executeAiReview(Long applicationId, Long userId, String ip) {
        LoanApplication application = loanApplicationMapper.selectById(applicationId);
        if (application == null) {
            throw new BusinessException("Loan application not found");
        }
        validateReviewableStatus(application.getStatus());
        Customer customer = customerMapper.selectById(application.getCustomerId());
        if (customer == null) {
            throw new BusinessException("Customer not found");
        }

        AgentReviewResponse response = agentReviewClient.review(AgentReviewRequest.from(application, customer));
        saveReport(applicationId, response);
        saveAgentLogs(applicationId, response);
        loanApplicationMapper.updateAiReviewResult(
                applicationId,
                LoanStatus.AI_REVIEWED.name(),
                response.getRiskScore(),
                response.getRiskLevel(),
                response.getFinalDecision(),
                response.getSummary()
        );
        auditLogService.record(userId, "AI_REVIEW", "loan_application", applicationId, "Executed AI approval assistance", ip);
        return response;
    }

    private void validateReviewableStatus(String status) {
        if (LoanStatus.SUBMITTED.name().equals(status)) {
            return;
        }
        // Demo and reassessment path: allow rerunning AI assistance after a prior AI review.
        if (LoanStatus.AI_REVIEWED.name().equals(status)) {
            return;
        }
        throw new BusinessException("AI review can only run when application status is SUBMITTED or AI_REVIEWED");
    }

    private void saveReport(Long applicationId, AgentReviewResponse response) {
        AiDecisionReport report = new AiDecisionReport();
        report.setApplicationId(applicationId);
        report.setWorkflowId(response.getWorkflowId());
        report.setFinalDecision(response.getFinalDecision());
        report.setRiskLevel(response.getRiskLevel());
        report.setRiskScore(response.getRiskScore());
        report.setSuggestedAmount(response.getSuggestedAmount());
        report.setSummary(response.getSummary());
        report.setReportJson(toJson(response.getReport()));
        aiDecisionReportMapper.insert(report);
    }

    private void saveAgentLogs(Long applicationId, AgentReviewResponse response) {
        for (AgentResult result : response.getAgentResults()) {
            AgentExecutionLog log = new AgentExecutionLog();
            log.setWorkflowId(response.getWorkflowId());
            log.setApplicationId(applicationId);
            log.setAgentName(result.getAgentName());
            log.setStatus(result.getStatus());
            log.setInputSummary(result.getInputSummary());
            log.setOutputSummary(outputSummaryWithDecisionReportGeneration(result));
            log.setErrorMessage(result.getErrorMessage());
            log.setStartedAt(result.getStartedAt());
            log.setEndedAt(result.getEndedAt());
            log.setDurationMs(result.getDurationMs());
            agentExecutionLogMapper.insert(log);
        }
    }

    private String outputSummaryWithDecisionReportGeneration(AgentResult result) {
        Object metadata = result.getResult() == null ? null : result.getResult().get("decision_report_generation");
        if (!(metadata instanceof java.util.Map<?, ?> generation)) {
            return result.getOutputSummary();
        }

        String generationSummary = "decision_report_generation: llm_used=%s, llm_provider=%s, llm_error=%s".formatted(
                generation.get("llm_used"),
                generation.get("llm_provider"),
                generation.get("llm_error")
        );
        String outputSummary = result.getOutputSummary();
        if (outputSummary == null || outputSummary.isBlank()) {
            return generationSummary;
        }
        return outputSummary + " | " + generationSummary;
    }

    private String toJson(Object value) {
        try {
            return objectMapper.writeValueAsString(value);
        } catch (JsonProcessingException exception) {
            throw new BusinessException("Failed to serialize AI review report");
        }
    }
}
