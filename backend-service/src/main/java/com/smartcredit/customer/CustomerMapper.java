package com.smartcredit.customer;

import org.apache.ibatis.annotations.Insert;
import org.apache.ibatis.annotations.Mapper;
import org.apache.ibatis.annotations.Options;
import org.apache.ibatis.annotations.Param;
import org.apache.ibatis.annotations.Select;
import org.apache.ibatis.annotations.Update;

import java.util.List;

@Mapper
public interface CustomerMapper {
    @Insert("""
            insert into customer(name, id_card_masked, phone_masked, age, monthly_income, work_years,
                                 existing_debt, overdue_count, asset_proof_count)
            values(#{name}, #{idCardMasked}, #{phoneMasked}, #{age}, #{monthlyIncome}, #{workYears},
                   #{existingDebt}, #{overdueCount}, #{assetProofCount})
            """)
    @Options(useGeneratedKeys = true, keyProperty = "id")
    int insert(Customer customer);

    @Select("select * from customer where id = #{id} and deleted = false")
    Customer selectById(Long id);

    @Select("""
            select * from customer
            where deleted = false
            order by id desc
            limit #{size} offset #{offset}
            """)
    List<Customer> selectPage(@Param("offset") int offset, @Param("size") int size);

    @Select("select count(1) from customer where deleted = false")
    long countActive();

    @Update("""
            update customer
            set name=#{name},
                id_card_masked=#{idCardMasked},
                phone_masked=#{phoneMasked},
                age=#{age},
                monthly_income=#{monthlyIncome},
                work_years=#{workYears},
                existing_debt=#{existingDebt},
                overdue_count=#{overdueCount},
                asset_proof_count=#{assetProofCount}
            where id=#{id} and deleted=false
            """)
    int update(Customer customer);

    @Update("update customer set deleted = true where id = #{id} and deleted = false")
    int logicalDelete(Long id);
}
