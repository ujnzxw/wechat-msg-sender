create user wx@localhost identified by 'bihu24h';

CREATE DATABASE wx;
USE wx;
CREATE TABLE wx_token
(
access_token varchar(512),
expires_in varchar(255),
update_time varchar(255)
);
CREATE TABLE wx_messages
(
MsgId bigint UNSIGNED,
ToUserName varchar(128),
FromUserName varchar(128),
CreateTime int UNSIGNED,
MsgType varchar(32),
Content varchar(255),
PRIMARY KEY ( msgid )
);
grant all  privileges  on wx.* to wx@localhost identified by 'bihu24h';
