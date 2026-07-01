package com.smartcredit.agent.dto;

import com.fasterxml.jackson.annotation.JsonProperty;
import lombok.Data;

import java.math.BigDecimal;
import java.util.ArrayList;
import java.util.List;

@Data
public class AgentReviewResponse {
    @JsonProperty("workflow_id")
    private String workflowId;
    @JsonProperty("final_decision")
    private String finalDecision;
    @JsonProperty("risk_level")
    private String riskLevel;
    @JsonProperty("risk_score")
    private Integer riskScore;
    @JsonProperty("suggested_amount")
    private BigDecimal suggestedAmount;
    private String summary;
    @JsonProperty("agent_results")
    private List<AgentResult> agentResults = new ArrayList<>();
    private ReviewReport report;
}
