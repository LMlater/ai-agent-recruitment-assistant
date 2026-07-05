package com.smartcredit.loan;

import com.smartcredit.audit.AuditLogService;
import com.smartcredit.common.BusinessException;
import com.smartcredit.customer.Customer;
import com.smartcredit.customer.CustomerMapper;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.ArgumentCaptor;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;
import org.springframework.mock.web.MockMultipartFile;

import java.nio.charset.StandardCharsets;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.ArgumentMatchers.eq;
import static org.mockito.Mockito.doAnswer;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;

@ExtendWith(MockitoExtension.class)
class LoanApplicationImportServiceTest {

    @Mock
    private CustomerMapper customerMapper;

    @Mock
    private LoanApplicationService loanApplicationService;

    @Mock
    private AuditLogService auditLogService;

    @InjectMocks
    private LoanApplicationImportService importService;

    @Test
    void importsValidRowsAndSubmitsApplicationsWhileCollectingInvalidRows() throws Exception {
        doAnswer(invocation -> {
            Customer customer = invocation.getArgument(0);
            customer.setId(100L + customer.getAge());
            return 1;
        }).when(customerMapper).insert(any(Customer.class));
        when(loanApplicationService.create(any(), eq(9L), eq("127.0.0.1")))
                .thenAnswer(invocation -> {
                    LoanApplication application = new LoanApplication();
                    application.setId(501L);
                    application.setCustomerId(invocation.getArgument(0, com.smartcredit.loan.dto.CreateLoanApplicationRequest.class).customerId());
                    application.setStatus(LoanStatus.DRAFT.name());
                    return application;
                });
        when(loanApplicationService.submit(eq(501L), eq(9L), eq("127.0.0.1")))
                .thenAnswer(invocation -> {
                    LoanApplication application = new LoanApplication();
                    application.setId(501L);
                    application.setStatus(LoanStatus.SUBMITTED.name());
                    return application;
                });

        var result = importService.importCsv(
                csv("""
                        applicant_name,id_card_masked,phone_masked,age,monthly_income,work_years,existing_debt,overdue_count,asset_proof_count,loan_amount,term_months,purpose
                        Low Risk Demo,4401********2099,138****2099,32,12000,5,30000,0,2,80000,24,low risk interview demo loan
                        Bad Phone Demo,4401********3099,00000000000,35,8500,3,65000,1,1,120000,36,bad phone
                        """),
                9L,
                "127.0.0.1"
        );

        assertEquals(2, result.totalRows());
        assertEquals(1, result.successCount());
        assertEquals(1, result.failedCount());
        assertEquals(1, result.imported().size());
        assertEquals(LoanStatus.SUBMITTED.name(), result.imported().get(0).status());
        assertTrue(result.errors().get(0).contains("row 3"));
        assertTrue(result.errors().get(0).contains("完整手机号"));
        verify(loanApplicationService).submit(501L, 9L, "127.0.0.1");
        verify(auditLogService).record(eq(9L), eq("BATCH_IMPORT_CUSTOMER"), eq("customer"), any(), any(), eq("127.0.0.1"));
    }

    @Test
    void recordsFullIdCardAsRowErrorAndRejectsNonCsvFiles() {
        var result = importService.importCsv(
                csv("""
                        applicant_name,id_card_masked,phone_masked,age,monthly_income,work_years,existing_debt,overdue_count,asset_proof_count,loan_amount,term_months,purpose
                        Real Id Demo,000000000000000000,138****2099,32,12000,5,30000,0,2,80000,24,bad id
                        """),
                9L,
                "127.0.0.1"
        );
        assertEquals(1, result.totalRows());
        assertEquals(0, result.successCount());
        assertEquals(1, result.failedCount());
        assertTrue(result.errors().get(0).contains("完整身份证"));

        MockMultipartFile xlsx = new MockMultipartFile(
                "file",
                "loan_applications.xlsx",
                "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                new byte[0]
        );
        BusinessException xlsxError = assertThrows(BusinessException.class, () -> importService.importCsv(xlsx, 9L, "127.0.0.1"));
        assertTrue(xlsxError.getMessage().contains("当前版本优先支持 CSV 导入"));
    }

    @Test
    void capturesCreatedCustomerFieldsFromCsv() throws Exception {
        doAnswer(invocation -> {
            Customer customer = invocation.getArgument(0);
            customer.setId(42L);
            return 1;
        }).when(customerMapper).insert(any(Customer.class));
        when(loanApplicationService.create(any(), eq(9L), eq("127.0.0.1"))).thenAnswer(invocation -> {
            LoanApplication application = new LoanApplication();
            application.setId(88L);
            return application;
        });
        when(loanApplicationService.submit(eq(88L), eq(9L), eq("127.0.0.1"))).thenAnswer(invocation -> {
            LoanApplication application = new LoanApplication();
            application.setId(88L);
            application.setStatus(LoanStatus.SUBMITTED.name());
            return application;
        });

        importService.importCsv(
                csv("""
                        applicant_name,id_card_masked,phone_masked,age,monthly_income,work_years,existing_debt,overdue_count,asset_proof_count,loan_amount,term_months,purpose
                        Medium Risk Demo,4401********3099,138****3099,35,8500,3,65000,1,1,120000,36,medium risk interview demo loan
                        """),
                9L,
                "127.0.0.1"
        );

        ArgumentCaptor<Customer> customerCaptor = ArgumentCaptor.forClass(Customer.class);
        verify(customerMapper).insert(customerCaptor.capture());
        assertEquals("Medium Risk Demo", customerCaptor.getValue().getName());
        assertEquals("4401********3099", customerCaptor.getValue().getIdCardMasked());
        assertEquals("138****3099", customerCaptor.getValue().getPhoneMasked());
        assertEquals(35, customerCaptor.getValue().getAge());
    }

    private MockMultipartFile csv(String content) {
        return new MockMultipartFile(
                "file",
                "loan_applications.csv",
                "text/csv",
                content.getBytes(StandardCharsets.UTF_8)
        );
    }
}
