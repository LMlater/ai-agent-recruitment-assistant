package com.smartcredit.audit;

import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;

@Service
@RequiredArgsConstructor
public class AuditLogService {
    private final AuditLogMapper auditLogMapper;

    public void record(Long userId, String action, String resourceType, Long resourceId, String detail, String ip) {
        AuditLog auditLog = new AuditLog();
        auditLog.setUserId(userId);
        auditLog.setAction(action);
        auditLog.setResourceType(resourceType);
        auditLog.setResourceId(resourceId);
        auditLog.setDetail(detail);
        auditLog.setIp(ip);
        auditLogMapper.insert(auditLog);
    }
}
