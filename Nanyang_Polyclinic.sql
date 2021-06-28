DROP DATABASE IF EXISTS nanyang_login;
CREATE DATABASE IF NOT EXISTS nanyang_login;
USE nanyang_login;
DROP TABLE IF EXISTS Accounts;
CREATE TABLE IF NOT EXISTS Accounts (
 nric varchar(9) NOT NULL,
 fname varchar(50) NOT NULL,
 lname varchar(50) NOT NULL,
 gender varchar(1) NOT NULL,
 date_of_birth date NOT NULL,
 email varchar(255) NOT NULL,
 password varchar(255) NOT NULL,
 symmetrickey varchar(255) NULL,
 role varchar(50) NOT NULL,
 PRIMARY KEY (nric)
);
INSERT INTO `nanyang_login`.`accounts`
(`nric`, `fname`, `lname`, `gender`, `date_of_birth`, `email`, `password`, `role`)
VALUES
('T0392511G', 'Daniel', 'Jack', 'M', '1999-10-22', 'danieljack@gmail.com','password', 'Patient'),
('T1111111F', 'Eric', 'Lee', 'M', '1994-10-30', 'samwilson@gmail.com', 'password', 'Doctor'),
('T5739128U', 'Chloe', 'Soh', 'F', '1980-10-15', 'chloesoh@gmail.com', 'password', 'Admin');
