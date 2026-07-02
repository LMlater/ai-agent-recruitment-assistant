package com.smartcredit.agent;

import org.apache.ibatis.annotations.Insert;
import org.apache.ibatis.annotations.Mapper;
import org.apache.ibatis.annotations.Options;
import org.apache.ibatis.annotations.Select;

import java.util.List;

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

    @Select("select * from agent_execution_log where application_id = #{applicationId} order by id asc")
    List<AgentExecutionLog> selectByApplicationId(Long applicationId);

    @Select("select * from agent_execution_log where workflow_id = #{workflowId} order by id asc")
    List<AgentExecutionLog> selectByWorkflowId(String workflowId);
}
