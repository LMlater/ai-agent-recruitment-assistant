package com.smartcredit.agent;

import com.smartcredit.common.Result;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.RestController;

import java.util.List;

@RestController
@RequiredArgsConstructor
public class AiAuditQueryController {
    private final AiAuditQueryService aiAuditQueryService;

    @GetMapping("/api/loan-applications/{id}/ai-reports")
    public Result<List<AiDecisionReport>> listReportsByApplication(@PathVariable Long id) {
        return Result.success(aiAuditQueryService.listReportsByApplicationId(id));
    }

    @GetMapping("/api/ai-reports/{reportId}")
    public Result<AiDecisionReport> getReport(@PathVariable Long reportId) {
        return Result.success(aiAuditQueryService.getReport(reportId));
    }

    @GetMapping("/api/loan-applications/{id}/agent-logs")
    public Result<List<AgentExecutionLog>> listLogsByApplication(@PathVariable Long id) {
        return Result.success(aiAuditQueryService.listLogsByApplicationId(id));
    }

    @GetMapping("/api/agent-workflows/{workflowId}/logs")
    public Result<List<AgentExecutionLog>> listLogsByWorkflow(@PathVariable String workflowId) {
        return Result.success(aiAuditQueryService.listLogsByWorkflowId(workflowId));
    }
}
