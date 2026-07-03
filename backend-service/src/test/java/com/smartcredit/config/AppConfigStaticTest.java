package com.smartcredit.config;

import org.junit.jupiter.api.Test;

import java.nio.file.Files;
import java.nio.file.Path;

import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertTrue;

class AppConfigStaticTest {

    @Test
    void agentServiceRestTemplateTimeoutsAreConfigurableForRealLlmDemo() throws Exception {
        String appConfig = Files.readString(Path.of("src/main/java/com/smartcredit/config/AppConfig.java"));
        String applicationYaml = Files.readString(Path.of("src/main/resources/application.yml"));

        assertTrue(appConfig.contains("agent-service.connect-timeout-seconds"));
        assertTrue(appConfig.contains("agent-service.read-timeout-seconds"));
        assertTrue(applicationYaml.contains("AGENT_SERVICE_CONNECT_TIMEOUT_SECONDS:5"));
        assertTrue(applicationYaml.contains("AGENT_SERVICE_READ_TIMEOUT_SECONDS:120"));
        assertFalse(appConfig.contains("setReadTimeout(Duration.ofSeconds(20))"));
    }
}
