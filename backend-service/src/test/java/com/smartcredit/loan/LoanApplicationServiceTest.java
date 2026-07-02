package com.smartcredit.loan;

import com.smartcredit.audit.AuditLogService;
import com.smartcredit.common.BusinessException;
import com.smartcredit.customer.CustomerMapper;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;

import static org.junit.jupiter.api.Assertions.assertThrows;

@ExtendWith(MockitoExtension.class)
class LoanApplicationServiceTest {

    @Mock
    private LoanApplicationMapper loanApplicationMapper;

    @Mock
    private CustomerMapper customerMapper;

    @Mock
    private AuditLogService auditLogService;

    @InjectMocks
    private LoanApplicationService loanApplicationService;

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
}
