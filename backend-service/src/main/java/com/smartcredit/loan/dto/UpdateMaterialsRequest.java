package com.smartcredit.loan.dto;

import jakarta.validation.constraints.NotBlank;

public record UpdateMaterialsRequest(@NotBlank String materialSummary) {
}
