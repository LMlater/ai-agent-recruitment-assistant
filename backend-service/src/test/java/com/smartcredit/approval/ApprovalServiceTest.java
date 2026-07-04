package com.smartcredit.approval;

import com.smartcredit.audit.AuditLogService;
import com.smartcredit.common.BusinessException;
import com.smartcredit.loan.LoanApplication;
import com.smartcredit.loan.LoanApplicationMapper;
import com.smartcredit.loan.LoanStatus;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;

import java.util.List;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.mockito.ArgumentMatchers.eq;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;

@ExtendWith(MockitoExtension.class)
class ApprovalServiceTest {

    @Mock
    private ApprovalRecordMapper approvalRecordMapper;

    @Mock
    private LoanApplicationMapper loanApplicationMapper;

    @Mock
    private AuditLogService auditLogService;

    @InjectMocks
    private ApprovalService approvalService;

    @Test
    void aiReviewedApplicationCanBeApproved() {
        when(loanApplicationMapper.selectById(7L)).thenReturn(applicationWithStatus(LoanStatus.AI_REVIEWED));

        ApprovalRecord record = approvalService.approve(7L, 99L, "manual approve", "127.0.0.1");

        assertEquals(LoanStatus.AI_REVIEWED.name(), record.getFromStatus());
        assertEquals(LoanStatus.APPROVED.name(), record.getToStatus());
        verify(approvalRecordMapper).insert(record);
        verify(loanApplicationMapper).updateStatus(7L, LoanStatus.APPROVED.name());
        verify(auditLogService).record(eq(99L), eq("MANUAL_APPROVE"), eq("loan_application"), eq(7L), eq("manual approve"), eq("127.0.0.1"));
    }

    @Test
    void aiReviewedApplicationCanBeRejected() {
        when(loanApplicationMapper.selectById(7L)).thenReturn(applicationWithStatus(LoanStatus.AI_REVIEWED));

        ApprovalRecord record = approvalService.reject(7L, 99L, "manual reject", "127.0.0.1");

        assertEquals(LoanStatus.REJECTED.name(), record.getToStatus());
        verify(loanApplicationMapper).updateStatus(7L, LoanStatus.REJECTED.name());
    }

    @Test
    void submittedApplicationCanRequestMoreInformation() {
        when(loanApplicationMapper.selectById(7L)).thenReturn(applicationWithStatus(LoanStatus.SUBMITTED));

        ApprovalRecord record = approvalService.needMoreInfo(7L, 99L, "need income proof", "127.0.0.1");

        assertEquals(LoanStatus.SUBMITTED.name(), record.getFromStatus());
        assertEquals(LoanStatus.NEED_MORE_INFO.name(), record.getToStatus());
        verify(loanApplicationMapper).updateStatus(7L, LoanStatus.NEED_MORE_INFO.name());
    }

    @Test
    void resubmittedApplicationCanRequestMoreInformationBeforeAiReview() {
        when(loanApplicationMapper.selectById(7L)).thenReturn(applicationWithStatus(LoanStatus.RESUBMITTED));

        ApprovalRecord record = approvalService.needMoreInfo(7L, 99L, "still missing income proof", "127.0.0.1");

        assertEquals(LoanStatus.RESUBMITTED.name(), record.getFromStatus());
        assertEquals(LoanStatus.NEED_MORE_INFO.name(), record.getToStatus());
        verify(loanApplicationMapper).updateStatus(7L, LoanStatus.NEED_MORE_INFO.name());
    }

    @Test
    void draftApplicationCannotBeManuallyApprovedRejectedOrRequestedForMoreInfo() {
        assertManualTransitionsRejectedFrom(LoanStatus.DRAFT);
    }

    @Test
    void submittedApplicationCannotBeApprovedOrRejected() {
        when(loanApplicationMapper.selectById(7L)).thenReturn(applicationWithStatus(LoanStatus.SUBMITTED));
        assertThrows(BusinessException.class, () -> approvalService.approve(7L, 99L, "manual approve", "127.0.0.1"));

        when(loanApplicationMapper.selectById(7L)).thenReturn(applicationWithStatus(LoanStatus.SUBMITTED));
        assertThrows(BusinessException.class, () -> approvalService.reject(7L, 99L, "manual reject", "127.0.0.1"));
    }

    @Test
    void resubmittedOrMaterialUpdatedApplicationsCannotBeApprovedOrRejected() {
        for (LoanStatus status : List.of(LoanStatus.RESUBMITTED, LoanStatus.MATERIAL_UPDATED)) {
            when(loanApplicationMapper.selectById(7L)).thenReturn(applicationWithStatus(status));
            assertThrows(BusinessException.class, () -> approvalService.approve(7L, 99L, "manual approve", "127.0.0.1"));

            when(loanApplicationMapper.selectById(7L)).thenReturn(applicationWithStatus(status));
            assertThrows(BusinessException.class, () -> approvalService.reject(7L, 99L, "manual reject", "127.0.0.1"));
        }
    }

    @Test
    void materialUpdatedApplicationCannotRequestMoreInfoAgainBeforeResubmission() {
        when(loanApplicationMapper.selectById(7L)).thenReturn(applicationWithStatus(LoanStatus.MATERIAL_UPDATED));

        assertThrows(BusinessException.class, () -> approvalService.needMoreInfo(7L, 99L, "need info", "127.0.0.1"));
    }

    @Test
    void terminalStatusesCannotBeManuallyTransitionedAgain() {
        for (LoanStatus status : List.of(LoanStatus.APPROVED, LoanStatus.REJECTED, LoanStatus.NEED_MORE_INFO)) {
            assertManualTransitionsRejectedFrom(status);
        }
    }

    private void assertManualTransitionsRejectedFrom(LoanStatus status) {
        when(loanApplicationMapper.selectById(7L)).thenReturn(applicationWithStatus(status));
        assertThrows(BusinessException.class, () -> approvalService.approve(7L, 99L, "manual approve", "127.0.0.1"));

        when(loanApplicationMapper.selectById(7L)).thenReturn(applicationWithStatus(status));
        assertThrows(BusinessException.class, () -> approvalService.reject(7L, 99L, "manual reject", "127.0.0.1"));

        when(loanApplicationMapper.selectById(7L)).thenReturn(applicationWithStatus(status));
        assertThrows(BusinessException.class, () -> approvalService.needMoreInfo(7L, 99L, "need info", "127.0.0.1"));
    }

    private LoanApplication applicationWithStatus(LoanStatus status) {
        LoanApplication application = new LoanApplication();
        application.setId(7L);
        application.setStatus(status.name());
        return application;
    }
}
