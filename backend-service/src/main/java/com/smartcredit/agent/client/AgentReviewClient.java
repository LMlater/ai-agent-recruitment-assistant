package com.smartcredit.agent.client;

import com.smartcredit.agent.dto.AgentReviewRequest;
import com.smartcredit.agent.dto.AgentReviewResponse;

public interface AgentReviewClient {
    AgentReviewResponse review(AgentReviewRequest request);
}
