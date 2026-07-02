-- Generated mock loan applications from public German Credit mappings. Import customers first.
insert into loan_application(customer_id, amount, term_months, purpose, status, created_by)
select id, 2835.00, 24, 'generated seed CASE_0007 furniture equipment', 'SUBMITTED', null
from customer
where name = 'Seed Customer 001'
  and not exists (select 1 from loan_application where purpose = 'generated seed CASE_0007 furniture equipment');

insert into loan_application(customer_id, amount, term_months, purpose, status, created_by)
select id, 3059.00, 12, 'generated seed CASE_0009 radio television', 'SUBMITTED', null
from customer
where name = 'Seed Customer 002'
  and not exists (select 1 from loan_application where purpose = 'generated seed CASE_0009 radio television');

insert into loan_application(customer_id, amount, term_months, purpose, status, created_by)
select id, 1567.00, 12, 'generated seed CASE_0013 radio television', 'SUBMITTED', null
from customer
where name = 'Seed Customer 003'
  and not exists (select 1 from loan_application where purpose = 'generated seed CASE_0013 radio television');

insert into loan_application(customer_id, amount, term_months, purpose, status, created_by)
select id, 1403.00, 15, 'generated seed CASE_0015 new car', 'SUBMITTED', null
from customer
where name = 'Seed Customer 004'
  and not exists (select 1 from loan_application where purpose = 'generated seed CASE_0015 new car');

insert into loan_application(customer_id, amount, term_months, purpose, status, created_by)
select id, 7882.00, 42, 'generated seed CASE_0004 furniture equipment', 'SUBMITTED', null
from customer
where name = 'Seed Customer 005'
  and not exists (select 1 from loan_application where purpose = 'generated seed CASE_0004 furniture equipment');

insert into loan_application(customer_id, amount, term_months, purpose, status, created_by)
select id, 9055.00, 36, 'generated seed CASE_0006 education', 'SUBMITTED', null
from customer
where name = 'Seed Customer 006'
  and not exists (select 1 from loan_application where purpose = 'generated seed CASE_0006 education');

insert into loan_application(customer_id, amount, term_months, purpose, status, created_by)
select id, 6948.00, 36, 'generated seed CASE_0008 used car', 'SUBMITTED', null
from customer
where name = 'Seed Customer 007'
  and not exists (select 1 from loan_application where purpose = 'generated seed CASE_0008 used car');

insert into loan_application(customer_id, amount, term_months, purpose, status, created_by)
select id, 1169.00, 6, 'generated seed CASE_0001 radio television', 'SUBMITTED', null
from customer
where name = 'Seed Customer 008'
  and not exists (select 1 from loan_application where purpose = 'generated seed CASE_0001 radio television');

insert into loan_application(customer_id, amount, term_months, purpose, status, created_by)
select id, 5951.00, 48, 'generated seed CASE_0002 radio television', 'SUBMITTED', null
from customer
where name = 'Seed Customer 009'
  and not exists (select 1 from loan_application where purpose = 'generated seed CASE_0002 radio television');

insert into loan_application(customer_id, amount, term_months, purpose, status, created_by)
select id, 2096.00, 12, 'generated seed CASE_0003 education', 'SUBMITTED', null
from customer
where name = 'Seed Customer 010'
  and not exists (select 1 from loan_application where purpose = 'generated seed CASE_0003 education');
