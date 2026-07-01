package com.smartcredit.agent.client;

import com.smartcredit.agent.dto.AgentReviewRequest;
import com.smartcredit.agent.dto.AgentReviewResponse;
import com.smartcredit.common.BusinessException;
import lombok.RequiredArgsConstructor;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.ResponseEntity;
import org.springframework.stereotype.Component;
import org.springframework.web.client.RestTemplate;

@Component
@RequiredArgsConstructor
public class HttpAgentReviewClient implements AgentReviewClient {
    private final RestTemplate restTemplate;

    @Value("${agent-service.base-url}")
    private String baseUrl;

    @Override
    public AgentReviewResponse review(AgentReviewRequest request) {
        ResponseEntity<AgentReviewResponse> response = restTemplate.postForEntity(
                baseUrl + "/api/v1/reviews",
                request,
                AgentReviewResponse.class
        );
        if (!response.getStatusCode().is2xxSuccessful() || response.getBody() == null) {
            throw new BusinessException("Agent service returned an empty review response");
        }
        return response.getBody();
    }
}
