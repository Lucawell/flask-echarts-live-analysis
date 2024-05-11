# encoding:utf-8
# utils.py
import json
import os
import re

def get_brand_paths(brands_dir, brand_name):
    # 定义品牌目录与拼音字母的映射关系
    brand_mapping = {
        'songshu': '三只松鼠',
        'jingzao': '京造',
        'baicao': '百草味',
        'liangpin': '良品铺子'
    }
    # 定义品牌目录
    # 获取拼音字母对应的品牌目录名称
    brand_name = brand_mapping.get(brand_name)
    if brand_name:
        # 构建品牌目录的完整路径
        brand_path = os.path.join(brands_dir, brand_name)
        if os.path.isdir(brand_path):
            # 获取品牌目录下所有的CSV文件
            csv_files = [f for f in os.listdir(brand_path) if f.endswith('.csv')]
            # 构建品牌对应的文件路径列表
            brand_paths = [os.path.join(brand_path, csv_file) for csv_file in csv_files]
            return {brand_name: brand_paths}
    return None  # 如果未找到对应品牌目录或者品牌不存在，返回 None

def extract_date(data):
    dates = []
    for key, file_paths in data.items():
        for file_path in file_paths:
            # 使用正则表达式从文件路径中提取日期信息
            match = re.search(r'\d{8}', file_path)
            if match:
                dates.append(match.group())
    return dates

def load_user_data(user_data_file):
    try:
        with open(user_data_file, 'r') as file:
            users = json.load(file)
    except FileNotFoundError:
        users = []
    return users

# 保存用户数据到文件
def save_user_data(users, user_data_file):
    with open(user_data_file, 'w') as file:
        json.dump(users, file, indent=4)