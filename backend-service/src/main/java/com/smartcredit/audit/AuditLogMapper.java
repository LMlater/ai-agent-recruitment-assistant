package com.smartcredit.audit;

import org.apache.ibatis.annotations.Insert;
import org.apache.ibatis.annotations.Mapper;
import org.apache.ibatis.annotations.Options;

@Mapper
public interface AuditLogMapper {
    @Insert("""
            insert into audit_log(user_id, action, resource_type, resource_id, detail, ip)
            values(#{userId}, #{action}, #{resourceType}, #{resourceId}, #{detail}, #{ip})
            """)
    @Options(useGeneratedKeys = true, keyProperty = "id")
    int insert(AuditLog auditLog);
}
