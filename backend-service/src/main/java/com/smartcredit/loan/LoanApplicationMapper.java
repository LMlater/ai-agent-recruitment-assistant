package com.smartcredit.loan;

import org.apache.ibatis.annotations.Insert;
import org.apache.ibatis.annotations.Mapper;
import org.apache.ibatis.annotations.Options;
import org.apache.ibatis.annotations.Param;
import org.apache.ibatis.annotations.Select;
import org.apache.ibatis.annotations.Update;

import java.util.List;

@Mapper
public interface LoanApplicationMapper {
    @Insert("""
            insert into loan_application(customer_id, amount, term_months, purpose, status, created_by)
            values(#{customerId}, #{amount}, #{termMonths}, #{purpose}, #{status}, #{createdBy})
            """)
    @Options(useGeneratedKeys = true, keyProperty = "id")
    int insert(LoanApplication application);

    @Select("select * from loan_application where id = #{id}")
    LoanApplication selectById(Long id);

    @Select("""
            select * from loan_application
            order by id desc
            limit #{size} offset #{offset}
            """)
    List<LoanApplication> selectPage(@Param("offset") int offset, @Param("size") int size);

    @Select("select count(1) from loan_application")
    long countAll();

    @Update("update loan_application set status = #{status} where id = #{id}")
    int updateStatus(@Param("id") Long id, @Param("status") String status);

    @Update("""
            update loan_application
            set status=#{status},
                risk_score=#{riskScore},
                risk_level=#{riskLevel},
                ai_decision=#{aiDecision},
                ai_summary=#{aiSummary}
            where id=#{id}
            """)
    int updateAiReviewResult(
            @Param("id") Long id,
            @Param("status") String status,
            @Param("riskScore") Integer riskScore,
            @Param("riskLevel") String riskLevel,
            @Param("aiDecision") String aiDecision,
            @Param("aiSummary") String aiSummary
    );
}
