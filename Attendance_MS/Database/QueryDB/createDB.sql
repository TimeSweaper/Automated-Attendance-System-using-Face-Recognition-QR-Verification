create database if not exists AttendanceMS
	character set utf8mb4
    collate utf8mb4_general_ci;

create user if not exists 'AttendanceMS'@'localhost' identified by 'pass123';
grant all privileges on AttendanceMS.* to 'AttendanceMS'@'localhost';
flush privileges;