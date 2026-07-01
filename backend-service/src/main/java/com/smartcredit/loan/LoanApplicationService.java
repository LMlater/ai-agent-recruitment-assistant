package com.smartcredit.loan;

import com.smartcredit.audit.AuditLogService;
import com.smartcredit.common.BusinessException;
import com.smartcredit.common.PageResponse;
import com.smartcredit.customer.CustomerMapper;
import com.smartcredit.loan.dto.CreateLoanApplicationRequest;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

@Service
@RequiredArgsConstructor
public class LoanApplicationService {
    private final LoanApplicationMapper loanApplicationMapper;
    private final CustomerMapper customerMapper;
    private final AuditLogService auditLogService;

    @Transactional
    public LoanApplication create(CreateLoanApplicationRequest request, Long userId, String ip) {
        if (customerMapper.selectById(request.customerId()) == null) {
            throw new BusinessException("Customer not found");
        }
        LoanApplication application = new LoanApplication();
        application.setCustomerId(request.customerId());
        application.setAmount(request.amount());
        application.setTermMonths(request.termMonths());
        application.setPurpose(request.purpose());
        application.setStatus(LoanStatus.DRAFT.name());
        application.setCreatedBy(userId);
        loanApplicationMapper.insert(application);
        auditLogService.record(userId, "CREATE_LOAN_APPLICATION", "loan_application", application.getId(), "Created loan application", ip);
        return get(application.getId());
    }

    @Transactional
    public LoanApplication submit(Long id, Long userId, String ip) {
        LoanApplication application = get(id);
        if (!LoanStatus.DRAFT.name().equals(application.getStatus())) {
            throw new BusinessException("Only DRAFT applications can be submitted");
        }
        loanApplicationMapper.updateStatus(id, LoanStatus.SUBMITTED.name());
        auditLogService.record(userId, "SUBMIT_LOAN_APPLICATION", "loan_application", id, "Submitted loan application", ip);
        return get(id);
    }

    public LoanApplication get(Long id) {
        LoanApplication application = loanApplicationMapper.selectById(id);
        if (application == null) {
            throw new BusinessException("Loan application not found");
        }
        return application;
    }

    public PageResponse<LoanApplication> page(int page, int size) {
        int safePage = Math.max(page, 1);
        int safeSize = Math.max(1, Math.min(size, 100));
        return new PageResponse<>(
                loanApplicationMapper.selectPage((safePage - 1) * safeSize, safeSize),
                loanApplicationMapper.countAll(),
                safePage,
                safeSize
        );
    }

    public LoanApplication updateStatus(Long id, String status) {
        LoanStatus nextStatus = LoanStatus.valueOf(status);
        if (nextStatus == LoanStatus.APPROVED || nextStatus == LoanStatus.REJECTED) {
            throw new BusinessException("Use manual approval APIs for final decisions");
        }
        get(id);
        loanApplicationMapper.updateStatus(id, nextStatus.name());
        return get(id);
    }
}
