package com.smartcredit.agent;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.datatype.jsr310.JavaTimeModule;
import com.smartcredit.agent.dto.AgentReviewResponse;
import com.smartcredit.agent.dto.PolicyReference;
import org.junit.jupiter.api.Test;

import java.math.BigDecimal;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNotNull;

class AgentReviewResponseJsonTest {

    private final ObjectMapper objectMapper = new ObjectMapper().registerModule(new JavaTimeModule());

    @Test
    void deserializesStructuredPolicyReferencesFromAgentServiceResponse() throws Exception {
        String json = """
                {
                  "workflow_id": "workflow-rag-1",
                  "final_decision": "NEED_MORE_INFO",
                  "risk_level": "MEDIUM",
                  "risk_score": 68,
                  "suggested_amount": 90000,
                  "summary": "Manual review is recommended.",
                  "agent_results": [
                    {
                      "agent_name": "PolicyAgent",
                      "status": "SUCCESS",
                      "input_summary": "Run RAG policy retrieval over mock credit policy documents",
                      "output_summary": "Retrieved 1 policy references",
                      "error_message": null,
                      "started_at": "2026-07-02T12:00:00",
                      "ended_at": "2026-07-02T12:00:01",
                      "duration_ms": 25,
                      "result": {
                        "policy_references": [
                          {
                            "policy_code": "R-001",
                            "document_name": "risk_control_policy.md",
                            "section_title": "R-001 Debt-to-Income Ratio Control",
                            "content": "Debt-to-income ratio above 80% requires high-risk manual review.",
                            "score": 0.82
                          }
                        ]
                      }
                    }
                  ],
                  "report": {
                    "intake_check": {"complete": true},
                    "risk_assessment": {
                      "risk_level": "MEDIUM",
                      "risk_score": 68,
                      "debt_income_ratio": 0.82
                    },
                    "policy_references": [
                      {
                        "policy_code": "R-001",
                        "document_name": "risk_control_policy.md",
                        "section_title": "R-001 Debt-to-Income Ratio Control",
                        "content": "Debt-to-income ratio above 80% requires high-risk manual review.",
                        "score": 0.82
                      }
                    ],
                    "compliance_warnings": ["AI output is approval assistance only."],
                    "decision_reasons": ["Debt-to-income ratio is above 80%."],
                    "required_materials": []
                  }
                }
                """;

        AgentReviewResponse response = objectMapper.readValue(json, AgentReviewResponse.class);

        assertEquals("workflow-rag-1", response.getWorkflowId());
        assertEquals("PolicyAgent", response.getAgentResults().get(0).getAgentName());
        assertEquals("MEDIUM", response.getReport().getRiskAssessment().get("risk_level"));
        assertEquals(68, response.getReport().getRiskAssessment().get("risk_score"));

        PolicyReference reference = response.getReport().getPolicyReferences().get(0);
        assertEquals("R-001", reference.getPolicyCode());
        assertEquals("risk_control_policy.md", reference.getDocumentName());
        assertEquals("R-001 Debt-to-Income Ratio Control", reference.getSectionTitle());
        assertEquals("Debt-to-income ratio above 80% requires high-risk manual review.", reference.getContent());
        assertEquals(0, new BigDecimal("0.82").compareTo(reference.getScore()));

        String reportJson = objectMapper.writeValueAsString(response.getReport());
        assertNotNull(reportJson);
        assertEquals(true, reportJson.contains("\"policy_code\":\"R-001\""));
    }
}
