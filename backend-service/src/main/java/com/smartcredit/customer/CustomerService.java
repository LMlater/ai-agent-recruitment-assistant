package com.smartcredit.customer;

import com.smartcredit.common.BusinessException;
import com.smartcredit.common.PageResponse;
import com.smartcredit.customer.dto.CustomerRequest;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;

@Service
@RequiredArgsConstructor
public class CustomerService {
    private final CustomerMapper customerMapper;

    public Customer create(CustomerRequest request) {
        Customer customer = toCustomer(null, request);
        customerMapper.insert(customer);
        return customerMapper.selectById(customer.getId());
    }

    public Customer get(Long id) {
        Customer customer = customerMapper.selectById(id);
        if (customer == null) {
            throw new BusinessException("Customer not found");
        }
        return customer;
    }

    public PageResponse<Customer> page(int page, int size) {
        int safePage = Math.max(page, 1);
        int safeSize = Math.max(1, Math.min(size, 100));
        return new PageResponse<>(
                customerMapper.selectPage((safePage - 1) * safeSize, safeSize),
                customerMapper.countActive(),
                safePage,
                safeSize
        );
    }

    public Customer update(Long id, CustomerRequest request) {
        get(id);
        Customer customer = toCustomer(id, request);
        customerMapper.update(customer);
        return get(id);
    }

    public void delete(Long id) {
        if (customerMapper.logicalDelete(id) == 0) {
            throw new BusinessException("Customer not found");
        }
    }

    private Customer toCustomer(Long id, CustomerRequest request) {
        Customer customer = new Customer();
        customer.setId(id);
        customer.setName(request.name());
        customer.setIdCardMasked(request.idCardMasked());
        customer.setPhoneMasked(request.phoneMasked());
        customer.setAge(request.age());
        customer.setMonthlyIncome(request.monthlyIncome());
        customer.setWorkYears(request.workYears());
        customer.setExistingDebt(request.existingDebt());
        customer.setOverdueCount(request.overdueCount());
        customer.setAssetProofCount(request.assetProofCount());
        return customer;
    }
}
