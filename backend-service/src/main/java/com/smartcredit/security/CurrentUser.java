package com.smartcredit.security;

import com.smartcredit.common.BusinessException;

public final class CurrentUser {
    private static final ThreadLocal<Long> USER_ID = new ThreadLocal<>();

    private CurrentUser() {
    }

    public static void setUserId(Long userId) {
        USER_ID.set(userId);
    }

    public static Long getRequiredUserId() {
        Long userId = USER_ID.get();
        if (userId == null) {
            throw new BusinessException("User is not authenticated");
        }
        return userId;
    }

    public static void clear() {
        USER_ID.remove();
    }
}
