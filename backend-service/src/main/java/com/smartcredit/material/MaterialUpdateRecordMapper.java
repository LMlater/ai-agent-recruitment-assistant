package com.smartcredit.material;

import org.apache.ibatis.annotations.Insert;
import org.apache.ibatis.annotations.Mapper;
import org.apache.ibatis.annotations.Options;
import org.apache.ibatis.annotations.Select;

import java.util.List;

@Mapper
public interface MaterialUpdateRecordMapper {
    @Insert("""
            insert into material_update_record(application_id, operator_id, material_summary, from_status, to_status)
            values(#{applicationId}, #{operatorId}, #{materialSummary}, #{fromStatus}, #{toStatus})
            """)
    @Options(useGeneratedKeys = true, keyProperty = "id")
    int insert(MaterialUpdateRecord record);

    @Select("select * from material_update_record where application_id = #{applicationId} order by id desc")
    List<MaterialUpdateRecord> selectByApplicationId(Long applicationId);
}
