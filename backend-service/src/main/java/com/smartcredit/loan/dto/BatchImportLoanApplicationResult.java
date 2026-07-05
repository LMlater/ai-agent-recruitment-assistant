package com.smartcredit.loan.dto;

import java.util.List;

public record BatchImportLoanApplicationResult(
        int totalRows,
        int successCount,
        int failedCount,
        List<ImportedLoanApplicationItem> imported,
        List<String> errors
) {
}
