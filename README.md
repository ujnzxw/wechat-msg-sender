WeChat Enterprise account API
=====================================

This is a WeChat Enterprise Account CLI message sending Tool.

Usage
-----
##### Create a WeChat Enterprise Account for your team from [微信公众平台](https://mp.weixin.qq.com/)

##### Install WeChat message sender

To **install** or **update** sender you can run this command:

`INSTALL_DIR=$HOME/.wechat-msg-sender sh <(curl -fsSL https://raw.githubusercontent.com/ujnzxw/wechat-msg-sender/master/install.sh)`

##### Have a test

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
