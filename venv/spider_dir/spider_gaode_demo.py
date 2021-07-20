import json
import os
import re
import time
from datetime import datetime
from collections import defaultdict
from math import sin, asin, cos, radians, fabs, sqrt

import requests
import pandas as pd
from sqlalchemy import create_engine
from simhash import Simhash
from jieba.analyse import extract_tags, set_stop_words

from configs_ods import log
from configs_ods import db_url


def obj2str(obj):
    if obj is None:
        return obj
    if isinstance(obj, (float, str, int)):
        return obj
    else:
        return json.dumps(obj)


def lng_lat(location):
    if location is None:
        return [None, None]
    else:
        return location.split(',')


def poi_type_filter(type_str, special_poi_type, common_poi_str):
    if type_str is None:
        return False
    if common_poi_str in type_str or type_str in special_poi_type:
        return False
    return True


def poi_scrapy(current_time, db_engine, poi_table_name, city_code_table_name):
    common_poi_str = '珠宝首饰工艺品'
    special_poi_type = {'购物服务;专卖店;专营店': 1,
                        '购物服务;购物相关场所;购物相关场所': 1,
                        '购物服务;商场;商场': 1,
                        '购物服务;个人用品/化妆品店;其它个人用品店': 1,
                        '购物服务;特殊买卖场所;典当行': 1,
                        '购物服务;特殊买卖场所;特殊买卖场所': 1,
                        '购物服务;购物相关场所;购物相关场所|生活服务;生活服务场所;生活服务场所': 1,
                        '风景名胜;风景名胜相关;旅游景点|购物服务;购物相关场所;购物相关场所': 1,
                        '购物服务;专卖店;礼品饰品店': 1,
                        '生活服务;生活服务场所;生活服务场所|购物服务;购物相关场所;购物相关场所': 1
                        }

    scrapy_cut = [('72af8ecf3609a546bac3150c20f70455', ['老凤祥', '六福珠宝', '周生生', '亚一珠宝', '亚一金店']),
                  ]

    code_data = pd.read_sql("""SELECT DISTINCT city_code as code FROM %s 
                                WHERE city_code !=''""" % city_code_table_name,
                            db_engine)
    city_code = code_data['code'].values

    brand_map = {'亚一珠宝': '亚一',
                 '亚一金店': '亚一'}

    record_filter = {}

    for s_key, store_names in scrapy_cut:
        for store in store_names:
            for code in city_code:

                poi_result = []
                sub_results = [1]
                num = 1
                while len(sub_results) > 0:
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

                    sub_results = map_results['pois']
                    num += 1
                    poi_result.extend(sub_results)

                poi_name = ['id', 'name', 'type', 'address', 'location', 'tel', 'adname', 'cityname', 'pname']
                columns_name = ['poi_id', 'store_name', 'store_type',
                                'address', 'lng', 'lat', 'tel', 'adname', 'cityname', 'pname']
                poi_vals = []
                for r in poi_result:
                    val = []

                    for col in poi_name:
                        if col != 'location':
                            val.append(obj2str(r.get(col, None)))
                        else:
                            location = lng_lat(r.get(col, None))
                            val.extend(location)

                    brand_name = brand_map[store] if store in brand_map else store

                    val.append(brand_name)

                    store_name = val[1]
                    if store not in store_name:
                        continue

                    if val[0] in record_filter:
                        continue
                    else:
                        record_filter[val[0]] = 1

                    if poi_type_filter(val[2], special_poi_type, common_poi_str):
                        continue

                    poi_vals.append(val)

                poi_df = pd.DataFrame(poi_vals, columns=columns_name + ['brand'])
                if len(poi_df) > 0:
                    poi_df['cal_time'] = current_time
                    poi_df.to_sql(name=poi_table_name, con=db_engine, if_exists='append', index=False)


