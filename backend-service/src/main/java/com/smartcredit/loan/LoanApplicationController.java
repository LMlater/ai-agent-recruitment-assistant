package com.smartcredit.loan;

import com.smartcredit.agent.AgentReviewService;
import com.smartcredit.agent.dto.AgentReviewResponse;
import com.smartcredit.common.PageResponse;
import com.smartcredit.common.Result;
import com.smartcredit.loan.dto.CreateLoanApplicationRequest;
import com.smartcredit.loan.dto.UpdateStatusRequest;
import com.smartcredit.loan.dto.UpdateMaterialsRequest;
import com.smartcredit.material.MaterialUpdateRecord;
import com.smartcredit.security.CurrentUser;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PatchMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

import java.util.List;

@RestController
@RequiredArgsConstructor
@RequestMapping("/api/loan-applications")
public class LoanApplicationController {
    private final LoanApplicationService loanApplicationService;
    private final AgentReviewService agentReviewService;

    @PostMapping
    public Result<LoanApplication> create(
            @Valid @RequestBody CreateLoanApplicationRequest request,
            HttpServletRequest servletRequest
    ) {
        return Result.success(loanApplicationService.create(request, CurrentUser.getRequiredUserId(), servletRequest.getRemoteAddr()));
    }

    @PostMapping("/{id}/submit")
    public Result<LoanApplication> submit(@PathVariable Long id, HttpServletRequest servletRequest) {
        return Result.success(loanApplicationService.submit(id, CurrentUser.getRequiredUserId(), servletRequest.getRemoteAddr()));
    }

    @PostMapping("/{id}/materials")
    public Result<LoanApplication> updateMaterials(
            @PathVariable Long id,
            @Valid @RequestBody UpdateMaterialsRequest request,
            HttpServletRequest servletRequest
    ) {
        return Result.success(loanApplicationService.updateMaterials(
                id,
                request.materialSummary(),
                CurrentUser.getRequiredUserId(),
                servletRequest.getRemoteAddr()
        ));
    }

    @PostMapping("/{id}/resubmit")
    public Result<LoanApplication> resubmit(@PathVariable Long id, HttpServletRequest servletRequest) {
        return Result.success(loanApplicationService.resubmit(id, CurrentUser.getRequiredUserId(), servletRequest.getRemoteAddr()));
    }

    @GetMapping("/{id}/material-updates")
    public Result<List<MaterialUpdateRecord>> materialUpdates(@PathVariable Long id) {
        return Result.success(loanApplicationService.materialUpdates(id));
    }

    @GetMapping("/{id}")
    public Result<LoanApplication> get(@PathVariable Long id) {
        return Result.success(loanApplicationService.get(id));
    }

    @GetMapping
    public Result<PageResponse<LoanApplication>> page(
            @RequestParam(defaultValue = "1") int page,
            @RequestParam(defaultValue = "10") int size
    ) {
        return Result.success(loanApplicationService.page(page, size));
    }

    @PatchMapping("/{id}/status")
    public Result<LoanApplication> updateStatus(@PathVariable Long id, @Valid @RequestBody UpdateStatusRequest request) {
        return Result.success(loanApplicationService.updateStatus(id, request.status()));
    }

    @PostMapping("/{id}/ai-review")
    public Result<AgentReviewResponse> aiReview(@PathVariable Long id, HttpServletRequest servletRequest) {
        return Result.success(agentReviewService.executeAiReview(id, CurrentUser.getRequiredUserId(), servletRequest.getRemoteAddr()));
    }
}
