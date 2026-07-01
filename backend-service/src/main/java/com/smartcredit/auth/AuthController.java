package com.smartcredit.auth;

import com.smartcredit.auth.dto.CurrentUserResponse;
import com.smartcredit.auth.dto.InitAdminRequest;
import com.smartcredit.auth.dto.LoginRequest;
import com.smartcredit.auth.dto.LoginResponse;
import com.smartcredit.common.Result;
import com.smartcredit.security.CurrentUser;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequiredArgsConstructor
@RequestMapping("/api/auth")
public class AuthController {
    private final AuthService authService;

    @PostMapping("/init-admin")
    public Result<CurrentUserResponse> initAdmin(@Valid @RequestBody InitAdminRequest request) {
        return Result.success(authService.initAdmin(request));
    }

    @PostMapping("/login")
    public Result<LoginResponse> login(@Valid @RequestBody LoginRequest request, HttpServletRequest servletRequest) {
        return Result.success(authService.login(request, servletRequest.getRemoteAddr()));
    }

    @GetMapping("/me")
    public Result<CurrentUserResponse> me() {
        return Result.success(authService.currentUser(CurrentUser.getRequiredUserId()));
    }
}
