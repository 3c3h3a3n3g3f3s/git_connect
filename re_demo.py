# -*- coding: UTF-8 -*-
import re

st = "ajfaldsfjlsdfja"

# 替换
print(re.sub('a', "中国", st))

# 替换 含有返回值,及计数。

print(re.subn('a', '中国', st))

# 分割

print(re.split('a', st))

# 分组

a = re.search('(?P<name>a)', st).group("name")
print(a)
