package com.churninsight.controller;

import com.churninsight.dto.PredictRequest;
import com.churninsight.dto.PredictResponse;
import com.churninsight.service.PredictionService;
import jakarta.validation.Valid;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;
import reactor.core.publisher.Mono;

@RestController
@RequestMapping("/")
public class PredictController {
    private final PredictionService service;

    public PredictController(PredictionService service) {
        this.service = service;
    }

    @PostMapping("/predict")
    public Mono<ResponseEntity<PredictResponse>> predict(@Valid @RequestBody PredictRequest req) {
        return service.predict(req)
                .map(resp -> ResponseEntity.ok(resp))
                .onErrorResume(e -> Mono.just(ResponseEntity.status(HttpStatus.BAD_GATEWAY).build()));
    }
}