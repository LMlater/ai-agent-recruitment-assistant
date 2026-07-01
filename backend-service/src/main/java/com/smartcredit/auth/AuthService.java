package com.smartcredit.auth;

import com.smartcredit.audit.AuditLogService;
import com.smartcredit.auth.dto.CurrentUserResponse;
import com.smartcredit.auth.dto.InitAdminRequest;
import com.smartcredit.auth.dto.LoginRequest;
import com.smartcredit.auth.dto.LoginResponse;
import com.smartcredit.common.BusinessException;
import com.smartcredit.security.JwtTokenProvider;
import lombok.RequiredArgsConstructor;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;

@Service
@RequiredArgsConstructor
public class AuthService {
    private static final long ADMIN_ROLE_ID = 1L;

    private final SysUserMapper sysUserMapper;
    private final PasswordEncoder passwordEncoder;
    private final JwtTokenProvider jwtTokenProvider;
    private final AuditLogService auditLogService;

    @Transactional
    public CurrentUserResponse initAdmin(InitAdminRequest request) {
        if (sysUserMapper.countUsers() > 0) {
            throw new BusinessException("Admin initialization is only allowed when no users exist");
        }
        SysUser user = new SysUser();
        user.setUsername(request.username());
        user.setPasswordHash(passwordEncoder.encode(request.password()));
        user.setDisplayName(request.displayName());
        user.setStatus("ACTIVE");
        sysUserMapper.insert(user);
        sysUserMapper.insertUserRole(user.getId(), ADMIN_ROLE_ID);
        return currentUser(user.getId());
    }

    public LoginResponse login(LoginRequest request, String ip) {
        SysUser user = sysUserMapper.selectByUsername(request.username());
        if (user == null || !"ACTIVE".equals(user.getStatus())) {
            throw new BusinessException("Invalid username or password");
        }
        if (!passwordEncoder.matches(request.password(), user.getPasswordHash())) {
            throw new BusinessException("Invalid username or password");
        }
        List<String> roles = sysUserMapper.selectRoleCodes(user.getId());
        auditLogService.record(user.getId(), "LOGIN", "sys_user", user.getId(), "User login", ip);
        return new LoginResponse(
                jwtTokenProvider.generateToken(user.getId(), user.getUsername()),
                user.getId(),
                user.getUsername(),
                user.getDisplayName(),
                roles
        );
    }

    public CurrentUserResponse currentUser(Long userId) {
        SysUser user = sysUserMapper.selectById(userId);
        if (user == null) {
            throw new BusinessException("User not found");
        }
        return new CurrentUserResponse(
                user.getId(),
                user.getUsername(),
                user.getDisplayName(),
                sysUserMapper.selectRoleCodes(userId)
        );
    }
}
