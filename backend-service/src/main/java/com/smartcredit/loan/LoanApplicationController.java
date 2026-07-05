package com.smartcredit.loan;

import com.smartcredit.agent.AgentReviewService;
import com.smartcredit.agent.dto.AgentReviewResponse;
import com.smartcredit.common.PageResponse;
import com.smartcredit.common.Result;
import com.smartcredit.loan.dto.BatchImportLoanApplicationResult;
import com.smartcredit.loan.dto.CreateLoanApplicationRequest;
import com.smartcredit.loan.dto.UpdateStatusRequest;
import com.smartcredit.loan.dto.UpdateMaterialsRequest;
import com.smartcredit.material.MaterialUpdateRecord;
import com.smartcredit.security.CurrentUser;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.validation.Valid;
import org.springframework.http.HttpHeaders;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PatchMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.web.multipart.MultipartFile;

import java.nio.charset.StandardCharsets;
import java.util.List;

@RestController
@RequiredArgsConstructor
@RequestMapping("/api/loan-applications")
public class LoanApplicationController {
    private final LoanApplicationService loanApplicationService;
    private final LoanApplicationImportService loanApplicationImportService;
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

    @GetMapping(value = "/batch-import-template", produces = "text/csv")
    public ResponseEntity<String> batchImportTemplate() {
        return ResponseEntity.ok()
                .header(HttpHeaders.CONTENT_DISPOSITION, "attachment; filename=loan_applications_sample.csv")
                .contentType(new MediaType("text", "csv", StandardCharsets.UTF_8))
                .body(LoanApplicationImportService.CSV_TEMPLATE);
    }

    @PostMapping(value = "/batch-import", consumes = MediaType.MULTIPART_FORM_DATA_VALUE)
    public Result<BatchImportLoanApplicationResult> batchImport(
            @RequestParam("file") MultipartFile file,
            HttpServletRequest servletRequest
    ) {
        return Result.success(loanApplicationImportService.importCsv(
                file,
                CurrentUser.getRequiredUserId(),
                servletRequest.getRemoteAddr()
        ));
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
