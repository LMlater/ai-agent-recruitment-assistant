package com.smartcredit.auth;

import org.apache.ibatis.annotations.Insert;
import org.apache.ibatis.annotations.Mapper;
import org.apache.ibatis.annotations.Options;
import org.apache.ibatis.annotations.Param;
import org.apache.ibatis.annotations.Select;

import java.util.List;

@Mapper
public interface SysUserMapper {
    @Select("select * from sys_user where username = #{username} limit 1")
    SysUser selectByUsername(String username);

    @Select("select * from sys_user where id = #{id}")
    SysUser selectById(Long id);

    @Select("select count(1) from sys_user")
    long countUsers();

    @Insert("""
            insert into sys_user(username, password_hash, display_name, status)
            values(#{username}, #{passwordHash}, #{displayName}, #{status})
            """)
    @Options(useGeneratedKeys = true, keyProperty = "id")
    int insert(SysUser user);

    @Insert("insert ignore into sys_user_role(user_id, role_id) values(#{userId}, #{roleId})")
    int insertUserRole(@Param("userId") Long userId, @Param("roleId") Long roleId);

    @Select("""
            select r.role_code
            from sys_role r
            join sys_user_role ur on ur.role_id = r.id
            where ur.user_id = #{userId}
            order by r.id
            """)
    List<String> selectRoleCodes(Long userId);
}
