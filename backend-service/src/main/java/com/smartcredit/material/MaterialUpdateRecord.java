package com.smartcredit.material;

import lombok.Data;

import java.time.LocalDateTime;

@Data
public class MaterialUpdateRecord {
    private Long id;
    private Long applicationId;
    private Long operatorId;
    private String materialSummary;
    private String fromStatus;
    private String toStatus;
    private LocalDateTime createdAt;
}
