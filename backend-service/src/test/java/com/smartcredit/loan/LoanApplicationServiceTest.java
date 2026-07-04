package com.smartcredit.loan;

import com.smartcredit.audit.AuditLogService;
import com.smartcredit.common.BusinessException;
import com.smartcredit.customer.CustomerMapper;
import com.smartcredit.material.MaterialUpdateRecord;
import com.smartcredit.material.MaterialUpdateRecordMapper;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.mockito.ArgumentCaptor.forClass;
import static org.mockito.ArgumentMatchers.eq;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;

@ExtendWith(MockitoExtension.class)
class LoanApplicationServiceTest {

    @Mock
    private LoanApplicationMapper loanApplicationMapper;

    @Mock
    private CustomerMapper customerMapper;

    @Mock
    private AuditLogService auditLogService;

    @Mock
    private MaterialUpdateRecordMapper materialUpdateRecordMapper;

    @InjectMocks
    private LoanApplicationService loanApplicationService;

    @Test
    void needMoreInfoApplicationCanUpdateMaterialsAndWritesAuditRecord() {
        when(loanApplicationMapper.selectById(7L))
                .thenReturn(applicationWithStatus(LoanStatus.NEED_MORE_INFO))
                .thenReturn(applicationWithStatus(LoanStatus.MATERIAL_UPDATED));

        LoanApplication application = loanApplicationService.updateMaterials(
                7L,
                "补充近 6 个月收入流水和资产证明摘要",
                99L,
                "127.0.0.1"
        );

        assertEquals(LoanStatus.MATERIAL_UPDATED.name(), application.getStatus());
        var recordCaptor = forClass(MaterialUpdateRecord.class);
        verify(materialUpdateRecordMapper).insert(recordCaptor.capture());
        assertEquals(7L, recordCaptor.getValue().getApplicationId());
        assertEquals(99L, recordCaptor.getValue().getOperatorId());
        assertEquals(LoanStatus.NEED_MORE_INFO.name(), recordCaptor.getValue().getFromStatus());
        assertEquals(LoanStatus.MATERIAL_UPDATED.name(), recordCaptor.getValue().getToStatus());
        verify(loanApplicationMapper).updateStatus(7L, LoanStatus.MATERIAL_UPDATED.name());
        verify(auditLogService).record(
                eq(99L),
                eq("UPDATE_MATERIALS"),
                eq("loan_application"),
                eq(7L),
                eq("补充近 6 个月收入流水和资产证明摘要"),
                eq("127.0.0.1")
        );
    }

    @Test
    void updateMaterialsRejectsStatusesOutsideNeedMoreInfo() {
        for (LoanStatus status : LoanStatus.values()) {
            if (status == LoanStatus.NEED_MORE_INFO) {
                continue;
            }
            when(loanApplicationMapper.selectById(7L)).thenReturn(applicationWithStatus(status));

            assertThrows(BusinessException.class, () -> loanApplicationService.updateMaterials(
                    7L,
                    "mock material summary",
                    99L,
                    "127.0.0.1"
            ));
        }
    }

    @Test
    void materialUpdatedApplicationCanBeResubmitted() {
        when(loanApplicationMapper.selectById(7L))
                .thenReturn(applicationWithStatus(LoanStatus.MATERIAL_UPDATED))
                .thenReturn(applicationWithStatus(LoanStatus.RESUBMITTED));

        LoanApplication application = loanApplicationService.resubmit(7L, 99L, "127.0.0.1");

        assertEquals(LoanStatus.RESUBMITTED.name(), application.getStatus());
        verify(loanApplicationMapper).updateStatus(7L, LoanStatus.RESUBMITTED.name());
        verify(auditLogService).record(
                eq(99L),
                eq("RESUBMIT_LOAN_APPLICATION"),
                eq("loan_application"),
                eq(7L),
                eq("Resubmitted loan application after material update"),
                eq("127.0.0.1")
        );
    }

    @Test
    void resubmitRejectsStatusesOutsideMaterialUpdated() {
        for (LoanStatus status : LoanStatus.values()) {
            if (status == LoanStatus.MATERIAL_UPDATED) {
                continue;
            }
            when(loanApplicationMapper.selectById(7L)).thenReturn(applicationWithStatus(status));

            assertThrows(BusinessException.class, () -> loanApplicationService.resubmit(7L, 99L, "127.0.0.1"));
        }
    }

    @Test
    void updateStatusRejectsFinalManualApprovalStatuses() {
        assertThrows(BusinessException.class, () -> loanApplicationService.updateStatus(1L, LoanStatus.APPROVED.name()));
        assertThrows(BusinessException.class, () -> loanApplicationService.updateStatus(1L, LoanStatus.REJECTED.name()));
        assertThrows(BusinessException.class, () -> loanApplicationService.updateStatus(1L, LoanStatus.NEED_MORE_INFO.name()));
    }

    @Test
    void updateStatusRejectsUnknownStatusAsBusinessError() {
        assertThrows(BusinessException.class, () -> loanApplicationService.updateStatus(1L, "ARCHIVED"));
    }

    private LoanApplication applicationWithStatus(LoanStatus status) {
        LoanApplication application = new LoanApplication();
        application.setId(7L);
        application.setStatus(status.name());
        return application;
    }
}
