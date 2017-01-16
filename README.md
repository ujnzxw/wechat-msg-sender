WeChat Enterprise account API
=====================================

This is a WeChat Enterprise Account CLI message sending Tool.

Usage
-----
1. Create a WeChat Enterprise Account for your team from [微信公众平台](https://mp.weixin.qq.com/)

2. Install WeChat message sender

To **install** or **update** sender you can run this command:
`curl -fsSL https://raw.githubusercontent.com/ujnzxw/wechat_msg-sender/master/install.sh | sh`

You can also install it in a different path

`INSTALL_DIR=$HOME/.wechat-msg-sender sh <(curl -fsSL https://raw.githubusercontent.com/ujnzxw/wechat-msg-sender/master/install.sh)`

3. Have a test



After you install or cloned this project, please run `sender -h`

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
