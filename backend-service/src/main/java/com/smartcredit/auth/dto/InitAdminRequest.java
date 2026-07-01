package com.smartcredit.auth.dto;

import jakarta.validation.constraints.NotBlank;

public record InitAdminRequest(
        @NotBlank String username,
        @NotBlank String password,
        @NotBlank String displayName
) {
}
