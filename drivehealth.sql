create table if not exists majorinfo (
    workstation varchar(10),
    serial_number varchar(30),
    device_model varchar(30),
    primary key (serial_number)
)

create table if not exists attribute_value (
    workstation varchar(10),
    serial_number varchar(30),
    ID varchar(5),
    raw_value varchar(20),
    mod_time datetime default current_timestamp,
    foreign key(workstation, serial_number) references majorinfo(workstation, serial_number)
)

