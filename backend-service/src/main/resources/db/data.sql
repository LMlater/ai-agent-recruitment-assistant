insert ignore into sys_role(id, role_code, role_name) values
    (1, 'ADMIN', 'Administrator'),
    (2, 'CREDIT_OFFICER', 'Credit Officer'),
    (3, 'AUDITOR', 'Audit Viewer');

insert into customer(name, id_card_masked, phone_masked, age, monthly_income, work_years, existing_debt, overdue_count, asset_proof_count)
select 'Mock Low Risk Customer', '4401********1234', '138****1234', 32, 12000.00, 5, 30000.00, 0, 2
where not exists (select 1 from customer where name = 'Mock Low Risk Customer');

insert into customer(name, id_card_masked, phone_masked, age, monthly_income, work_years, existing_debt, overdue_count, asset_proof_count)
select 'Mock Medium Risk Customer', '4401********5678', '139****5678', 30, 9000.00, 2, 65000.00, 1, 1
where not exists (select 1 from customer where name = 'Mock Medium Risk Customer');

insert into customer(name, id_card_masked, phone_masked, age, monthly_income, work_years, existing_debt, overdue_count, asset_proof_count)
select 'Mock High Risk Customer', '4401********9012', '137****9012', 28, 5000.00, 0, 140000.00, 4, 0
where not exists (select 1 from customer where name = 'Mock High Risk Customer');

insert into loan_application(customer_id, amount, term_months, purpose, status, created_by)
select id, 80000.00, 24, 'seed low risk personal consumption', 'SUBMITTED', null
from customer
where name = 'Mock Low Risk Customer'
  and not exists (select 1 from loan_application where purpose = 'seed low risk personal consumption');

insert into loan_application(customer_id, amount, term_months, purpose, status, created_by)
select id, 130000.00, 24, 'seed medium risk home appliance upgrade', 'SUBMITTED', null
from customer
where name = 'Mock Medium Risk Customer'
  and not exists (select 1 from loan_application where purpose = 'seed medium risk home appliance upgrade');

insert into loan_application(customer_id, amount, term_months, purpose, status, created_by)
select id, 160000.00, 36, 'seed high risk business turnover', 'SUBMITTED', null
from customer
where name = 'Mock High Risk Customer'
  and not exists (select 1 from loan_application where purpose = 'seed high risk business turnover');
