CREATE DATABASE proxy;
USE proxy;

CREATE TABLE proxies
(
proxy_port varchar(64),
passwd varchar(64),
PRIMARY KEY ( proxy_port )
);
grant all  privileges  on proxy.* to wx@localhost identified by 'bihu24h';
desc proxies;

