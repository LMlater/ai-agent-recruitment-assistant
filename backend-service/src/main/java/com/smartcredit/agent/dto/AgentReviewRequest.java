package com.smartcredit.agent.dto;

import com.fasterxml.jackson.annotation.JsonProperty;
import com.smartcredit.customer.Customer;
import com.smartcredit.loan.LoanApplication;
import lombok.Data;

import java.math.BigDecimal;

@Data
public class AgentReviewRequest {
    @JsonProperty("application_id")
    private Long applicationId;
    private CustomerPayload customer;
    @JsonProperty("loan_application")
    private LoanApplicationPayload loanApplication;

    public static AgentReviewRequest from(LoanApplication application, Customer customer) {
        AgentReviewRequest request = new AgentReviewRequest();
        request.setApplicationId(application.getId());
        request.setCustomer(CustomerPayload.from(customer));
        request.setLoanApplication(LoanApplicationPayload.from(application));
        return request;
    }

    @Data
    public static class CustomerPayload {
        private Long id;
        private Integer age;
        @JsonProperty("monthly_income")
        private BigDecimal monthlyIncome;
        @JsonProperty("work_years")
        private Integer workYears;
        @JsonProperty("existing_debt")
        private BigDecimal existingDebt;
        @JsonProperty("overdue_count")
        private Integer overdueCount;
        @JsonProperty("asset_proof_count")
        private Integer assetProofCount;

        static CustomerPayload from(Customer customer) {
            CustomerPayload payload = new CustomerPayload();
            payload.setId(customer.getId());
            payload.setAge(customer.getAge());
            payload.setMonthlyIncome(customer.getMonthlyIncome());
            payload.setWorkYears(customer.getWorkYears());
            payload.setExistingDebt(customer.getExistingDebt());
            payload.setOverdueCount(customer.getOverdueCount());
            payload.setAssetProofCount(customer.getAssetProofCount());
            return payload;
        }
    }

    @Data
    public static class LoanApplicationPayload {
        private BigDecimal amount;
        @JsonProperty("term_months")
        private Integer termMonths;
        private String purpose;

        static LoanApplicationPayload from(LoanApplication application) {
            LoanApplicationPayload payload = new LoanApplicationPayload();
            payload.setAmount(application.getAmount());
            payload.setTermMonths(application.getTermMonths());
            payload.setPurpose(application.getPurpose());
            return payload;
        }
    }
}
