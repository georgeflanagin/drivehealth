CREATE TABLE majorinfo (workstation varchar(10),serial_number varchar(30),device_model varchar(30), primary key (serial_number));
CREATE TABLE attribute_value (workstation varchar(10), serial_number varchar(30),ID varchar(5),raw_value varchar(20),mod_time datetime default current_timestamp, foreign key(serial_number) references majorinfo(serial_number));
CREATE TABLE attribute_desc (
    ID varchar(5),
    desc varchar(200),
    primary key (ID));


INSERT INTO attribute_desc VALUES('1','read error rate');
INSERT INTO attribute_desc VALUES('2','throughput performance');
INSERT INTO attribute_desc VALUES('3','spin-up time');
INSERT INTO attribute_desc VALUES('4','start-stop count');
INSERT INTO attribute_desc VALUES('5','reallocated sectors count');
INSERT INTO attribute_desc VALUES('6','read channel margin');
INSERT INTO attribute_desc VALUES('7','seek error rate');
INSERT INTO attribute_desc VALUES('8','seek time performance');
INSERT INTO attribute_desc VALUES('9','power-on hours');
INSERT INTO attribute_desc VALUES('10','spin retry count');
INSERT INTO attribute_desc VALUES('11','recalibration count');
INSERT INTO attribute_desc VALUES('12','power cycle count');
INSERT INTO attribute_desc VALUES('192','unsafe shutdown count');
INSERT INTO attribute_desc VALUES('194','temperature');
INSERT INTO attribute_desc VALUES('196','reallocation event count');
INSERT INTO attribute_desc VALUES('197','unstable sector count');
INSERT INTO attribute_desc VALUES('198','uncorrectable sector count');
INSERT INTO attribute_desc VALUES('200','write error rate');

CREATE VIEW temps as 
    select 
        workstation, 
        serial_number, 
        raw_value as temp,
        mod_time as time
    from
        attribute_value 
    where 
        ID = '194' 
    order by workstation asc, serial_number asc, time asc

CREATE VIEW latest as 
    select 
        majorinfo.workstation as workstation,
        majorinfo.serial_number as sn,
        attribute_value.ID as ID,
        attribute_value.raw_value as value,
        max(attribute_value.mod_time) as time
    from
        majorinfo inner join attribute_value on majorinfo.serial_number = attribute_value.serial_number
    group by majorinfo.workstation, sn, ID
    order by workstation, sn, ID, value, time

CREATE VIEW latest_w_desc as
    select 
        latest.workstation as workstation, 
        latest.sn as sn, 
        latest.ID as ID, 
        latest.value as value,
        attribute_desc.desc as desc
    from
        latest inner join attribute_desc on latest.ID = attribute_desc.ID
    order by workstation asc, sn asc, ID asc
