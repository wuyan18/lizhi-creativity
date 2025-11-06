# auth.py
import streamlit as st
import json
import os
from datetime import datetime

def load_user_relationships():
    """加载用户关系数据"""
    try:
        if os.path.exists("user_relationships.json"):
            with open("user_relationships.json", 'r', encoding='utf-8') as f:
                return json.load(f)
        else:
            return {}
    except Exception as e:
        st.error(f"加载用户关系数据失败: {str(e)}")
        return {}

def save_user_relationships(user_relationships):
    """保存用户关系数据"""
    try:
        with open("user_relationships.json", 'w', encoding='utf-8') as f:
            json.dump(user_relationships, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        st.error(f"保存用户关系数据失败: {str(e)}")
        return False

def authenticate_user(username, password, users):
    """用户认证"""
    if username in users:
        stored_password = users[username].get("password")
        return stored_password == password
    return False

def register_user(username, password, users):
    """用户注册 - 移除邀请码功能"""
    if not username or not password:
        return False, "请输入用户名和密码"
    
    if username in users:
        return False, "用户名已存在"
    
    users[username] = {
        "password": password,
        "created_at": datetime.now().isoformat()
    }
    
    return True, "注册成功！"

def send_binding_request(target_username, current_user, user_relationships):
    """发送绑定请求"""
    if not current_user:
        return False, "请先登录"
    
    if target_username == current_user:
        return False, "不能绑定自己"
    
    # 初始化用户关系
    if current_user not in user_relationships:
        user_relationships[current_user] = {
            "sent_requests": [],
            "received_requests": [],
            "binded_users": []
        }
    
    if target_username not in user_relationships:
        user_relationships[target_username] = {
            "sent_requests": [],
            "received_requests": [],
            "binded_users": []
        }
    
    # 检查是否已经绑定
    if target_username in user_relationships[current_user]["binded_users"]:
        return False, "已经绑定该用户"
    
    # 检查是否已经发送过请求
    if target_username in user_relationships[current_user]["sent_requests"]:
        return False, "已经发送过绑定请求"
    
    # 发送请求
    user_relationships[current_user]["sent_requests"].append(target_username)
    user_relationships[target_username]["received_requests"].append(current_user)
    
    return True, f"已向 {target_username} 发送绑定请求"

def accept_binding_request(from_username, current_user, user_relationships):
    """接受绑定请求"""
    if not current_user:
        return False, "请先登录"
    
    # 移除请求
    user_relationships[current_user]["received_requests"].remove(from_username)
    user_relationships[from_username]["sent_requests"].remove(current_user)
    
    # 建立绑定关系
    user_relationships[current_user]["binded_users"].append(from_username)
    user_relationships[from_username]["binded_users"].append(current_user)
    
    return True, f"已与 {from_username} 建立绑定关系"

def reject_binding_request(from_username, current_user, user_relationships):
    """拒绝绑定请求"""
    if not current_user:
        return False, "请先登录"
    
    # 移除请求
    user_relationships[current_user]["received_requests"].remove(from_username)
    user_relationships[from_username]["sent_requests"].remove(current_user)
    
    return True, f"已拒绝 {from_username} 的绑定请求"

def unbind_user(target_username, current_user, user_relationships):
    """解除绑定关系"""
    if not current_user:
        return False, "请先登录"
    
    if target_username == current_user:
        return False, "不能解除与自己的绑定"
    
    # 检查是否已绑定
    if target_username not in user_relationships.get(current_user, {}).get("binded_users", []):
        return False, "未绑定该用户"
    
    # 从双方的绑定列表中移除
    if current_user in user_relationships and "binded_users" in user_relationships[current_user]:
        user_relationships[current_user]["binded_users"].remove(target_username)
    
    if target_username in user_relationships and "binded_users" in user_relationships[target_username]:
        user_relationships[target_username]["binded_users"].remove(current_user)
    
    return True, f"已解除与 {target_username} 的绑定关系"

def get_binded_users(current_user, user_relationships):
    """获取已绑定的用户列表"""
    if not current_user:
        return []
    
    user_rels = user_relationships.get(current_user, {})
    return user_rels.get("binded_users", [])

def is_user_binded(username, current_user, user_relationships):
    """检查用户是否已绑定"""
    if not current_user:
        return False
    
    binded_users = get_binded_users(current_user, user_relationships)
    return username in binded_users