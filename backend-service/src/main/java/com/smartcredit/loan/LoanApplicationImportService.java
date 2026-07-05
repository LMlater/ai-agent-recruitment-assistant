package com.smartcredit.loan;

import com.smartcredit.audit.AuditLogService;
import com.smartcredit.common.BusinessException;
import com.smartcredit.customer.Customer;
import com.smartcredit.customer.CustomerMapper;
import com.smartcredit.loan.dto.BatchImportLoanApplicationResult;
import com.smartcredit.loan.dto.CreateLoanApplicationRequest;
import com.smartcredit.loan.dto.ImportedLoanApplicationItem;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.web.multipart.MultipartFile;

import java.io.IOException;
import java.math.BigDecimal;
import java.nio.charset.StandardCharsets;
import java.util.ArrayList;
import java.util.List;
import java.util.regex.Pattern;

@Service
@RequiredArgsConstructor
public class LoanApplicationImportService {
    public static final String CSV_TEMPLATE = """
            applicant_name,id_card_masked,phone_masked,age,monthly_income,work_years,existing_debt,overdue_count,asset_proof_count,loan_amount,term_months,purpose
            Low Risk Demo,4401********2099,138****2099,32,12000,5,30000,0,2,80000,24,low risk interview demo loan
            Medium Risk Demo,4401********3099,138****3099,35,8500,3,65000,1,1,120000,36,medium risk interview demo loan
            High Risk Demo,4401********9099,139****9099,24,4200,1,90000,3,0,180000,36,high risk interview demo loan
            """;
    private static final long MAX_FILE_BYTES = 2L * 1024L * 1024L;
    private static final String EXPECTED_HEADER = "applicant_name,id_card_masked,phone_masked,age,monthly_income,work_years,existing_debt,overdue_count,asset_proof_count,loan_amount,term_months,purpose";
    private static final Pattern FULL_ID_CARD = Pattern.compile("^\\d{17}[\\dXx]$|^\\d{18}$");
    private static final Pattern FULL_PHONE = Pattern.compile("^\\d{11}$");

    private final CustomerMapper customerMapper;
    private final LoanApplicationService loanApplicationService;
    private final AuditLogService auditLogService;

    public BatchImportLoanApplicationResult importCsv(MultipartFile file, Long userId, String ip) {
        validateFile(file);
        List<String> lines = readLines(file);
        if (lines.isEmpty() || lines.get(0).trim().isBlank()) {
            throw new BusinessException("CSV header is required");
        }
        String header = normalizeHeader(lines.get(0));
        if (!EXPECTED_HEADER.equals(header)) {
            throw new BusinessException("CSV header 不正确，请使用系统模板。Expected: " + EXPECTED_HEADER);
        }

        List<ImportedLoanApplicationItem> imported = new ArrayList<>();
        List<String> errors = new ArrayList<>();
        int totalRows = 0;
        for (int index = 1; index < lines.size(); index++) {
            String line = lines.get(index);
            if (line == null || line.trim().isBlank()) {
                continue;
            }
            totalRows++;
            int rowNumber = index + 1;
            try {
                imported.add(importRow(parseCsvLine(line), userId, ip));
            } catch (RuntimeException exception) {
                errors.add("row " + rowNumber + ": " + exception.getMessage());
            }
        }
        return new BatchImportLoanApplicationResult(
                totalRows,
                imported.size(),
                errors.size(),
                List.copyOf(imported),
                List.copyOf(errors)
        );
    }

    private void validateFile(MultipartFile file) {
        if (file == null) {
            throw new BusinessException("CSV file is required");
        }
        String filename = file.getOriginalFilename() == null ? "" : file.getOriginalFilename().toLowerCase();
        if (filename.endsWith(".xlsx")) {
            throw new BusinessException("当前版本优先支持 CSV 导入，Excel 模板作为后续增强；请先使用 CSV 模板。");
        }
        if (!filename.endsWith(".csv")) {
            throw new BusinessException("Only .csv files are supported for batch import");
        }
        if (file.isEmpty()) {
            throw new BusinessException("CSV file is required");
        }
        if (file.getSize() > MAX_FILE_BYTES) {
            throw new BusinessException("CSV file must be <= 2MB");
        }
    }

    private List<String> readLines(MultipartFile file) {
        try {
            String text = new String(file.getBytes(), StandardCharsets.UTF_8);
            if (text.startsWith("\uFEFF")) {
                text = text.substring(1);
            }
            return text.lines().toList();
        } catch (IOException exception) {
            throw new BusinessException("Failed to read CSV file");
        }
    }

    private String normalizeHeader(String rawHeader) {
        return String.join(",", parseCsvLine(rawHeader).stream().map(String::trim).toList());
    }

    private ImportedLoanApplicationItem importRow(List<String> columns, Long userId, String ip) {
        if (columns.size() != 12) {
            throw new BusinessException("expected 12 columns but got " + columns.size());
        }
        String applicantName = required(columns, 0, "applicant_name");
        String idCardMasked = required(columns, 1, "id_card_masked");
        String phoneMasked = required(columns, 2, "phone_masked");
        Integer age = positiveInt(columns, 3, "age");
        BigDecimal monthlyIncome = positiveDecimal(columns, 4, "monthly_income");
        Integer workYears = nonNegativeInt(columns, 5, "work_years");
        BigDecimal existingDebt = nonNegativeDecimal(columns, 6, "existing_debt");
        Integer overdueCount = nonNegativeInt(columns, 7, "overdue_count");
        Integer assetProofCount = nonNegativeInt(columns, 8, "asset_proof_count");
        BigDecimal loanAmount = positiveDecimal(columns, 9, "loan_amount");
        Integer termMonths = positiveInt(columns, 10, "term_months");
        String purpose = required(columns, 11, "purpose");

        if (age < 18 || age > 70) {
            throw new BusinessException("age must be between 18 and 70");
        }
        if (FULL_ID_CARD.matcher(idCardMasked).matches()) {
            throw new BusinessException("id_card_masked 不能是完整身份证，请上传脱敏证件号");
        }
        if (FULL_PHONE.matcher(phoneMasked).matches()) {
            throw new BusinessException("phone_masked 不能是完整手机号，请上传脱敏手机号");
        }

        Customer customer = new Customer();
        customer.setName(applicantName);
        customer.setIdCardMasked(idCardMasked);
        customer.setPhoneMasked(phoneMasked);
        customer.setAge(age);
        customer.setMonthlyIncome(monthlyIncome);
        customer.setWorkYears(workYears);
        customer.setExistingDebt(existingDebt);
        customer.setOverdueCount(overdueCount);
        customer.setAssetProofCount(assetProofCount);
        customerMapper.insert(customer);
        auditLogService.record(userId, "BATCH_IMPORT_CUSTOMER", "customer", customer.getId(), "Batch imported mock customer", ip);

        LoanApplication created = loanApplicationService.create(
                new CreateLoanApplicationRequest(customer.getId(), loanAmount, termMonths, purpose),
                userId,
                ip
        );
        LoanApplication submitted = loanApplicationService.submit(created.getId(), userId, ip);
        return new ImportedLoanApplicationItem(
                customer.getId(),
                submitted.getId(),
                applicantName,
                submitted.getStatus(),
                loanAmount,
                termMonths,
                purpose
        );
    }

    private String required(List<String> columns, int index, String name) {
        String value = columns.get(index).trim();
        if (value.isBlank()) {
            throw new BusinessException(name + " is required");
        }
        return value;
    }

    private Integer positiveInt(List<String> columns, int index, String name) {
        int value = parseInt(columns, index, name);
        if (value <= 0) {
            throw new BusinessException(name + " must be > 0");
        }
        return value;
    }

    private Integer nonNegativeInt(List<String> columns, int index, String name) {
        int value = parseInt(columns, index, name);
        if (value < 0) {
            throw new BusinessException(name + " must be >= 0");
        }
        return value;
    }

    private int parseInt(List<String> columns, int index, String name) {
        try {
            return Integer.parseInt(required(columns, index, name));
        } catch (NumberFormatException exception) {
            throw new BusinessException(name + " must be a number");
        }
    }

    private BigDecimal positiveDecimal(List<String> columns, int index, String name) {
        BigDecimal value = parseDecimal(columns, index, name);
        if (value.compareTo(BigDecimal.ZERO) <= 0) {
            throw new BusinessException(name + " must be > 0");
        }
        return value;
    }

    private BigDecimal nonNegativeDecimal(List<String> columns, int index, String name) {
        BigDecimal value = parseDecimal(columns, index, name);
        if (value.compareTo(BigDecimal.ZERO) < 0) {
            throw new BusinessException(name + " must be >= 0");
        }
        return value;
    }

    private BigDecimal parseDecimal(List<String> columns, int index, String name) {
        try {
            return new BigDecimal(required(columns, index, name));
        } catch (NumberFormatException exception) {
            throw new BusinessException(name + " must be a number");
        }
    }

    private List<String> parseCsvLine(String line) {
        List<String> values = new ArrayList<>();
        StringBuilder current = new StringBuilder();
        boolean inQuotes = false;
        for (int i = 0; i < line.length(); i++) {
            char ch = line.charAt(i);
            if (ch == '"') {
                if (inQuotes && i + 1 < line.length() && line.charAt(i + 1) == '"') {
                    current.append('"');
                    i++;
                } else {
                    inQuotes = !inQuotes;
                }
            } else if (ch == ',' && !inQuotes) {
                values.add(current.toString().trim());
                current.setLength(0);
            } else {
                current.append(ch);
            }
        }
        values.add(current.toString().trim());
        return values;
    }
}
