create table if not exists sys_user (
    id bigint primary key auto_increment,
    username varchar(64) not null unique,
    password_hash varchar(255) not null,
    display_name varchar(64) not null,
    status varchar(20) not null default 'ACTIVE',
    created_at datetime not null default current_timestamp,
    updated_at datetime not null default current_timestamp on update current_timestamp
) engine=InnoDB default charset=utf8mb4;

create table if not exists sys_role (
    id bigint primary key auto_increment,
    role_code varchar(64) not null unique,
    role_name varchar(64) not null
) engine=InnoDB default charset=utf8mb4;

create table if not exists sys_user_role (
    id bigint primary key auto_increment,
    user_id bigint not null,
    role_id bigint not null,
    unique key uk_user_role(user_id, role_id)
) engine=InnoDB default charset=utf8mb4;

create table if not exists customer (
    id bigint primary key auto_increment,
    name varchar(64) not null,
    id_card_masked varchar(32) not null,
    phone_masked varchar(32) not null,
    age int not null,
    monthly_income decimal(12,2) not null,
    work_years int not null,
    existing_debt decimal(12,2) not null,
    overdue_count int not null default 0,
    asset_proof_count int not null default 0,
    deleted tinyint(1) not null default 0,
    created_at datetime not null default current_timestamp,
    updated_at datetime not null default current_timestamp on update current_timestamp
) engine=InnoDB default charset=utf8mb4;

create table if not exists loan_application (
    id bigint primary key auto_increment,
    customer_id bigint not null,
    amount decimal(12,2) not null,
    term_months int not null,
    purpose varchar(255) not null,
    status varchar(32) not null,
    risk_score int null,
    risk_level varchar(32) null,
    ai_decision varchar(32) null,
    ai_summary text null,
    created_by bigint null,
    created_at datetime not null default current_timestamp,
    updated_at datetime not null default current_timestamp on update current_timestamp,
    key idx_loan_customer(customer_id),
    key idx_loan_status(status)
) engine=InnoDB default charset=utf8mb4;

create table if not exists ai_decision_report (
    id bigint primary key auto_increment,
    application_id bigint not null,
    workflow_id varchar(64) not null,
    final_decision varchar(32) not null,
    risk_level varchar(32) not null,
    risk_score int not null,
    suggested_amount decimal(12,2) not null,
    summary text not null,
    report_json json not null,
    created_at datetime not null default current_timestamp,
    key idx_report_application(application_id),
    key idx_report_workflow(workflow_id)
) engine=InnoDB default charset=utf8mb4;

create table if not exists agent_execution_log (
    id bigint primary key auto_increment,
    workflow_id varchar(64) not null,
    application_id bigint not null,
    agent_name varchar(64) not null,
    status varchar(32) not null,
    input_summary text null,
    output_summary text null,
    error_message text null,
    started_at datetime null,
    ended_at datetime null,
    duration_ms bigint null,
    created_at datetime not null default current_timestamp,
    key idx_agent_log_workflow(workflow_id),
    key idx_agent_log_application(application_id)
) engine=InnoDB default charset=utf8mb4;

create table if not exists approval_record (
    id bigint primary key auto_increment,
    application_id bigint not null,
    operator_id bigint not null,
    from_status varchar(32) not null,
    to_status varchar(32) not null,
    comment text null,
    created_at datetime not null default current_timestamp,
    key idx_approval_application(application_id)
) engine=InnoDB default charset=utf8mb4;

create table if not exists audit_log (
    id bigint primary key auto_increment,
    user_id bigint null,
    action varchar(64) not null,
    resource_type varchar(64) not null,
    resource_id bigint null,
    detail text null,
    ip varchar(64) null,
    created_at datetime not null default current_timestamp,
    key idx_audit_user(user_id),
    key idx_audit_resource(resource_type, resource_id)
) engine=InnoDB default charset=utf8mb4;
