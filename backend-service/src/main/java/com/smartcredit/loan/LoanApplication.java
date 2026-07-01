package com.smartcredit.loan;

import lombok.Data;

import java.math.BigDecimal;
import java.time.LocalDateTime;

@Data
public class LoanApplication {
    private Long id;
    private Long customerId;
    private BigDecimal amount;
    private Integer termMonths;
    private String purpose;
    private String status;
    private Integer riskScore;
    private String riskLevel;
    private String aiDecision;
    private String aiSummary;
    private Long createdBy;
    private LocalDateTime createdAt;
    private LocalDateTime updatedAt;
}
