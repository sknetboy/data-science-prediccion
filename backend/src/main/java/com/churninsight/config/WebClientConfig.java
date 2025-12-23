package com.churninsight.config;

import org.springframework.beans.factory.annotation.Value;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.web.reactive.function.client.WebClient;

@Configuration
public class WebClientConfig {

    @Value("${prediction.service.base-url:http://localhost:8001}")
    private String propBaseUrl;

    @Value("${PREDICTION_SERVICE_URL:}")
    private String envBaseUrl;

    @Bean
    public WebClient predictionWebClient() {
        String base = (envBaseUrl != null && !envBaseUrl.isBlank()) ? envBaseUrl : propBaseUrl;
        return WebClient.builder().baseUrl(base).build();
    }
}