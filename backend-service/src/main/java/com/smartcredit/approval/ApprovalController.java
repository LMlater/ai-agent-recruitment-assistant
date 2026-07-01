package com.smartcredit.approval;

import com.smartcredit.approval.dto.ApprovalRequest;
import com.smartcredit.common.Result;
import com.smartcredit.security.CurrentUser;
import jakarta.servlet.http.HttpServletRequest;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import java.util.List;

@RestController
@RequiredArgsConstructor
@RequestMapping("/api/approvals")
public class ApprovalController {
    private final ApprovalService approvalService;

    @PostMapping("/{applicationId}/approve")
    public Result<ApprovalRecord> approve(
            @PathVariable Long applicationId,
            @RequestBody ApprovalRequest request,
            HttpServletRequest servletRequest
    ) {
        return Result.success(approvalService.approve(applicationId, CurrentUser.getRequiredUserId(), request.comment(), servletRequest.getRemoteAddr()));
    }

    @PostMapping("/{applicationId}/reject")
    public Result<ApprovalRecord> reject(
            @PathVariable Long applicationId,
            @RequestBody ApprovalRequest request,
            HttpServletRequest servletRequest
    ) {
        return Result.success(approvalService.reject(applicationId, CurrentUser.getRequiredUserId(), request.comment(), servletRequest.getRemoteAddr()));
    }

    @PostMapping("/{applicationId}/need-more-info")
    public Result<ApprovalRecord> needMoreInfo(
            @PathVariable Long applicationId,
            @RequestBody ApprovalRequest request,
            HttpServletRequest servletRequest
    ) {
        return Result.success(approvalService.needMoreInfo(applicationId, CurrentUser.getRequiredUserId(), request.comment(), servletRequest.getRemoteAddr()));
    }

    @GetMapping("/{applicationId}/history")
    public Result<List<ApprovalRecord>> history(@PathVariable Long applicationId) {
        return Result.success(approvalService.history(applicationId));
    }
}
