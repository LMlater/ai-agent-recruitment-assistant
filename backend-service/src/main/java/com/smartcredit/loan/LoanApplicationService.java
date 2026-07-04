package com.smartcredit.loan;

import com.smartcredit.audit.AuditLogService;
import com.smartcredit.common.BusinessException;
import com.smartcredit.common.PageResponse;
import com.smartcredit.customer.CustomerMapper;
import com.smartcredit.loan.dto.CreateLoanApplicationRequest;
import com.smartcredit.material.MaterialUpdateRecord;
import com.smartcredit.material.MaterialUpdateRecordMapper;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;

@Service
@RequiredArgsConstructor
public class LoanApplicationService {
    private final LoanApplicationMapper loanApplicationMapper;
    private final CustomerMapper customerMapper;
    private final AuditLogService auditLogService;
    private final MaterialUpdateRecordMapper materialUpdateRecordMapper;

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

    @Transactional
    public LoanApplication updateMaterials(Long id, String materialSummary, Long userId, String ip) {
        LoanApplication application = get(id);
        if (!LoanStatus.NEED_MORE_INFO.name().equals(application.getStatus())) {
            throw new BusinessException("Only NEED_MORE_INFO applications can update materials");
        }

        MaterialUpdateRecord record = new MaterialUpdateRecord();
        record.setApplicationId(id);
        record.setOperatorId(userId);
        record.setMaterialSummary(materialSummary);
        record.setFromStatus(application.getStatus());
        record.setToStatus(LoanStatus.MATERIAL_UPDATED.name());
        materialUpdateRecordMapper.insert(record);

        loanApplicationMapper.updateStatus(id, LoanStatus.MATERIAL_UPDATED.name());
        auditLogService.record(userId, "UPDATE_MATERIALS", "loan_application", id, materialSummary, ip);
        return get(id);
    }

    @Transactional
    public LoanApplication resubmit(Long id, Long userId, String ip) {
        LoanApplication application = get(id);
        if (!LoanStatus.MATERIAL_UPDATED.name().equals(application.getStatus())) {
            throw new BusinessException("Only MATERIAL_UPDATED applications can be resubmitted");
        }
        loanApplicationMapper.updateStatus(id, LoanStatus.RESUBMITTED.name());
        auditLogService.record(
                userId,
                "RESUBMIT_LOAN_APPLICATION",
                "loan_application",
                id,
                "Resubmitted loan application after material update",
                ip
        );
        return get(id);
    }

    public List<MaterialUpdateRecord> materialUpdates(Long id) {
        get(id);
        return materialUpdateRecordMapper.selectByApplicationId(id);
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
        LoanStatus nextStatus;
        try {
            nextStatus = LoanStatus.valueOf(status);
        } catch (IllegalArgumentException | NullPointerException exception) {
            throw new BusinessException("Unsupported loan application status: " + status);
        }
        // Final approval states must be confirmed by a human reviewer and leave approval_record traces.
        if (nextStatus == LoanStatus.APPROVED || nextStatus == LoanStatus.REJECTED || nextStatus == LoanStatus.NEED_MORE_INFO) {
            throw new BusinessException("Use manual approval APIs for final approval decisions");
        }
        if (nextStatus == LoanStatus.MATERIAL_UPDATED || nextStatus == LoanStatus.RESUBMITTED) {
            throw new BusinessException("Use material reassessment APIs for material update and resubmission");
        }
        get(id);
        loanApplicationMapper.updateStatus(id, nextStatus.name());
        return get(id);
    }
}
