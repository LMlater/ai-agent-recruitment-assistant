-- Generated mock customers from public German Credit mappings. Do not treat as real customer data.
insert into customer(name, id_card_masked, phone_masked, age, monthly_income, work_years, existing_debt, overdue_count, asset_proof_count)
select 'Seed Customer 001', '4401********0001', '138****0001', 53, 3221.59, 8.0, 9213.75, 0, 3
where not exists (select 1 from customer where name = 'Seed Customer 001');

insert into customer(name, id_card_masked, phone_masked, age, monthly_income, work_years, existing_debt, overdue_count, asset_proof_count)
select 'Seed Customer 002', '4401********0002', '138****0002', 61, 5098.33, 5.0, 8259.30, 0, 4
where not exists (select 1 from customer where name = 'Seed Customer 002');

insert into customer(name, id_card_masked, phone_masked, age, monthly_income, work_years, existing_debt, overdue_count, asset_proof_count)
select 'Seed Customer 003', '4401********0003', '138****0003', 22, 2238.57, 2.0, 3369.05, 0, 1
where not exists (select 1 from customer where name = 'Seed Customer 003');

insert into customer(name, id_card_masked, phone_masked, age, monthly_income, work_years, existing_debt, overdue_count, asset_proof_count)
select 'Seed Customer 004', '4401********0004', '138****0004', 28, 1870.67, 2.0, 3788.10, 0, 1
where not exists (select 1 from customer where name = 'Seed Customer 004');

insert into customer(name, id_card_masked, phone_masked, age, monthly_income, work_years, existing_debt, overdue_count, asset_proof_count)
select 'Seed Customer 005', '4401********0005', '138****0005', 45, 3753.33, 5.0, 21281.40, 0, 2
where not exists (select 1 from customer where name = 'Seed Customer 005');

insert into customer(name, id_card_masked, phone_masked, age, monthly_income, work_years, existing_debt, overdue_count, asset_proof_count)
select 'Seed Customer 006', '4401********0006', '138****0006', 35, 5030.56, 2.0, 24448.50, 0, 1
where not exists (select 1 from customer where name = 'Seed Customer 006');

insert into customer(name, id_card_masked, phone_masked, age, monthly_income, work_years, existing_debt, overdue_count, asset_proof_count)
select 'Seed Customer 007', '4401********0007', '138****0007', 35, 3860.00, 2.0, 18759.60, 0, 1
where not exists (select 1 from customer where name = 'Seed Customer 007');

insert into customer(name, id_card_masked, phone_masked, age, monthly_income, work_years, existing_debt, overdue_count, asset_proof_count)
select 'Seed Customer 008', '4401********0008', '138****0008', 67, 6494.44, 8.0, 8884.40, 2, 3
where not exists (select 1 from customer where name = 'Seed Customer 008');

insert into customer(name, id_card_masked, phone_masked, age, monthly_income, work_years, existing_debt, overdue_count, asset_proof_count)
select 'Seed Customer 009', '4401********0009', '138****0009', 22, 2479.58, 2.0, 16067.70, 0, 2
where not exists (select 1 from customer where name = 'Seed Customer 009');

insert into customer(name, id_card_masked, phone_masked, age, monthly_income, work_years, existing_debt, overdue_count, asset_proof_count)
select 'Seed Customer 010', '4401********0010', '138****0010', 49, 3493.33, 5.0, 5659.20, 2, 2
where not exists (select 1 from customer where name = 'Seed Customer 010');
