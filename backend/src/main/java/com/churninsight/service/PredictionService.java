package com.churninsight.service;

import com.churninsight.dto.PredictRequest;
import com.churninsight.dto.PredictResponse;
import org.springframework.http.MediaType;
import org.springframework.stereotype.Service;
import org.springframework.web.reactive.function.client.WebClient;
import reactor.core.publisher.Mono;

@Service
public class PredictionService {
    private final WebClient client;

    public PredictionService(WebClient predictionWebClient) {
        this.client = predictionWebClient;
    }

    public Mono<PredictResponse> predict(PredictRequest req) {
        return client.post()
                .uri("/predict")
                .contentType(MediaType.APPLICATION_JSON)
                .bodyValue(req)
                .retrieve()
                .bodyToMono(PredictResponse.class);
    }
}