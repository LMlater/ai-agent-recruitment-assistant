package com.smartcredit.agent;

import com.smartcredit.common.BusinessException;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;

import java.util.List;

import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.mockito.Mockito.when;

@ExtendWith(MockitoExtension.class)
class AiAuditQueryServiceTest {

    @Mock
    private AiDecisionReportMapper aiDecisionReportMapper;

    @Mock
    private AgentExecutionLogMapper agentExecutionLogMapper;

    @InjectMocks
    private AiAuditQueryService aiAuditQueryService;

    @Test
    void listReportsByApplicationReturnsHistoricalReports() {
        List<AiDecisionReport> reports = List.of(new AiDecisionReport());
        when(aiDecisionReportMapper.selectByApplicationId(7L)).thenReturn(reports);

        assertSame(reports, aiAuditQueryService.listReportsByApplicationId(7L));
    }

    @Test
    void getReportThrowsWhenMissing() {
        when(aiDecisionReportMapper.selectById(404L)).thenReturn(null);

        assertThrows(BusinessException.class, () -> aiAuditQueryService.getReport(404L));
    }

    @Test
    void listLogsByWorkflowReturnsCompleteAgentChain() {
        List<AgentExecutionLog> logs = List.of(new AgentExecutionLog());
        when(agentExecutionLogMapper.selectByWorkflowId("workflow-1")).thenReturn(logs);

        assertSame(logs, aiAuditQueryService.listLogsByWorkflowId("workflow-1"));
    }
}
