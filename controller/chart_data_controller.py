# encoding:utf-8
import pandas as pd
from snownlp import SnowNLP


class ChartDataProcessor:
    def __init__(self, file_path):
        self.df = None
        self.file_path = file_path

    def load_data(self):
        self.df = pd.read_csv(self.file_path, header=None, names=['用户行为', '时间戳', '时间', '用户id', '用户消息'])
        self.df['时间'] = pd.to_datetime(self.df['时间'])  # 将时间戳转换为时间对象

    def user_behavior_counts(self):
        """
        返回用户行为计数数据
        """
        self.load_data()  # 重新加载数据
        user_behavior_counts = self.df['用户行为'].value_counts().to_dict()
        return user_behavior_counts

    # 用户消息计数
    def user_message_counts(self):
        """
        返回用户消息计数数据
        """
        self.load_data()  # 重新加载数据
        user_message_counts = self.df['用户消息'].value_counts().to_dict()
        return user_message_counts

    def live_viewers_and_popularity(self, freq='25min'):
        """
        计算每个时间段的直播人数和观看热度
        参数:
        - freq: 时间段的频率，默认为每25分钟
        返回:
        - live_viewers_popularity: 包含时间段、直播人数和观看热度的DataFrame
        """
        self.load_data()  # 重新加载数据
        # 将时间设为索引
        self.df.set_index('时间', inplace=True)
        # 计算直播人数
        # live_viewers = self.df[self.df['用户行为']=='【用户关注】'].resample(freq)['用户id'].nunique()
        live_viewers = self.df.resample(freq)['用户id'].nunique()
        # 计算观看热度，假设观看热度为弹幕数量
        popularity = self.df[self.df['用户行为'] == '【实时弹幕】'].resample(freq).size()
        # 合并直播人数和观看热度数据
        live_viewers_popularity = pd.concat([live_viewers, popularity], axis=1)
        live_viewers_popularity.columns = ['直播人数', '观看热度']
        # 填充NaN值为0
        live_viewers_popularity.fillna(0, inplace=True)
        # 转换成字典
        # 转换DataFrame为字典
        chart_data = {
            '时间段': live_viewers_popularity.index.strftime('%Y-%m-%d %H:%M').tolist(),
            '直播人数': live_viewers_popularity['直播人数'].tolist(),
            '观看热度': live_viewers_popularity['观看热度'].tolist()
        }
        return chart_data

    # 弹幕发送时间分布
    def barrage_send_time_distribution(self, freq='60min'):
        """
        计算弹幕发送时间分布
        参数:
        - freq: 时间段的频率，默认为每25分钟
        返回:
        - barrage_send_time_distribution: 包含时间段和弹幕发送数量的DataFrame
        """
        self.load_data()  # 重新加载数据
        # 将时间设为索引
        self.df.set_index('时间', inplace=True)
        # 计算弹幕发送时间分布
        barrage_send_time_distribution = self.df[self.df['用户行为'] == '【实时弹幕】'].resample(freq).size()
        # 转换成字典
        # 转换Series为字典
        chart_data = {
            '时间段': barrage_send_time_distribution.index.strftime('%Y-%m-%d %H:%M').tolist(),
            '弹幕发送数量': barrage_send_time_distribution.tolist()
        }
        return chart_data

    # 用户平均停留时间
    def user_average_stay_time(self, freq='1H'):
        """
        计算每个时间段的用户平均停留时长分布数据
        参数:
        - freq: 时间段的频率，默认为每小时
        :return: 字典，键是时间段的起始时间，值是该时间段内的平均停留时长
        """
        # 计算用户停留时长
        self.load_data()  # 重新加载数据
        self.df['停留时长'] = self.df.groupby('用户id')['时间'].diff().dt.total_seconds()
        # 根据频率对数据进行分组，并计算每个时间段内的平均停留时长
        user_average_stay_time = self.df.groupby(pd.Grouper(key='时间', freq=freq)).agg({'停留时长': 'mean'}).to_dict()[
            '停留时长']
        formatted_time_segments = [timestamp.strftime('%Y-%m-%d %H:%M') for timestamp in user_average_stay_time.keys()]
        # NaN值填充为0
        user_average_stay_time.update((k, 1) for k, v in user_average_stay_time.items() if pd.isna(v))
        # 转换成字典
        chart_data = {
            '时间段': formatted_time_segments,
            '平均停留时长': list(user_average_stay_time.values())
        }
        return chart_data

    # 主播行为与用户互动的时间差分布
    def time_diff_data(self):
        """
        返回主播行为后到下一次用户互动的时间差数据
        """
        self.load_data()  # 重新加载数据
        anchor_actions = ['【主播推送商品】', '【主播弹幕】']
        user_interactions = ['【实时弹幕】', '【用户关注】']
        anchor_data = self.df[self.df['用户行为'].isin(anchor_actions)]
        user_data = self.df[self.df['用户行为'].isin(user_interactions)]

        time_diffs = []

        for _, anchor_row in anchor_data.iterrows():
            anchor_time = anchor_row['时间']
            post_anchor_interactions = user_data[user_data['时间'] > anchor_time]
            if not post_anchor_interactions.empty:
                nearest_interaction_time = post_anchor_interactions['时间'].min()
                time_diff = (nearest_interaction_time - anchor_time).total_seconds()
                time_diffs.append(time_diff)

        # 使用 numpy.histogram 函数计算时间差的直方图数据
        import numpy as np
        hist, bins = np.histogram(time_diffs, bins=50)
        # 构建字典返回数据
        x_axis = [f'{int(bins[i])} - {int(bins[i + 1])}' for i in range(len(bins) - 1)]
        y_axis = hist.tolist()
        return {'时间差': x_axis, '频次': y_axis}

        # return time_diffs

    def item_purchase_distribution(self, top_n=8):
        """
        计算商品购买数量分布
        参数:
        - top_n: 控制显示数量较大的数据的数量，默认为 None，即显示所有数据
        返回:
        - item_purchase_distribution: 包含商品和购买数量的DataFrame
        """
        self.load_data()  # 重新加载数据
        # 筛选出购买行为的数据
        buy_data = self.df[self.df['用户行为'] == '【用户正在购买】']
        # 统计每个商品的购买数量
        item_purchase_distribution = buy_data['用户消息'].value_counts().sort_values(ascending=False)
        # 如果指定了 top_n，则只保留前 top_n 个数据
        if top_n is not None:
            item_purchase_distribution = item_purchase_distribution.head(top_n)
        # 转换成字典
        chart_data = {
            '商品': item_purchase_distribution.index.tolist(),
            '购买数量': item_purchase_distribution.values.tolist()
        }
        return chart_data

    def item_purchase_frequency_distribution(self, freq='10min'):
        """
        计算商品购买数量时间分布
        参数:
        - freq: 控制时间间隔的频率，默认为每小时（'H'）
            'T': 分钟
            'H': 小时
            'D': 天
        返回:
        - item_purchase_hourly_distribution: 包含时间和购买数量的DataFrame
        """
        self.load_data()  # 重新加载数据
        # 过滤出购买活动的数据
        buy_data = self.df[self.df['用户行为'] == '【用户正在购买】']
        # 将时间设为索引并按照指定频率统计购买数量
        frequency_buy_count = buy_data.resample(freq, on='时间')['用户id'].count()
        # 转换成字典
        chart_data = {
            '时间段': frequency_buy_count.index.strftime('%Y-%m-%d %H:%M:%S').tolist(),
            '购买数量': frequency_buy_count.values.tolist()
        }
        return chart_data

    def get_basic_data(self):
        self.load_data()  # 重新加载数据
        # 计算购买人数
        purchase_count = self.df[self.df['用户行为'] == '【用户正在购买】']['用户id'].nunique()
        # 计算购买次数
        purchase_frequency = self.df[self.df['用户行为'] == '【用户正在购买】'].shape[0]
        # 筛选出主播开始和结束讲解的行
        start_lecture_rows = self.df[self.df['用户行为'] == '【主播开始讲解】']
        end_lecture_rows = self.df[self.df['用户行为'] == '【主播结束讲解】']
        # 计算讲解时长
        lecture_time = end_lecture_rows['时间戳'].mean() - start_lecture_rows['时间戳'].mean()
        # 计算讲解时长（分钟）
        average_explanation_duration = round(lecture_time / 1000 / 60, 2)
        # 计算加入购物车人数
        cart_count = self.df[self.df['用户行为'] == '【用户加入购物车】']['用户id'].nunique()
        # 计算在线人数
        online_users = self.df[self.df['用户行为'].isin(
            ['【用户正在购买】', '【实时弹幕】', '【用户加入购物车】', '【用户进入店铺】', '【用户关注】'])]['用户id'].nunique()

        chart_data = {
            '购买人数': purchase_count,
            '购买次数': purchase_frequency,
            '平均讲解时长': average_explanation_duration,
            '加入购物车人数': cart_count,
            '在线人数': online_users
        }
        return chart_data

    def generate_barrage_wordcloud_data(self):
        self.load_data()  # 重新加载数据
        # 获取弹幕数据
        barrage_messages = self.df[self.df['用户行为'] == '【实时弹幕】']['用户消息'].tolist()
        # 计算词频
        word_freq = {}
        for message in barrage_messages:
            words = message.split()  # 假设弹幕消息以空格分隔单词
            for word in words:
                # 去除纯数字的词
                if not word.isdigit():
                    if word in word_freq:
                        word_freq[word] += 1
                    else:
                        word_freq[word] = 1
        # 格式化词云数据为 ECharts 所需格式
        wordcloud_data = [{'name': word, 'value': int(freq)} for word, freq in word_freq.items()]
        return wordcloud_data

    def positive_negative_neutral_barrage_by_time(self):
        """
        构建各时间段正负面弹幕统计的字典数据
        返回:
        - chart_data: 各时间段正负面弹幕统计的字典数据
        """
        # 计算积极、消极和中性弹幕数量
        self.load_data()  # 重新加载数据
        # 将用户消息转换为字符串类型
        self.df['用户消息'] = self.df['用户消息'].astype(str)
        positive_counts = []
        negative_counts = []
        neutral_counts = []
        # 划分时间段
        start_time = self.df['时间'].min()
        end_time = self.df['时间'].max()
        time_interval = pd.date_range(start=start_time, end=end_time, freq='30min')
        # 统计每个时间段内的积极、消极和中性弹幕数量
        for i in range(len(time_interval) - 1):
            start = time_interval[i]
            end = time_interval[i + 1]
            positive_count = 0
            negative_count = 0
            neutral_count = 0
            for index, row in self.df.iterrows():
                if start <= row['时间'] < end:
                    message = row['用户消息']
                    # 利用 SnowNLP 进行情感分析
                    sentiment_score = SnowNLP(message).sentiments
                    # 判断情感倾向并统计数量
                    if sentiment_score > 0.5:
                        positive_count += 1
                    elif sentiment_score < 0.3:
                        negative_count += 1
                    else:
                        neutral_count += 1
            positive_counts.append(positive_count)
            negative_counts.append(negative_count)
            neutral_counts.append(neutral_count)
        # 构建字典数据
        chart_data = {
            '时间段': [start_time.strftime('%Y-%m-%d %H:%M')] + [interval.strftime('%Y-%m-%d %H:%M') for interval in
                                                                 time_interval[1:]],
            'Positive': positive_counts,
            'Negative': negative_counts,
            'Neutral': neutral_counts
        }
        return chart_data
