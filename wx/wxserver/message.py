# -*- coding: utf-8 -*-

# 新用户关注显示的欢迎信息
SUBSCRIBE_WELCOME_MSG = '''你来了呀，币乎搜一搜！\n请输入“？” 获取帮助信息哦~ '''

# 输入？显示的帮助信息
HELP_MSG = '''
币乎365帮助信息：

排行榜功能：

1. 输入乎er用户名 + “的币乎排名信息”获取个人排名：金马的币乎排名信息

搜索功能：

2. 直接输入关键词，搜索全文匹配项

<a href="http://mp.weixin.qq.com/s/NIB7IEisoEXhtYKpttlq7Q">获取更多...</a>
'''

MORE_HELP_MSG = '''
2. 输入作者 + 关键词，搜索作者匹配项：作者 东湾以东

3. 输入内容 + 关键词，搜索内容匹配项：内容 区块链

4. 输入标题 + 关键词，搜索标题匹配项：标题 比特币

1. 输入“点赞排行榜” 获取文章点赞总量TOP 10

2. 输入“发文排行榜” 获取用户发文总量TOP 10

3. 输入“收赞排行榜” 获取用户收赞总量TOP 10

4. 输入“收入排行榜” 获取用户收入排名TOP 10
<a href="https://bihu.com/people/$userid">$username</a>
'''

# 遇到没有标题的文章用这个代替
NO_ARTICLE_TITLE = '[无标题]'

# 输入非文本消息后显示的提示信息
SEARCH_NO_TEXT_MSG = '''暂时不支持非文本消息哦~'''

# 输入作者错误显示的提示信息
USERNAME_ERROR_MSG = '''“作者 ”后面不能为空哦~'''

# 输入内容错误显示的提示信息
CONTENT_ERROR_MSG  = '''“内容 ”后面不能为空哦~'''

# 输入标题错误显示的提示信息
TITLE_ERROR_MSG    = '''“标题 ”后面不能为空哦~'''

# 搜索不成功后返回的提示信息
SEARCH_RETURN_NULL_MSG = '''暂未搜到你要的内容，换个关键词试试~'''

# 开发中未完成功能提示信息
DEV_INPROGRESS_MSG = '''你好厉害，发现了未成熟的我，等我哦~'''

# 获取点赞排行榜的请求信息
ARTICLE_UPS_RANK_QUERY = '点赞排行榜'

# 获取发文排行榜的请求信息
ARTICLE_COUNT_RANK_QUERY = '发文排行榜'

# 获取搜索排行榜的请求信息
SEARCH_KEYWORDS_RANK_QUERY = '搜索排行榜'

# 获取总点赞排行榜的请求信息
PERSON_UPS_RANK_QUERY = '收赞排行榜'

# 获取总收入排行榜的请求信息
PERSON_REVENUE_RANK_QUERY = '收入排行榜'

# 获取个人[ 发文量、收赞量、收入信息] 及排名的识别后缀
# 输入用户名+'的币乎排名信息'，例如，东湾以东的币乎排名信息
MY_INFO_AND_RANK_SUFFIX = '的币乎排名信息'

# 用户名不存在返回信息提示
MY_INFO_AND_RANK_ERROR = '用户名不存在，请重新输入~'

# 系统遇到错误时返回信息提示
UPGRADE_INPROGRESS_MSG = '系统正在升级中，请稍候再试~'

# 获取个人[ 发文量、收赞量、收入信息] 及排名的数据模板
MY_INFO_AND_RANK_TEMPLATE = """
$username的币乎排名信息:
发文：$art_number，排名：$art_rank
收赞：$ups_number，排名：$ups_rank
收入：$rev_number，排名：$rev_rank
"""

# 搜索返回数据模板
SEARCH_RETURN_MSG_TEMPLATE = """
标题：<a href="https://m.bihu.com/article/$artid">$title</a>
作者：$username
"""

# 获取点赞排行榜返回数据模板
ARTICLE_UPS_RANK_MSG_TEMPLATE_HEADER = "文章点赞排行榜TOP $total:\n"
ARTICLE_UPS_RANK_MSG_TEMPLATE = """
[$number] <a href="https://m.bihu.com/article/$artid">$title</a>
点赞量：$ups
"""

# 获取发文排行榜返回数据模板
ARTICLE_COUNT_RANK_MSG_TEMPLATE_HEADER = "用户发文数量排行榜TOP $total:\n"
ARTICLE_COUNT_RANK_MSG_TEMPLATE = """
[$number] <a href="https://bihu.com/people/$userid">$username</a>
发文量：$count
"""

# 获取收赞排行榜返回数据模板
PERSON_UPS_RANK_MSG_TEMPLATE_HEADER =  "用户收赞排行榜TOP $total:\n"
PERSON_UPS_RANK_MSG_TEMPLATE =  """
[$number] <a href="https://bihu.com/people/$userid">$username</a>
收赞量：$total_ups
"""

# 获取收入排行榜返回数据模板
PERSON_REVENUE_RANK_MSG_TEMPLATE_HEADER =  "用户收入排行榜TOP $total:\n"
PERSON_REVENUE_RANK_MSG_TEMPLATE =  """
[$number] <a href="https://bihu.com/people/$userid">$username</a>
收入：$total_revenue
"""
