
use attendancems;
create table if not exists users(
	id bigint unsigned not null auto_increment,
    role enum('teacher','student') not null,
    name varchar(100) not null,
    department varchar(100) null,
    course varchar(100) null,
    subjects text null,
    email varchar(250) not null,
    password_hash varchar(250) not null,
    photo_path varchar(500) null,
    face_encoding json null,
    create_at timestamp not null default current_timestamp,
    update_at timestamp not null default current_timestamp on update current_timestamp,
    primary key (id),
    unique key uq_users_email (email)
)engine=InnoDB default charset=utf8mb4;

use attendancems;

select * from users;