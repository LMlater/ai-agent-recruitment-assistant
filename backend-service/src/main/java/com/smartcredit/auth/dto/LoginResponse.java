package com.smartcredit.auth.dto;

import java.util.List;

public record LoginResponse(
        String token,
        Long userId,
        String username,
        String displayName,
        List<String> roles
) {
}
