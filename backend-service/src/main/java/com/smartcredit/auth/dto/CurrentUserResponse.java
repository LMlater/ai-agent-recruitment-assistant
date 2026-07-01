package com.smartcredit.auth.dto;

import java.util.List;

public record CurrentUserResponse(
        Long userId,
        String username,
        String displayName,
        List<String> roles
) {
}
