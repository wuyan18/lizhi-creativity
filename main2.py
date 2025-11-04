import streamlit as st
import pandas as pd
import json
import os
import course2
from datetime import datetime

# 设置页面配置
st.set_page_config(
    page_title="荔枝营地 - 集体学习平台",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 极简CSS - 只修复基本样式
st.markdown("""
<style>
/* 仅保留必要的样式修复 */
.stButton>button {
    border-radius: 8px;
    border: none;
    padding: 0.5rem 1rem;
}

.stTextInput>div>div>input {
    border-radius: 8px;
}
</style>
""", unsafe_allow_html=True)

# 数据文件路径
USER_RELATIONSHIPS_FILE = "user_relationships.json"

def load_user_relationships():
    """加载用户关系数据"""
    try:
        if os.path.exists(USER_RELATIONSHIPS_FILE):
            with open(USER_RELATIONSHIPS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        else:
            return {}
    except Exception as e:
        st.error(f"加载用户关系数据失败: {str(e)}")
        return {}

def save_user_relationships():
    """保存用户关系数据"""
    try:
        with open(USER_RELATIONSHIPS_FILE, 'w', encoding='utf-8') as f:
            json.dump(st.session_state.user_relationships, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        st.error(f"保存用户关系数据失败: {str(e)}")
        return False

# 初始化session state
if 'active_tab' not in st.session_state:
    st.session_state.active_tab = "网站介绍"

# 初始化用户系统
if 'users' not in st.session_state:
    st.session_state.users = course2.load_users()
if 'current_user' not in st.session_state:
    st.session_state.current_user = None
if 'invite_codes' not in st.session_state:
    st.session_state.invite_codes = course2.load_invite_codes()
if 'user_relationships' not in st.session_state:
    st.session_state.user_relationships = load_user_relationships()

def authenticate_user(username, password):
    """用户认证"""
    if username in st.session_state.users:
        stored_password = st.session_state.users[username].get("password")
        return stored_password == password
    return False

def register_user(username, password, invite_code=None):
    """用户注册"""
    if not username or not password:
        return False, "请输入用户名和密码"
    
    if username in st.session_state.users:
        return False, "用户名已存在"
    
    # 检查是否是第一个用户
    is_first_user = len(st.session_state.users) == 0
    user_role = "user"
    
    # 首个用户自动成为管理员
    if is_first_user:
        user_role = "admin"
        message = "🎉 恭喜！您是该系统的首个用户，已自动成为管理员。"
    # 有有效邀请码的用户成为管理员
    elif invite_code and check_invite_code(invite_code):
        user_role = "admin"
        message = "🎉 欢迎管理员！邀请码验证成功。"
        # 标记邀请码为已使用
        mark_invite_code_used(invite_code, username)
    else:
        message = "注册成功！"
    
    st.session_state.users[username] = {
        "password": password,
        "role": user_role,
        "created_at": datetime.now().isoformat(),
        "invite_used": invite_code if invite_code else None
    }
    
    course2.save_users(st.session_state.users)
    return True, message

def check_invite_code(code):
    """检查邀请码有效性"""
    if code in st.session_state.invite_codes:
        invite_info = st.session_state.invite_codes[code]
        return not invite_info.get("used", False)
    return False

def mark_invite_code_used(code, username):
    """标记邀请码为已使用"""
    if code in st.session_state.invite_codes:
        st.session_state.invite_codes[code]["used"] = True
        st.session_state.invite_codes[code]["used_by"] = username
        st.session_state.invite_codes[code]["used_at"] = datetime.now().isoformat()
        course2.save_invite_codes(st.session_state.invite_codes)
        return True
    return False

def send_binding_request(target_username):
    """发送绑定请求"""
    if not st.session_state.current_user:
        return False, "请先登录"
    
    if target_username == st.session_state.current_user:
        return False, "不能绑定自己"
    
    if target_username not in st.session_state.users:
        return False, "用户不存在"
    
    # 初始化用户关系
    if st.session_state.current_user not in st.session_state.user_relationships:
        st.session_state.user_relationships[st.session_state.current_user] = {
            "sent_requests": [],
            "received_requests": [],
            "binded_users": []
        }
    
    if target_username not in st.session_state.user_relationships:
        st.session_state.user_relationships[target_username] = {
            "sent_requests": [],
            "received_requests": [],
            "binded_users": []
        }
    
    # 检查是否已经绑定
    if target_username in st.session_state.user_relationships[st.session_state.current_user]["binded_users"]:
        return False, "已经绑定该用户"
    
    # 检查是否已经发送过请求
    if target_username in st.session_state.user_relationships[st.session_state.current_user]["sent_requests"]:
        return False, "已经发送过绑定请求"
    
    # 发送请求
    st.session_state.user_relationships[st.session_state.current_user]["sent_requests"].append(target_username)
    st.session_state.user_relationships[target_username]["received_requests"].append(st.session_state.current_user)
    
    save_user_relationships()
    return True, f"已向 {target_username} 发送绑定请求"

def accept_binding_request(from_username):
    """接受绑定请求"""
    if not st.session_state.current_user:
        return False, "请先登录"
    
    # 移除请求
    st.session_state.user_relationships[st.session_state.current_user]["received_requests"].remove(from_username)
    st.session_state.user_relationships[from_username]["sent_requests"].remove(st.session_state.current_user)
    
    # 建立绑定关系
    st.session_state.user_relationships[st.session_state.current_user]["binded_users"].append(from_username)
    st.session_state.user_relationships[from_username]["binded_users"].append(st.session_state.current_user)
    
    save_user_relationships()
    return True, f"已与 {from_username} 建立绑定关系"

def reject_binding_request(from_username):
    """拒绝绑定请求"""
    if not st.session_state.current_user:
        return False, "请先登录"
    
    # 移除请求
    st.session_state.user_relationships[st.session_state.current_user]["received_requests"].remove(from_username)
    st.session_state.user_relationships[from_username]["sent_requests"].remove(st.session_state.current_user)
    
    save_user_relationships()
    return True, f"已拒绝 {from_username} 的绑定请求"

def get_binded_users():
    """获取已绑定的用户列表"""
    if not st.session_state.current_user:
        return []
    
    user_rels = st.session_state.user_relationships.get(st.session_state.current_user, {})
    return user_rels.get("binded_users", [])

def is_user_binded(username):
    """检查用户是否已绑定"""
    if not st.session_state.current_user:
        return False
    
    binded_users = get_binded_users()
    return username in binded_users

# 完全重写的登录系统 - 纯Streamlit组件
def global_login_system():
    """全局登录系统 - 完全重写版本"""
    # 顶部标题栏
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.title("🍈 荔枝营地")
        st.caption("集体学习平台 • 日程与课表汇总")
    
    with col2:
        if st.session_state.current_user:
            user_info = st.session_state.users.get(st.session_state.current_user, {})
            user_role = user_info.get("role", "user")
            role_display = "👑 管理员" if user_role == "admin" else "👤 普通用户"
            
            st.write(f"欢迎，**{st.session_state.current_user}**")
            st.write(f"*{role_display}*")
            
            if st.button("退出登录", key="logout_btn"):
                st.session_state.current_user = None
                st.rerun()
        else:
            if st.button("🔐 登录/注册", key="login_btn", type="primary"):
                st.session_state.show_login_modal = True
                st.rerun()

# 登录/注册模态框 - 使用Streamlit原生组件
if 'show_login_modal' not in st.session_state:
    st.session_state.show_login_modal = False

def login_modal():
    """登录模态框 - 完全重写"""
    if st.session_state.show_login_modal:
        # 使用st.container创建模态框效果
        with st.container():
            st.markdown("---")
            st.subheader("🔐 用户登录/注册")
            
            tab1, tab2 = st.tabs(["登录", "注册"])
            
            with tab1:
                username = st.text_input("用户名", key="modal_login_username")
                password = st.text_input("密码", type="password", key="modal_login_password")
                
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("登录", use_container_width=True, key="login_submit"):
                        if authenticate_user(username, password):
                            st.session_state.current_user = username
                            st.session_state.show_login_modal = False
                            st.success("登录成功!")
                            st.rerun()
                        else:
                            st.error("用户名或密码错误")
                with col2:
                    if st.button("取消", use_container_width=True, key="login_cancel"):
                        st.session_state.show_login_modal = False
                        st.rerun()
            
            with tab2:
                new_username = st.text_input("新用户名", key="modal_reg_username")
                new_password = st.text_input("新密码", type="password", key="modal_reg_password")
                invite_code = st.text_input("管理员邀请码（可选）", key="modal_invite_code")
                
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("注册", use_container_width=True, key="reg_submit"):
                        success, message = register_user(new_username, new_password, invite_code)
                        if success:
                            st.session_state.current_user = new_username
                            st.session_state.show_login_modal = False
                            st.success(message)
                            st.rerun()
                        else:
                            st.error(message)
                with col2:
                    if st.button("取消", use_container_width=True, key="reg_cancel"):
                        st.session_state.show_login_modal = False
                        st.rerun()
            
            st.markdown("---")

# 账号绑定管理
def account_binding_section():
    """账号绑定管理界面"""
    st.header("🔗 账号绑定管理")
    
    if not st.session_state.current_user:
        st.warning("请先登录以使用账号绑定功能")
        return
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("发送绑定请求")
        target_username = st.text_input("输入要绑定的用户名:", key="bind_target")
        if st.button("发送绑定请求", use_container_width=True, key="send_bind_request"):
            success, message = send_binding_request(target_username)
            if success:
                st.success(message)
                st.rerun()
            else:
                st.error(message)
    
    with col2:
        st.subheader("待处理请求")
        user_rels = st.session_state.user_relationships.get(st.session_state.current_user, {})
        received_requests = user_rels.get("received_requests", [])
        
        if received_requests:
            for req_user in received_requests:
                col_req1, col_req2 = st.columns([2, 1])
                with col_req1:
                    st.write(f"**{req_user}** 请求绑定")
                with col_req2:
                    col_btn1, col_btn2 = st.columns(2)
                    with col_btn1:
                        if st.button("✅", key=f"accept_{req_user}"):
                            success, message = accept_binding_request(req_user)
                            if success:
                                st.success(message)
                                st.rerun()
                    with col_btn2:
                        if st.button("❌", key=f"reject_{req_user}"):
                            success, message = reject_binding_request(req_user)
                            if success:
                                st.success(message)
                                st.rerun()
        else:
            st.info("暂无待处理请求")
    
    st.subheader("已绑定用户")
    binded_users = get_binded_users()
    if binded_users:
        for binded_user in binded_users:
            st.success(f"✅ {binded_user}")
    else:
        st.info("暂无绑定用户")
    
    st.subheader("已发送的请求")
    user_rels = st.session_state.user_relationships.get(st.session_state.current_user, {})
    sent_requests = user_rels.get("sent_requests", [])
    if sent_requests:
        for sent_user in sent_requests:
            st.info(f"⏳ 已向 {sent_user} 发送请求，等待对方确认")
    else:
        st.info("暂无已发送的请求")

# 修改后的日程显示函数
def display_schedule_section_modified():
    """修改后的日程分享部分，只显示绑定用户的日程"""
    # 数据文件路径
    DATA_FILE = "saved_texts.json"
    
    # 初始化数据
    def load_data():
        if os.path.exists(DATA_FILE):
            try:
                with open(DATA_FILE, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return []
        return []
    
    def save_data(data):
        with open(DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    # 初始化session state
    if 'saved_texts' not in st.session_state:
        st.session_state.saved_texts = load_data()
    
    if 'text_counter' not in st.session_state:
        if st.session_state.saved_texts:
            st.session_state.text_counter = max([text['id'] for text in st.session_state.saved_texts]) + 1
        else:
            st.session_state.text_counter = 0
    
    # 使用自定义的session state来存储当前文本
    if 'current_text' not in st.session_state:
        st.session_state.current_text = ""
    
    if 'current_title' not in st.session_state:
        st.session_state.current_title = f"文本_{st.session_state.text_counter + 1}"
    
    # 检查登录状态
    if not st.session_state.current_user:
        st.warning("请先登录以查看和分享日程")
        return
    
    # 获取绑定用户列表
    binded_users = get_binded_users()
    
    # 显示保存的文本 - 只显示当前用户和绑定用户的文本
    st.markdown("---")
    
    # 过滤文本：只显示当前用户和绑定用户的文本
    visible_texts = []
    for text in st.session_state.saved_texts:
        author = text.get('author', '未知')
        if author == st.session_state.current_user or author in binded_users:
            visible_texts.append(text)
    
    st.subheader(f"共享日程 共 ({len(visible_texts)} 条)")
    
    if not visible_texts:
        st.info("还没有导入过任何日程，请在下方输入并保存您的第一条日程。")
    else:
        # 搜索和过滤功能
        st.subheader("🔍 搜索与筛选")
        col1, col2, col3 = st.columns([2, 1, 1])
        
        with col1:
            search_term = st.text_input("搜索文本内容:", placeholder="输入关键词搜索...", key="search_schedule")
        
        with col2:
            category_filter = st.selectbox(
                "分类筛选:",
                ["所有分类"] + list(set([text.get('category', '未分类') for text in visible_texts])),
                key="category_filter_schedule"
            )
        
        with col3:
            sort_option = st.selectbox("排序方式:", ["最新优先", "最早优先", "标题A-Z", "标题Z-A"], key="sort_schedule")
        
        # 过滤文本
        filtered_texts = visible_texts
        
        if search_term:
            filtered_texts = [
                text for text in filtered_texts
                if search_term.lower() in text['content'].lower() or 
                   search_term.lower() in text['title'].lower()
            ]
        
        if category_filter != "所有分类":
            filtered_texts = [
                text for text in filtered_texts
                if text.get('category', '未分类') == category_filter
            ]
        
        # 排序
        if sort_option == "最新优先":
            filtered_texts = sorted(filtered_texts, key=lambda x: x['created_at'], reverse=True)
        elif sort_option == "最早优先":
            filtered_texts = sorted(filtered_texts, key=lambda x: x['created_at'])
        elif sort_option == "标题A-Z":
            filtered_texts = sorted(filtered_texts, key=lambda x: x['title'])
        elif sort_option == "标题Z-A":
            filtered_texts = sorted(filtered_texts, key=lambda x: x['title'], reverse=True)
        
        # 显示统计信息
        if filtered_texts:
            total_chars = sum(text['char_count'] for text in filtered_texts)
            st.caption(f"找到 {len(filtered_texts)} 条文本，共 {total_chars} 字符")
        
        # 显示过滤后的文本
        if not filtered_texts:
            st.warning("没有找到符合条件的文本")
        else:
            for i, text_entry in enumerate(filtered_texts):
                with st.container():
                    # 标题栏
                    col_title, col_category, col_author = st.columns([2, 1, 1])
                    with col_title:
                        st.markdown(f"### {text_entry['title']}")
                    with col_category:
                        st.caption(f"📁 {text_entry.get('category', '未分类')}")
                    with col_author:
                        author = text_entry.get('author', '未知')
                        if author == st.session_state.current_user:
                            st.caption("👤 我")
                        else:
                            st.caption(f"👥 {author}")
                    
                    # 元信息
                    col_meta1, col_meta2, col_meta3 = st.columns(3)
                    with col_meta1:
                        st.caption(f"📅 {text_entry['created_at']}")
                    with col_meta2:
                        st.caption(f"📊 {text_entry['char_count']} 字符")
                    with col_meta3:
                        if text_entry['tags']:
                            st.caption(f"🏷️ {', '.join(text_entry['tags'])}")
                    
                    # 文本内容（可折叠）
                    with st.expander("查看内容", expanded=(i == 0 and len(filtered_texts) <= 3)):
                        st.text_area(
                            "内容:",
                            value=text_entry['content'],
                            height=min(200, max(100, len(text_entry['content']) // 4)),
                            key=f"content_{text_entry['id']}",
                            disabled=True
                        )
                    
                    # 操作按钮 - 只允许编辑和删除自己的文本
                    col_btn1, col_btn2, col_btn3 = st.columns(3)
                    with col_btn1:
                        if st.button(f"📋 复制", key=f"copy_{text_entry['id']}"):
                            st.code(text_entry['content'], language="text")
                            st.success("内容已复制到代码块")
                    
                    # 只有作者本人可以编辑和删除
                    if text_entry.get('author') == st.session_state.current_user:
                        with col_btn2:
                            if st.button(f"✏️ 编辑", key=f"edit_{text_entry['id']}"):
                                # 设置编辑模式
                                st.session_state.editing_id = text_entry['id']
                                st.rerun()
                        
                        with col_btn3:
                            if st.button(f"🗑️ 删除", key=f"delete_{text_entry['id']}"):
                                st.session_state.saved_texts = [
                                    text for text in st.session_state.saved_texts 
                                    if text['id'] != text_entry['id']
                                ]
                                save_data(st.session_state.saved_texts)
                                st.success("文本已删除")
                                st.rerun()
                    else:
                        with col_btn2:
                            st.button(f"👀 查看", key=f"view_{text_entry['id']}", disabled=True)
                        with col_btn3:
                            st.button(f"🔒 锁定", key=f"lock_{text_entry['id']}", disabled=True)
                    
                    st.markdown("---")
            
            # 编辑功能
            if 'editing_id' in st.session_state:
                editing_id = st.session_state.editing_id
                text_to_edit = next((text for text in st.session_state.saved_texts if text['id'] == editing_id), None)
                
                if text_to_edit:
                    st.subheader("✏️ 编辑文本")
                    
                    edited_title = st.text_input("标题:", value=text_to_edit['title'], key="edit_title_schedule")
                    edited_content = st.text_area("内容:", value=text_to_edit['content'], height=200, key="edit_content_schedule")
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button("💾 保存修改", key="save_edit_schedule"):
                            text_to_edit['title'] = edited_title
                            text_to_edit['content'] = edited_content
                            text_to_edit['updated_at'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                            text_to_edit['char_count'] = len(edited_content)
                            
                            save_data(st.session_state.saved_texts)
                            del st.session_state.editing_id
                            st.success("修改已保存!")
                            st.rerun()
                    
                    with col2:
                        if st.button("❌ 取消编辑", key="cancel_edit_schedule"):
                            del st.session_state.editing_id
                            st.rerun()
    
    # 文本输入区域
    st.subheader("添加新日程")
    
    # 文本标题
    st.session_state.current_title = st.text_input(
        "日程标题:",
        placeholder="给这段日程起个名字",
        value=st.session_state.current_title,
        key="schedule_title_input"
    )
    
    # 文本内容
    new_text = st.text_area(
        "输入您要保存的日程内容:",
        placeholder="在这里输入您的日程安排...",
        height=150,
        value=st.session_state.current_text,
        key="schedule_content_input"
    )
    
    # 更新自定义session state
    st.session_state.current_text = new_text
    
    # 标签和分类
    col1, col2 = st.columns(2)
    with col1:
        tags = st.text_input(
            "标签 (可选):",
            placeholder="用逗号分隔标签，如：工作,重要,笔记",
            key="schedule_tags_input"
        )
    with col2:
        category = st.selectbox(
            "分类:",
            ["未分类", "工作", "个人", "学习", "想法", "其他"],
            key="schedule_category_select"
        )
    
    # 保存和清空按钮
    col1, col2, col3 = st.columns([1, 1, 3])
    
    with col1:
        if st.button("💾 保存日程", use_container_width=True, key="save_schedule_btn"):
            if st.session_state.current_text.strip():
                # 创建文本条目
                text_entry = {
                    'id': st.session_state.text_counter,
                    'title': st.session_state.current_title if st.session_state.current_title else f"文本_{st.session_state.text_counter + 1}",
                    'content': st.session_state.current_text,
                    'tags': [tag.strip() for tag in tags.split(",")] if tags else [],
                    'category': category,
                    'author': st.session_state.current_user,
                    'created_at': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    'updated_at': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    'char_count': len(st.session_state.current_text)
                }
                
                # 添加到保存的文本列表
                st.session_state.saved_texts.append(text_entry)
                st.session_state.text_counter += 1
                
                # 保存到文件
                save_data(st.session_state.saved_texts)
                
                # 清空当前输入
                st.session_state.current_text = ""
                st.session_state.current_title = f"文本_{st.session_state.text_counter + 1}"
                
                st.success("✅ 日程已保存!")
                st.rerun()
            else:
                st.warning("⚠️ 请输入日程内容")

# 主界面
def main():
    """主函数"""
    # 显示全局登录系统
    global_login_system()
    
    # 显示登录模态框（如果需要）
    if st.session_state.show_login_modal:
        login_modal()
    
    # 创建导航标签
    st.markdown("---")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("🏠 网站介绍", use_container_width=True, 
                    type="primary" if st.session_state.active_tab == "网站介绍" else "secondary"):
            st.session_state.active_tab = "网站介绍"
            st.rerun()
    
    with col2:
        if st.button("📅 日程分享", use_container_width=True,
                    type="primary" if st.session_state.active_tab == "日程分享" else "secondary"):
            st.session_state.active_tab = "日程分享"
            st.rerun()
    
    with col3:
        if st.button("📚 课表窗口", use_container_width=True,
                    type="primary" if st.session_state.active_tab == "课表窗口" else "secondary"):
            st.session_state.active_tab = "课表窗口"
            st.rerun()
    
    with col4:
        if st.button("🔗 账号绑定", use_container_width=True,
                    type="primary" if st.session_state.active_tab == "账号绑定" else "secondary"):
            st.session_state.active_tab = "账号绑定"
            st.rerun()
    
    st.markdown("---")
    
    # 页面内容
    if st.session_state.active_tab == "网站介绍":
        st.header("✨ 欢迎来到荔枝营地集体学习平台！")
        st.write("这是一个专为学生设计的学习和交流平台。")
        st.write("在这里，你可以找到志同道合的学习伙伴，分享学习资源，制定学习计划。")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("主要功能")
            st.markdown("""
            - 🔗 **账号绑定**：与学习伙伴建立连接
            - 📚 **课程分享**：共享课程信息和课表
            - 📅 **日程安排**：管理学习和生活日程
            - 👥 **协作学习**：与伙伴共同进步
            """)
        
        with col2:
            st.subheader("使用指南")
            st.markdown("""
            1. 首先注册/登录账号
            2. 在账号绑定页面添加学习伙伴
            3. 上传你的课表和日程
            4. 开始与伙伴共享学习信息
            """)
        
        st.info("💡 温馨提示：请先登录并绑定账号，才能查看伙伴的课表和日程信息")

    elif st.session_state.active_tab == "课表窗口":
        st.header("📚 课表窗口")
        st.write("引入你的课表，来告诉ta你今天上什么课吧！")
        course2.timetable_management_tab_modified(get_binded_users())
        
    elif st.session_state.active_tab == "日程分享":
        st.header("📅 日程分享")
        st.write("与学习伙伴共享你的日程安排")
        display_schedule_section_modified()
        
    elif st.session_state.active_tab == "账号绑定":
        st.header("🔗 账号绑定")
        st.write("与学习伙伴建立连接，共享学习信息")
        account_binding_section()

# 运行主程序
if __name__ == "__main__":
    main()