package com.smartcredit.config;

import com.smartcredit.security.JwtAuthInterceptor;
import lombok.RequiredArgsConstructor;
import org.springframework.boot.web.client.RestTemplateBuilder;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.security.crypto.bcrypt.BCryptPasswordEncoder;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.web.client.RestTemplate;
import org.springframework.web.servlet.config.annotation.InterceptorRegistry;
import org.springframework.web.servlet.config.annotation.WebMvcConfigurer;

import java.time.Duration;

@Configuration
@RequiredArgsConstructor
public class AppConfig implements WebMvcConfigurer {
    private final JwtAuthInterceptor jwtAuthInterceptor;

    @Value("${agent-service.connect-timeout-seconds:5}")
    private long agentServiceConnectTimeoutSeconds;

    @Value("${agent-service.read-timeout-seconds:120}")
    private long agentServiceReadTimeoutSeconds;

    @Bean
    public RestTemplate restTemplate(RestTemplateBuilder builder) {
        return builder
                .setConnectTimeout(Duration.ofSeconds(agentServiceConnectTimeoutSeconds))
                .setReadTimeout(Duration.ofSeconds(agentServiceReadTimeoutSeconds))
                .build();
    }

    @Bean
    public PasswordEncoder passwordEncoder() {
        return new BCryptPasswordEncoder();
    }

    @Override
    public void addInterceptors(InterceptorRegistry registry) {
        registry.addInterceptor(jwtAuthInterceptor)
                .addPathPatterns("/api/**")
                .excludePathPatterns(
                        "/api/auth/login",
                        "/api/auth/init-admin",
                        "/swagger-ui/**",
                        "/v3/api-docs/**"
                );
    }
}
