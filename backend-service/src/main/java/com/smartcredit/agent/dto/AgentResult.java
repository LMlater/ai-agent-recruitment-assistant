package com.smartcredit.agent.dto;

import com.fasterxml.jackson.annotation.JsonProperty;
import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.time.LocalDateTime;
import java.util.Map;

@Data
@NoArgsConstructor
@AllArgsConstructor
public class AgentResult {
    @JsonProperty("agent_name")
    private String agentName;
    private String status;
    @JsonProperty("input_summary")
    private String inputSummary;
    @JsonProperty("output_summary")
    private String outputSummary;
    @JsonProperty("error_message")
    private String errorMessage;
    @JsonProperty("started_at")
    private LocalDateTime startedAt;
    @JsonProperty("ended_at")
    private LocalDateTime endedAt;
    @JsonProperty("duration_ms")
    private Long durationMs;
    private Map<String, Object> result;
}
