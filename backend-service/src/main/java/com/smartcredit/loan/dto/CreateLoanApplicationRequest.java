package com.smartcredit.loan.dto;

import jakarta.validation.constraints.DecimalMin;
import jakarta.validation.constraints.Min;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;

import java.math.BigDecimal;

public record CreateLoanApplicationRequest(
        @NotNull Long customerId,
        @NotNull @DecimalMin("1.0") BigDecimal amount,
        @NotNull @Min(1) Integer termMonths,
        @NotBlank String purpose
) {
}
