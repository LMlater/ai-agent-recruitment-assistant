package com.smartcredit.audit;

import lombok.Data;

import java.time.LocalDateTime;

@Data
public class AuditLog {
    private Long id;
    private Long userId;
    private String action;
    private String resourceType;
    private Long resourceId;
    private String detail;
    private String ip;
    private LocalDateTime createdAt;
}
