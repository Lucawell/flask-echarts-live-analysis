# encoding:utf-8
import json
import threading
import time
from flask_socketio import SocketIO
from flask import Flask
from flask_cors import CORS  # 导入 CORS 类
from controller.chart_data_controller import ChartDataProcessor
from routes import auth, data, service

# 注意：生成环境中谨慎使用cors，因为它会允许所有的跨域请求，这可能会导致安全问题。在开发环境中，可以使用CORS来解决跨域问题。
# 指定品牌目录的路径
BRANDS_DIR = 'static/data/'
app = Flask(__name__)
app.config.from_object('config')
CORS(app)  # 在应用中启用 CORS
socketio = SocketIO(app, websocket=True, cors_allowed_origins="*")
stop_background_task = threading.Event()

# Register blueprints
app.register_blueprint(auth.auth_bp)
app.register_blueprint(data.data_bp)
app.register_blueprint(service.service_bp)

def process_and_emit_data(processor, method_names):
    # 初始化结果字典
    result_dict = {}
    # 遍历每个方法
    for method_name in method_names:
        # 获取处理方法
        method = getattr(processor, method_name, None)
        if not method:
            print(f"Method {method_name} not found in ChartDataProcessor.")
            continue
        # 调用处理方法获取数据
        processed_data = method()
        # 检查是否有数据
        if not processed_data:
            print(f"No data processed for method {method_name}.")
            continue
        # 合并到结果字典中
        result_dict[method_name] = processed_data
    # print(result_dict)
    # 切割数据并发送
    send_sliced_data(result_dict)

def send_sliced_data(data_dict):
    # keys = list(data_dict.keys())
    values = list(data_dict.values())
    data_length = len(list(values[0].values())[0])

    for i in range(data_length):
        sub_dict = {}
        for method_name, data in data_dict.items():
            sub_data = {}
            for key, value_list in data.items():
                sub_data[key] = [value_list[i]]
            sub_dict[method_name] = sub_data
        # 发送数据-json格式
        socketio.emit('update_data', json.dumps(sub_dict, ensure_ascii=False))
        time.sleep(5)
        # 在每次循环结束时检查是否接收到停止信号
        if stop_background_task.is_set():
            break
        print(sub_dict)

# 建立websocket连接
@socketio.on('connect')
def handle_connect_index():
    print('客户端连接到主页')
    csv_file_path = 'static/data/良品铺子/20220517良品铺子.csv'
    processor = ChartDataProcessor(csv_file_path)
    method_names = [
        'live_viewers_and_popularity',
        'barrage_send_time_distribution',
        'item_purchase_frequency_distribution'
    ]
    socketio.start_background_task(target=process_and_emit_data, processor=processor,
                                   method_names=method_names),

# 断开websocket连接
@socketio.on('disconnect')
def handle_disconnect_index():
    # 发送停止任务的信号
    stop_background_task.set()
    print('客户端断开连接')

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5005, debug=True, allow_unsafe_werkzeug=True)
