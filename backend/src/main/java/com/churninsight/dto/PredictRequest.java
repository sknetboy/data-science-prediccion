package com.churninsight.dto;

import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;
import jakarta.validation.constraints.PositiveOrZero;

public record PredictRequest(
        @NotNull @PositiveOrZero Integer tiempo_contrato_meses,
        @NotNull @PositiveOrZero Integer retrasos_pago,
        @NotNull @PositiveOrZero Double uso_mensual,
        @NotBlank String plan
) {}