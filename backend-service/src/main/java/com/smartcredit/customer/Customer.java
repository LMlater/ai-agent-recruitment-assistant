package com.smartcredit.customer;

import lombok.Data;

import java.math.BigDecimal;
import java.time.LocalDateTime;

@Data
public class Customer {
    private Long id;
    private String name;
    private String idCardMasked;
    private String phoneMasked;
    private Integer age;
    private BigDecimal monthlyIncome;
    private Integer workYears;
    private BigDecimal existingDebt;
    private Integer overdueCount;
    private Integer assetProofCount;
    private Boolean deleted;
    private LocalDateTime createdAt;
    private LocalDateTime updatedAt;
}
