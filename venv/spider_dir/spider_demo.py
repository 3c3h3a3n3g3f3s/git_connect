# -*- coding:utf-8 -*-

import requests
import json


def fun1():
    s_cut = [('72af8ecf3609a546bac3150c20f70455', ['老凤祥', '六福珠宝', '周生生', '亚一珠宝', '亚一金店']),
             ('3e78397f7dbb88ffbd78ba52d0e925fa', ['老庙', '谢瑞麟', '中国黄金', '明牌珠宝']),  # yh
             ('6bee32b2f0719ea45cc194847efd8917', ['周大福', '潮宏基', '东华美钻', '周大生']),  # zyy
             ]
    num = 1
    city_code = ['上海']
    for s_key, store_names in s_cut:
        for store in store_names:
            for code in city_code:
                params = {'keywords': store,
                          'types': '购物服务',
                          'city': code,
                          'citylimit': 'True',
                          'output': 'json',
                          'key': s_key,
                          'offset': 20,
                          'page': num}
                response = requests.get('https://restapi.amap.com/v3/place/text', params=params)
                map_results = json.loads(response.text)
                print(map_results)
                return map_results


json_text = fun1()
print(json_text['pois'])

print(len(json_text['pois']))
