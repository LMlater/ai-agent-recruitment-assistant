package com.smartcredit.loan.dto;

import java.math.BigDecimal;

public record ImportedLoanApplicationItem(
        Long customerId,
        Long applicationId,
        String applicantName,
        String status,
        BigDecimal amount,
        Integer termMonths,
        String purpose
) {
}
