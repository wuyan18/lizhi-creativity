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

def register_user(username, password, invite_code, users, invite_codes):
    """用户注册"""
    if not username or not password:
        return False, "请输入用户名和密码"
    
    if username in users:
        return False, "用户名已存在"
    
    # 检查是否是第一个用户
    is_first_user = len(users) == 0
    user_role = "user"
    
    # 首个用户自动成为管理员
    if is_first_user:
        user_role = "admin"
        message = "🎉 恭喜！您是该系统的首个用户，已自动成为管理员。"
    # 有有效邀请码的用户成为管理员
    elif invite_code and check_invite_code(invite_code, invite_codes):
        user_role = "admin"
        message = "🎉 欢迎管理员！邀请码验证成功。"
        # 标记邀请码为已使用
        mark_invite_code_used(invite_code, username, invite_codes)
    else:
        message = "注册成功！"
    
    users[username] = {
        "password": password,
        "role": user_role,
        "created_at": datetime.now().isoformat(),
        "invite_used": invite_code if invite_code else None
    }
    
    return True, message

def check_invite_code(code, invite_codes):
    """检查邀请码有效性"""
    if code in invite_codes:
        invite_info = invite_codes[code]
        return not invite_info.get("used", False)
    return False

def mark_invite_code_used(code, username, invite_codes):
    """标记邀请码为已使用"""
    if code in invite_codes:
        invite_codes[code]["used"] = True
        invite_codes[code]["used_by"] = username
        invite_codes[code]["used_at"] = datetime.now().isoformat()
        return True
    return False

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