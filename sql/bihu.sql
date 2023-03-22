CREATE DATABASE bihu;
USE bihu;

CREATE TABLE article
(
artid varchar(32),
title varchar(128),
username varchar(255),
userid varchar(64),
boardname varchar(128),
updatime varchar(128),
content MEDIUMTEXT,
money varchar(64),
ups varchar(64),
downs varchar(64),
PRIMARY KEY ( artid )
);
CREATE TABLE article_not_found
(
artid INT UNSIGNED ,
PRIMARY KEY ( artid )
);
grant all  privileges  on bihu.* to wx@localhost identified by 'bihu24h';
desc article;

