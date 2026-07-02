package com.smartcredit.agent.dto;

import com.fasterxml.jackson.annotation.JsonProperty;
import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.math.BigDecimal;

@Data
@NoArgsConstructor
@AllArgsConstructor
public class PolicyReference {
    @JsonProperty("policy_code")
    private String policyCode;
    @JsonProperty("document_name")
    private String documentName;
    @JsonProperty("section_title")
    private String sectionTitle;
    private String content;
    private BigDecimal score;
}
