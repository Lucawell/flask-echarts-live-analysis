# encoding:utf-8
# routes/data.py
import os
from flask import Blueprint, jsonify, request
from controller.chart_data_controller import ChartDataProcessor
from utils import get_brand_paths, extract_date
from config import BRANDS_DIR

data_bp = Blueprint('data', __name__)
# 获取品牌的日期信息
@data_bp.route('/get_brand_dates/<brand>', methods=['GET'])
def get_brand_dates(brand):
    if not brand:
        return jsonify({'error': 'Brand name is missing'}), 400
    brand_paths = get_brand_paths(BRANDS_DIR, brand)
    if brand_paths:
        dates = extract_date(brand_paths)
        return jsonify({'dates': dates})
    else:
        return jsonify({'error': 'Brand not found'}), 404


# 获取特定品牌和时间的数据
@data_bp.route('/get_data/<brand>/<data_time>')
def get_data(brand, data_time):
    # 定义品牌目录与拼音字母的映射关系
    brand_mapping = {
        'songshu': '三只松鼠',
        'jingzao': '京造',
        'baicao': '百草味',
        'liangpin': '良品铺子'
    }
    # 拼接路径名
    brand_path_name = os.path.join(BRANDS_DIR, brand_mapping[brand], data_time + brand_mapping[brand] + '.csv')
    # 获取品牌数据路径映射字典
    brand_paths = get_brand_paths(BRANDS_DIR, brand)
    # 检查brand_paths中是否存在brand_path_name
    if brand_mapping[brand] in brand_paths and brand_path_name in brand_paths[brand_mapping[brand]]:
        # 获取品牌路径
        brand_path = brand_path_name
        # 获取请求中的图表类型参数
        chart_type = request.args.get('chart_type')
        # 使用 ChartDataProcessor 处理 CSV 文件并获取处理后的数据
        processor = ChartDataProcessor(brand_path)
        # 映射chart_type到处理函数的字典
        chart_type_mapping = {
            'user_behavior_counts': processor.user_behavior_counts,
            'user_message': processor.user_message_counts,
            'live_viewers_and_popularity': processor.live_viewers_and_popularity,
            'barrage_send_time_distribution': processor.barrage_send_time_distribution,
            'user_average_stay_time': processor.user_average_stay_time,
            'time_diff_data': processor.time_diff_data,
            'item_purchase_distribution': processor.item_purchase_distribution,
            'item_purchase_frequency_distribution': processor.item_purchase_frequency_distribution,
            'get_basic_data': processor.get_basic_data,
            'generate_barrage_wordcloud_data': processor.generate_barrage_wordcloud_data,
            'positive_negative_neutral_barrage_by_time': processor.positive_negative_neutral_barrage_by_time,
        }
        # 检查chart_type是否在映射中，如果在则调用对应的处理函数，否则返回错误响应
        if chart_type in chart_type_mapping:
            processed_data = chart_type_mapping[chart_type]()
            return jsonify(processed_data)
        else:
            return jsonify({"error": "Brand data not found"}), 404
