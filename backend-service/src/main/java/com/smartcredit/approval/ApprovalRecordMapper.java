package com.smartcredit.approval;

import org.apache.ibatis.annotations.Insert;
import org.apache.ibatis.annotations.Mapper;
import org.apache.ibatis.annotations.Options;
import org.apache.ibatis.annotations.Select;

import java.util.List;

@Mapper
public interface ApprovalRecordMapper {
    @Insert("""
            insert into approval_record(application_id, operator_id, from_status, to_status, comment)
            values(#{applicationId}, #{operatorId}, #{fromStatus}, #{toStatus}, #{comment})
            """)
    @Options(useGeneratedKeys = true, keyProperty = "id")
    int insert(ApprovalRecord record);

    @Select("select * from approval_record where application_id = #{applicationId} order by id desc")
    List<ApprovalRecord> selectByApplicationId(Long applicationId);
}
