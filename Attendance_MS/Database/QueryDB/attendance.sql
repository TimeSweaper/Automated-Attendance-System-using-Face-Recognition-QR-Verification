
use attendancems;

create table if not exists attendnace(
	id bigint unsigned not null auto_increment,
    sessionID bigint unsigned not null,
    studentID bigint unsigned not null,
    status enum('Present','Absent','Late','Excused') not null default 'Present',
    method varchar(32) not null default 'qr_face',
    device_info varchar(120) null,
    marked_at datetime not null default current_timestamp,
    primary key (id),
    unique key uq_att_once (sessionID, studentID),
    key idx_att_session (sessionID),
    key idx_att_student (studentID),
    constraint fk_att_session
		foreign key (sessionID) references session(id)
        on delete cascade,
        constraint fk_att_student
			foreign key (studentID) references users(id)
            on delete cascade
)engine=InnoDB default charset =utf8mb4;

use ams;

select * from attendancems;