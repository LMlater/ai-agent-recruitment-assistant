package com.smartcredit.agent;

import org.apache.ibatis.annotations.Insert;
import org.apache.ibatis.annotations.Mapper;
import org.apache.ibatis.annotations.Options;

@Mapper
public interface AgentExecutionLogMapper {
    @Insert("""
            insert into agent_execution_log(workflow_id, application_id, agent_name, status, input_summary,
                                            output_summary, error_message, started_at, ended_at, duration_ms)
            values(#{workflowId}, #{applicationId}, #{agentName}, #{status}, #{inputSummary},
                   #{outputSummary}, #{errorMessage}, #{startedAt}, #{endedAt}, #{durationMs})
            """)
    @Options(useGeneratedKeys = true, keyProperty = "id")
    int insert(AgentExecutionLog log);
}
