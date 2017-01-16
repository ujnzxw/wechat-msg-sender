WeChat Enterprise account API
=====================================

This is a WeChat Enterprise Account CLI message sending Tool.

Usage
-----
### Create a WeChat Enterprise Account

1. Create a WeChat Enterprise Account for your team from [微信公众平台](https://mp.weixin.qq.com/)
2. Get your corpid and secret
3. create a party and add a main user id.


### Install WeChat message sender

To **install** or **update** sender you can run this command:

`INSTALL_DIR=$HOME/.wechat-msg-sender sh <(curl -fsSL https://raw.githubusercontent.com/ujnzxw/wechat-msg-sender/master/install.sh)`

###  Configuration File

Fill your WeChat Enterprise Account infomation into ${INSTALL_DIR}/.wechat-msg-sender/cfg.ini

  For Example:
  ```
  [server]

  url     = https://qyapi.weixin.qq.com/cgi-bin
  corpid  = YOUR_CORPID
  secret  = YOUR_SECRET

  [user]

  touser  = YOUR_USER_ID
  toparty = 1
  msgtype = text
  agentid = 1
  safe    = 0

  [logs]

  logfile = ./logs/wechat.log
  ```

### Have a test

After you install or cloned this project, please run `wechat-msg-sender -h`

Usage: sender --touser=<to user> --message=<sending message> [options]

Options:
  -h, --help            show this help message and exit
  -u TOUSER, --touser=TOUSER
                        message send to
  -m MESSAGE, --message=MESSAGE
                        message you want to send
  -p TOPARTY, --toparty=TOPARTY
                        sending party. Use the one in cfg.ini as default



TO-DO List
----------

License
-------
Copyright (c) 2014-2016 ujnzxw <ujnzxw@gmail.com>

Distributed under the MIT license. See the LICENSE file for more details.
