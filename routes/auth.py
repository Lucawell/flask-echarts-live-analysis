# encoding:utf-8
# routes/auth.py
from flask import Blueprint, jsonify, request, session, redirect, url_for, render_template
from config import USER_DATA_FILE
from utils import load_user_data, save_user_data

auth_bp = Blueprint('auth', __name__)
# 加载用户数据
users = load_user_data(USER_DATA_FILE)
# 注册用户
@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    role = data.get('role')
    brandname = data.get('brandname')
    if not username or not password or not role or not brandname:
        return jsonify({'error': 'Missing fields'}), 400
    # 检查用户名是否已存在
    if any(user['username'] == username for user in users):
        return jsonify({'error': '用户名已存在'}), 400
    user = {'id': len(users) + 1, 'username': username, 'password': password, 'role': role, 'brandname': brandname}
    users.append(user)
    save_user_data(users, USER_DATA_FILE)  # 保存用户数据到文件
    return jsonify({'message': 'User registered successfully'}), 201


# 用户登录
@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    if not username or not password:
        return jsonify({'error': 'Missing username or password'}), 400
    user = next((user for user in users if user['username'] == username and user['password'] == password), None)
    if user:
        session['username'] = user['username']
        session['role'] = user['role']
        session['brandname'] = user['brandname']
        return jsonify({'message': 'Login successful', 'user': user}), 200
    else:
        return jsonify({'error': 'Invalid username or password'}), 401


@auth_bp.route('/logout')
def logout():
    session.clear()  # 清除会话数据
    return redirect(url_for('auth.signin'))


@auth_bp.route('/user_info')
def get_user_info():
    if 'username' in session:
        username = session['username']
        brandname = session.get('brandname')  # 如果用户是 Platform 角色，则 brandname 可能不存在
        return jsonify({'username': username, 'brandname': brandname})
    else:
        return jsonify({'error': 'User not logged in'}), 401


# 登录页面路由
@auth_bp.route('/signin')
def signin():
    return render_template('signin.html')

# 注册页面路由
@auth_bp.route('/signup')
def signup():
    return render_template('signup.html')
