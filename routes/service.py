# encoding:utf-8
# routes/service.py
from flask import Blueprint, render_template

service_bp = Blueprint('service', __name__)

# 主页路由
@service_bp.route('/')
def index():
    return render_template('index1.html')

# 销售页面路由
@service_bp.route('/sales')
def sales():
    return render_template('static-sales.html')

# 热度图页面路由
@service_bp.route('/heat')
def heat():
    return render_template('static-heat.html')

# 情感分析页面路由
@service_bp.route('/emotional')
def emotional():
    return render_template('static-emotional.html')

# # 登录页面路由
# @service_bp.route('/signin')
# def signin():
#     return render_template('signin.html')
#
# # 注册页面路由
# @service_bp.route('/signup')
# def signup():
#     return render_template('signup.html')
