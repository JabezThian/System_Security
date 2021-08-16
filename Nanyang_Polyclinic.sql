CREATE DATABASE IF NOT EXISTS nanyang_login;
USE nanyang_login;
DROP TABLE IF EXISTS users;
CREATE TABLE IF NOT EXISTS users (
 nric varchar(9) NOT NULL,
 fname varchar(50) NOT NULL,
 lname varchar(50) NOT NULL,
 gender varchar(1) NOT NULL,
 dob date NOT NULL,
 email varchar(255),
 password varchar(255) NOT NULL,
 symmetrickey varchar(255) NULL,
 role varchar(50) NOT NULL,
 specialization varchar(50) NULL,
 url varchar(255) NULL,
 attempt int NOT NULL,
 lockout varchar(20) NOT NULL,
 lockout_time varchar(50) NULL,
 reset_password varchar(1) NOT NULL,
 PRIMARY KEY (nric)
);
INSERT INTO `nanyang_login`.`users`
(`nric`, `fname`, `lname`, `gender`, `dob`, `email`, `password`, `symmetrickey`, `role`, `specialization`, `url`, `attempt`, `lockout`, `lockout_time`, `reset_password`)
VALUES
('T0392511G', 'Daniel', 'Jack', 'M', '1999-10-22', 'nugget6chicken@gmail.com','gAAAAABhGSCC3f-RLC1qjMTYk4RZOIuTHusv0vQNrBgVoUsgkKIgxrqmG7MnNsXcV1BHiTcaYTEbYbsJ-kOR7GjUMitYhQ73Tg==', 'J6HdU98z_PBxzw_15jOXiGMMuFEsmzlXcysQDnsx_IE=', 'Patient', NULL, NULL, 0, 'false', NULL, 'F'),
('T1111111F', 'Eric', 'Lee', 'M', '1994-10-30', 'nanyanghospital2021@gmail.com', 'gAAAAABhGSCC3f-RLC1qjMTYk4RZOIuTHusv0vQNrBgVoUsgkKIgxrqmG7MnNsXcV1BHiTcaYTEbYbsJ-kOR7GjUMitYhQ73Tg==', 'J6HdU98z_PBxzw_15jOXiGMMuFEsmzlXcysQDnsx_IE=', 'Doctor', 'Cardiology', 'https://google.com', 0, 'false', NULL, 'F'),
('T5739128U', 'Chloe', 'Soh', 'F', '1980-10-15', 'cholesoh@gmail.com', 'gAAAAABhGSCC3f-RLC1qjMTYk4RZOIuTHusv0vQNrBgVoUsgkKIgxrqmG7MnNsXcV1BHiTcaYTEbYbsJ-kOR7GjUMitYhQ73Tg==', 'J6HdU98z_PBxzw_15jOXiGMMuFEsmzlXcysQDnsx_IE=','Admin', NULL, NULL, 0, 'false', NULL, 'F');
