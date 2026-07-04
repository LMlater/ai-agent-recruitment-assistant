package com.smartcredit;

import org.junit.jupiter.api.Test;

import java.nio.file.Files;
import java.nio.file.Path;

import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertTrue;

class DeliveryPackagingStaticTest {

    @Test
    void dockerComposePackagesTheFullDemoStack() throws Exception {
        String compose = Files.readString(Path.of("../docker-compose.yml"));

        assertTrue(compose.contains("mysql:"));
        assertTrue(compose.contains("redis:"));
        assertTrue(compose.contains("agent-service:"));
        assertTrue(compose.contains("backend-service:"));
        assertTrue(compose.contains("condition: service_healthy"));
        assertTrue(compose.contains("AGENT_SERVICE_BASE_URL"));
        assertTrue(compose.contains("LLM_PROVIDER"));
    }

    @Test
    void dockerfilesAndCiUseMockSafeDeliveryDefaults() throws Exception {
        String agentDockerfile = Files.readString(Path.of("../agent-service/Dockerfile"));
        String backendDockerfile = Files.readString(Path.of("Dockerfile"));
        String ci = Files.readString(Path.of("../.github/workflows/ci.yml"));

        assertTrue(agentDockerfile.contains("python:3.11-slim"));
        assertTrue(agentDockerfile.contains("LLM_PROVIDER=mock"));
        assertFalse(agentDockerfile.contains(".env"));
        assertTrue(backendDockerfile.contains("maven:3.9"));
        assertTrue(backendDockerfile.contains("eclipse-temurin:17"));
        assertTrue(ci.contains("python -m pytest tests -q"));
        assertTrue(ci.contains("mvn test"));
        assertTrue(ci.contains("check_demo_readiness.py --skip-services"));
    }
}
