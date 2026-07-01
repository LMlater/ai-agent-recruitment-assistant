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
