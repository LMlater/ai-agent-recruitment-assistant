package com.smartcredit.agent;

import org.apache.ibatis.annotations.Insert;
import org.apache.ibatis.annotations.Mapper;
import org.apache.ibatis.annotations.Options;

@Mapper
public interface AiDecisionReportMapper {
    @Insert("""
            insert into ai_decision_report(application_id, workflow_id, final_decision, risk_level, risk_score,
                                           suggested_amount, summary, report_json)
            values(#{applicationId}, #{workflowId}, #{finalDecision}, #{riskLevel}, #{riskScore},
                   #{suggestedAmount}, #{summary}, #{reportJson})
            """)
    @Options(useGeneratedKeys = true, keyProperty = "id")
    int insert(AiDecisionReport report);
}
