package com.smartcredit.approval;

import lombok.Data;

import java.time.LocalDateTime;

@Data
public class ApprovalRecord {
    private Long id;
    private Long applicationId;
    private Long operatorId;
    private String fromStatus;
    private String toStatus;
    private String comment;
    private LocalDateTime createdAt;
}
