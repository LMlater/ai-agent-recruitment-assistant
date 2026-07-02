package com.smartcredit.agent;

import com.smartcredit.common.BusinessException;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;

import java.util.List;

@Service
@RequiredArgsConstructor
public class AiAuditQueryService {
    private final AiDecisionReportMapper aiDecisionReportMapper;
    private final AgentExecutionLogMapper agentExecutionLogMapper;

    public List<AiDecisionReport> listReportsByApplicationId(Long applicationId) {
        return aiDecisionReportMapper.selectByApplicationId(applicationId);
    }

    public AiDecisionReport getReport(Long reportId) {
        AiDecisionReport report = aiDecisionReportMapper.selectById(reportId);
        if (report == null) {
            throw new BusinessException("AI decision report not found");
        }
        return report;
    }

    public List<AgentExecutionLog> listLogsByApplicationId(Long applicationId) {
        return agentExecutionLogMapper.selectByApplicationId(applicationId);
    }

    public List<AgentExecutionLog> listLogsByWorkflowId(String workflowId) {
        return agentExecutionLogMapper.selectByWorkflowId(workflowId);
    }
}
