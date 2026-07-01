package com.smartcredit.customer.dto;

import jakarta.validation.constraints.DecimalMin;
import jakarta.validation.constraints.Min;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;

import java.math.BigDecimal;

public record CustomerRequest(
        @NotBlank String name,
        @NotBlank String idCardMasked,
        @NotBlank String phoneMasked,
        @NotNull @Min(18) Integer age,
        @NotNull @DecimalMin("0.0") BigDecimal monthlyIncome,
        @NotNull @Min(0) Integer workYears,
        @NotNull @DecimalMin("0.0") BigDecimal existingDebt,
        @NotNull @Min(0) Integer overdueCount,
        @NotNull @Min(0) Integer assetProofCount
) {
}
