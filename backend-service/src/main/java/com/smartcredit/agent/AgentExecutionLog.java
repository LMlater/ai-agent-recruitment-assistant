package com.smartcredit.agent;

import lombok.Data;

import java.time.LocalDateTime;

@Data
public class AgentExecutionLog {
    private Long id;
    private String workflowId;
    private Long applicationId;
    private String agentName;
    private String status;
    private String inputSummary;
    private String outputSummary;
    private String errorMessage;
    private LocalDateTime startedAt;
    private LocalDateTime endedAt;
    private Long durationMs;
    private LocalDateTime createdAt;
}
