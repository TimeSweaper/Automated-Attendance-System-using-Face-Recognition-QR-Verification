use attendancems;

create table if not exists session(
	id bigint unsigned not null auto_increment,
    teacher_id bigint unsigned not null,
    code varchar(32) not null,
    subject varchar(120) null,
    section varchar(50) null,
    started_at datetime not null default current_timestamp,
    locked tinyint(1) not null default 0,
    ended_at datetime null,
    primary key(id),
    unique key uq_session_code (code),
    key idx_session_teacher (teacher_id),
    constraint fk_session_teacher
		foreign key (teacher_id) references users(id)
        on delete cascade
)engine=InnoDB default charset=utf8mb4;

use ams;

select * from session;
