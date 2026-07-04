package com.smartcredit.approval;

import com.smartcredit.audit.AuditLogService;
import com.smartcredit.common.BusinessException;
import com.smartcredit.loan.LoanApplication;
import com.smartcredit.loan.LoanApplicationMapper;
import com.smartcredit.loan.LoanStatus;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;

@Service
@RequiredArgsConstructor
public class ApprovalService {
    private final ApprovalRecordMapper approvalRecordMapper;
    private final LoanApplicationMapper loanApplicationMapper;
    private final AuditLogService auditLogService;

    @Transactional
    public ApprovalRecord approve(Long applicationId, Long operatorId, String comment, String ip) {
        return manualTransition(applicationId, operatorId, LoanStatus.APPROVED, comment, "MANUAL_APPROVE", ip);
    }

    @Transactional
    public ApprovalRecord reject(Long applicationId, Long operatorId, String comment, String ip) {
        return manualTransition(applicationId, operatorId, LoanStatus.REJECTED, comment, "MANUAL_REJECT", ip);
    }

    @Transactional
    public ApprovalRecord needMoreInfo(Long applicationId, Long operatorId, String comment, String ip) {
        return manualTransition(applicationId, operatorId, LoanStatus.NEED_MORE_INFO, comment, "MANUAL_NEED_MORE_INFO", ip);
    }

    public List<ApprovalRecord> history(Long applicationId) {
        return approvalRecordMapper.selectByApplicationId(applicationId);
    }

    private ApprovalRecord manualTransition(Long applicationId, Long operatorId, LoanStatus toStatus, String comment, String action, String ip) {
        LoanApplication application = loanApplicationMapper.selectById(applicationId);
        if (application == null) {
            throw new BusinessException("Loan application not found");
        }
        validateManualTransition(application.getStatus(), toStatus);
        ApprovalRecord record = new ApprovalRecord();
        record.setApplicationId(applicationId);
        record.setOperatorId(operatorId);
        record.setFromStatus(application.getStatus());
        record.setToStatus(toStatus.name());
        record.setComment(comment);
        approvalRecordMapper.insert(record);
        loanApplicationMapper.updateStatus(applicationId, toStatus.name());
        auditLogService.record(operatorId, action, "loan_application", applicationId, comment, ip);
        return record;
    }

    private void validateManualTransition(String fromStatus, LoanStatus toStatus) {
        if (toStatus == LoanStatus.APPROVED || toStatus == LoanStatus.REJECTED) {
            if (!LoanStatus.AI_REVIEWED.name().equals(fromStatus)) {
                throw new BusinessException("Only AI_REVIEWED applications can be approved or rejected");
            }
            return;
        }
        if (toStatus == LoanStatus.NEED_MORE_INFO) {
            if (!LoanStatus.SUBMITTED.name().equals(fromStatus)
                    && !LoanStatus.RESUBMITTED.name().equals(fromStatus)
                    && !LoanStatus.AI_REVIEWED.name().equals(fromStatus)) {
                throw new BusinessException("Only SUBMITTED, RESUBMITTED or AI_REVIEWED applications can request more information");
            }
            return;
        }
        throw new BusinessException("Unsupported manual approval transition");
    }
}
