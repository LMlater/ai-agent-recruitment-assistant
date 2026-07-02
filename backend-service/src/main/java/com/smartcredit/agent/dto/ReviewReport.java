package com.smartcredit.agent.dto;

import com.fasterxml.jackson.annotation.JsonProperty;
import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.util.List;
import java.util.Map;

@Data
@NoArgsConstructor
@AllArgsConstructor
public class ReviewReport {
    @JsonProperty("intake_check")
    private Map<String, Object> intakeCheck;
    @JsonProperty("risk_assessment")
    private Map<String, Object> riskAssessment;
    @JsonProperty("policy_references")
    private List<PolicyReference> policyReferences;
    @JsonProperty("compliance_warnings")
    private List<String> complianceWarnings;
    @JsonProperty("decision_reasons")
    private List<String> decisionReasons;
    @JsonProperty("required_materials")
    private List<String> requiredMaterials;
}
