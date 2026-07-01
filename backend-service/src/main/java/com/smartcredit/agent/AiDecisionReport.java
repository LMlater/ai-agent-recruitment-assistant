package com.smartcredit.agent;

import lombok.Data;

import java.math.BigDecimal;
import java.time.LocalDateTime;

@Data
public class AiDecisionReport {
    private Long id;
    private Long applicationId;
    private String workflowId;
    private String finalDecision;
    private String riskLevel;
    private Integer riskScore;
    private BigDecimal suggestedAmount;
    private String summary;
    private String reportJson;
    private LocalDateTime createdAt;
}
