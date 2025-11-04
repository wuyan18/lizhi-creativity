# timetable_module.py
import streamlit as st
import pandas as pd
from io import BytesIO
import datetime
import uuid
import hashlib
import os
import json
import pickle
import random
import string

# 定义数据存储目录和文件
DATA_DIR = "./timetable_data"
TIMETABLES_FILE = os.path.join(DATA_DIR, "timetables.pkl")
METADATA_FILE = os.path.join(DATA_DIR, "metadata.json")
USERS_FILE = os.path.join(DATA_DIR, "users.json")
INVITE_CODES_FILE = os.path.join(DATA_DIR, "invite_codes.json")

def ensure_data_dir():
    """确保数据目录存在"""
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)

def init_timetable_session_state():
    """初始化课程表相关的session state"""
    ensure_data_dir()
    
    # 初始化session state
    if 'timetables' not in st.session_state:
        st.session_state.timetables = {}
    if 'uploaded_file_hashes' not in st.session_state:
        st.session_state.uploaded_file_hashes = set()
    if 'current_user' not in st.session_state:
        st.session_state.current_user = None
    if 'users' not in st.session_state:
        st.session_state.users = load_users()
    if 'delete_success' not in st.session_state:
        st.session_state.delete_success = False
    if 'timetables_to_delete' not in st.session_state:
        st.session_state.timetables_to_delete = []
    if 'force_refresh' not in st.session_state:
        st.session_state.force_refresh = False
    if 'last_upload_time' not in st.session_state:
        st.session_state.last_upload_time = None
    if 'invite_codes' not in st.session_state:
        st.session_state.invite_codes = load_invite_codes()
    
    # 从本地存储加载数据
    load_timetables_from_storage()

def load_invite_codes():
    """加载邀请码数据"""
    try:
        if os.path.exists(INVITE_CODES_FILE):
            with open(INVITE_CODES_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        else:
            # 初始化默认邀请码
            default_codes = {
                "ADMIN2024": {
                    "role": "admin",
                    "created_by": "system",
                    "created_at": datetime.datetime.now().isoformat(),
                    "used": False,
                    "used_by": None,
                    "used_at": None
                },
                "TEACHER123": {
                    "role": "admin", 
                    "created_by": "system",
                    "created_at": datetime.datetime.now().isoformat(),
                    "used": False,
                    "used_by": None,
                    "used_at": None
                }
            }
            save_invite_codes(default_codes)
            return default_codes
    except Exception as e:
        st.error(f"加载邀请码数据失败: {str(e)}")
        return {}

def save_invite_codes(invite_codes_data=None):
    """保存邀请码数据"""
    try:
        if invite_codes_data is None:
            invite_codes_data = st.session_state.invite_codes
        
        with open(INVITE_CODES_FILE, 'w', encoding='utf-8') as f:
            json.dump(invite_codes_data, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        st.error(f"保存邀请码数据失败: {str(e)}")
        return False

def load_users():
    """加载用户数据"""
    try:
        if os.path.exists(USERS_FILE):
            with open(USERS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        else:
            return {}
    except Exception as e:
        st.error(f"加载用户数据失败: {str(e)}")
        return {}

def save_users(users_data=None):
    """保存用户数据"""
    try:
        if users_data is None:
            users_data = st.session_state.users
        
        with open(USERS_FILE, 'w', encoding='utf-8') as f:
            json.dump(users_data, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        st.error(f"保存用户数据失败: {str(e)}")
        return False

def enhanced_user_system():
    """增强的用户系统"""
    st.sidebar.markdown("---")
    st.sidebar.subheader("🔐 用户登录")
    
    if st.session_state.current_user:
        user_info = st.session_state.users.get(st.session_state.current_user, {})
        user_role = user_info.get("role", "user")
        role_display = "👑 管理员" if user_role == "admin" else "👤 普通用户"
        st.sidebar.success(f"已登录: {st.session_state.current_user} ({role_display})")
        
        if st.sidebar.button("🚪 退出登录"):
            st.session_state.current_user = None
            st.rerun()
        return True
    
    with st.sidebar.expander("点击登录/注册", expanded=False):
        tab1, tab2 = st.tabs(["登录", "注册"])
        
        with tab1:
            username = st.text_input("用户名", key="login_username")
            password = st.text_input("密码", type="password", key="login_password")
            
            if st.button("登录", key="login_btn"):
                if authenticate_user(username, password):
                    st.session_state.current_user = username
                    st.success("登录成功!")
                    st.rerun()
                else:
                    st.error("用户名或密码错误")
        
        with tab2:
            new_username = st.text_input("新用户名", key="reg_username")
            new_password = st.text_input("新密码", type="password", key="reg_password")
            invite_code = st.text_input("管理员邀请码（可选）", key="invite_code")
            
            if st.button("注册", key="register_btn"):
                success, message = register_enhanced_user(new_username, new_password, invite_code)
                if success:
                    st.session_state.current_user = new_username
                    st.success(message)
                    st.rerun()
                else:
                    st.error(message)
    
    return False

def authenticate_user(username, password):
    """用户认证"""
    if username in st.session_state.users:
        stored_password = st.session_state.users[username].get("password")
        return stored_password == password
    return False

def register_enhanced_user(username, password, invite_code=None):
    """增强的用户注册"""
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
        "created_at": datetime.datetime.now().isoformat(),
        "invite_used": invite_code if invite_code else None
    }
    
    save_users()
    return True, message

def check_invite_code(code):
    """检查邀请码有效性"""
    # 检查邀请码是否存在且未被使用
    if code in st.session_state.invite_codes:
        invite_info = st.session_state.invite_codes[code]
        return not invite_info.get("used", False)
    return False

def mark_invite_code_used(code, username):
    """标记邀请码为已使用"""
    if code in st.session_state.invite_codes:
        st.session_state.invite_codes[code]["used"] = True
        st.session_state.invite_codes[code]["used_by"] = username
        st.session_state.invite_codes[code]["used_at"] = datetime.datetime.now().isoformat()
        save_invite_codes()
        return True
    return False

def generate_invite_code(role="admin", prefix="", length=8):
    """生成新的邀请码"""
    # 生成随机字符串
    characters = string.ascii_uppercase + string.digits
    random_part = ''.join(random.choice(characters) for _ in range(length))
    
    # 组合前缀和随机部分
    code = f"{prefix}{random_part}"
    
    # 确保邀请码唯一
    while code in st.session_state.invite_codes:
        random_part = ''.join(random.choice(characters) for _ in range(length))
        code = f"{prefix}{random_part}"
    
    # 保存邀请码
    st.session_state.invite_codes[code] = {
        "role": role,
        "created_by": st.session_state.current_user,
        "created_at": datetime.datetime.now().isoformat(),
        "used": False,
        "used_by": None,
        "used_at": None
    }
    
    save_invite_codes()
    return code

def save_timetables_to_storage():
    """将课表数据保存到本地存储"""
    try:
        # 保存课表数据
        with open(TIMETABLES_FILE, 'wb') as f:
            # 使用pickle保存DataFrame数据
            pickle.dump(st.session_state.timetables, f)
        
        # 保存元数据（文件哈希值）
        metadata = {
            'uploaded_file_hashes': list(st.session_state.uploaded_file_hashes),
            'last_saved': datetime.datetime.now().isoformat()
        }
        with open(METADATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, ensure_ascii=False, indent=2)
        
        return True
    except Exception as e:
        st.error(f"保存数据时出错: {str(e)}")
        return False

def load_timetables_from_storage():
    """从本地存储加载课表数据"""
    try:
        # 加载课表数据
        if os.path.exists(TIMETABLES_FILE):
            with open(TIMETABLES_FILE, 'rb') as f:
                loaded_timetables = pickle.load(f)
                # 清空当前数据，用加载的数据替换
                st.session_state.timetables.clear()
                st.session_state.timetables.update(loaded_timetables)
        
        # 加载元数据
        if os.path.exists(METADATA_FILE):
            with open(METADATA_FILE, 'r', encoding='utf-8') as f:
                metadata = json.load(f)
                st.session_state.uploaded_file_hashes.update(metadata.get('uploaded_file_hashes', []))
        
        return True
    except Exception as e:
        st.warning(f"加载保存的数据时遇到问题: {str(e)}")
        return False

def get_file_hash(file):
    """生成文件的哈希值用于唯一标识"""
    return hashlib.md5(file.getvalue()).hexdigest()

def validate_excel_file(file):
    """验证文件是否为Excel格式"""
    valid_extensions = ('.xlsx', '.xls')
    return any(file.name.lower().endswith(ext) for ext in valid_extensions)

def read_excel_file(file):
    """读取Excel文件，自动选择引擎"""
    try:
        # 根据文件扩展名选择引擎
        if file.name.lower().endswith('.xlsx'):
            df = pd.read_excel(file, engine='openpyxl')
        elif file.name.lower().endswith('.xls'):
            try:
                df = pd.read_excel(file, engine='xlrd')
            except ImportError:
                return None, "读取.xls文件需要安装xlrd库，请运行: pip install xlrd"
        else:
            return None, "不支持的文件格式"
        return df, None
    except Exception as e:
        return None, f"读取文件时出错: {str(e)}"

def save_timetable(file, df, timetable_name):
    """保存课表到session state和本地存储"""
    # 确保timetable_name是唯一的
    if timetable_name in st.session_state.timetables:
        # 如果名称已存在，添加时间戳和用户名
        timestamp = datetime.datetime.now().strftime("%H%M%S")
        user_suffix = f"_{st.session_state.current_user}" if st.session_state.current_user else ""
        timetable_name = f"{timetable_name}{user_suffix}_{timestamp}"
    elif st.session_state.current_user:
        # 添加用户标识
        timetable_name = f"{timetable_name}_{st.session_state.current_user}"
    
    st.session_state.timetables[timetable_name] = {
        'file_name': file.name,
        'dataframe': df,
        'upload_time': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        'uploaded_by': st.session_state.current_user or "匿名用户"
    }
    
    # 记录文件哈希值，避免重复上传
    file_hash = get_file_hash(file)
    st.session_state.uploaded_file_hashes.add(file_hash)
    
    # 保存到本地存储
    save_timetables_to_storage()
    
    # 设置强制刷新标志
    st.session_state.force_refresh = True
    st.session_state.last_upload_time = datetime.datetime.now()
    
    return timetable_name

def delete_timetable(timetable_name):
    """删除指定的课表"""
    if timetable_name in st.session_state.timetables:
        # 检查权限：只有上传者或管理员可以删除
        current_user = st.session_state.current_user
        uploader = st.session_state.timetables[timetable_name].get('uploaded_by')
        
        # 获取当前用户的角色
        current_user_role = "user"
        if current_user and current_user in st.session_state.users:
            current_user_role = st.session_state.users[current_user].get("role", "user")
        
        # 检查删除权限：管理员或上传者本人
        if current_user_role == 'admin' or current_user == uploader:
            del st.session_state.timetables[timetable_name]
            # 更新本地存储
            save_timetables_to_storage()
            st.session_state.delete_success = True
            st.session_state.force_refresh = True
            return True, f"成功删除课表: {timetable_name}"
        else:
            return False, "您只能删除自己上传的课表"
    return False, "课表不存在"

def clear_all_timetables():
    """清空所有课表（仅管理员）"""
    current_user = st.session_state.current_user
    if current_user and current_user in st.session_state.users:
        current_user_role = st.session_state.users[current_user].get("role", "user")
        if current_user_role == 'admin':
            st.session_state.timetables = {}
            st.session_state.uploaded_file_hashes = set()
            # 更新本地存储
            save_timetables_to_storage()
            st.session_state.delete_success = True
            st.session_state.force_refresh = True
            return True, "已清空所有课表"
    
    return False, "只有管理员可以清空所有课表"

def create_download_button(df, file_name, context=""):
    """创建下载按钮 - 动态生成唯一key"""
    output = BytesIO()
    
    # 统一使用.xlsx格式下载，避免依赖问题
    download_name = file_name.rsplit('.', 1)[0] + '.xlsx'
    
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='课程表')
    
    processed_data = output.getvalue()
    
    # 动态生成唯一key，包含上下文信息避免重复
    button_key = f"download_{context}_{uuid.uuid4().hex[:8]}"
    
    st.download_button(
        label=f"📥 下载 {download_name}",
        data=processed_data,
        file_name=download_name,
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        key=button_key
    )

def display_timetable_main():
    """在主界面显示课程表"""
    st.header("📅 课程表总览")
    
    # 检查删除成功状态
    if st.session_state.delete_success:
        st.success("删除操作成功完成！")
        st.session_state.delete_success = False
    
    if not st.session_state.timetables:
        st.info("📚 暂无课程表数据，请在导入页面上传课程表文件")
        return
    
    # 显示存储状态信息
    storage_info = get_storage_info()
    st.sidebar.info(f"💾 本地存储: {storage_info}")
    
    # 显示所有课表的概览
    timetable_names = list(st.session_state.timetables.keys())
    
    # 添加筛选选项
    col1, col2 = st.columns([3, 1])
    with col2:
        filter_option = st.selectbox(
            "筛选显示:",
            ["所有课表", "我上传的课表", "其他用户课表"]
        )
    
    # 根据筛选条件过滤课表
    if filter_option == "我上传的课表" and st.session_state.current_user:
        timetable_names = [name for name in timetable_names 
                          if st.session_state.timetables[name].get('uploaded_by') == st.session_state.current_user]
    elif filter_option == "其他用户课表" and st.session_state.current_user:
        timetable_names = [name for name in timetable_names 
                          if st.session_state.timetables[name].get('uploaded_by') != st.session_state.current_user]
    
    if not timetable_names:
        st.info("没有找到符合条件的课表")
        return
    
    # 创建选项卡显示不同的课表
    tabs = st.tabs([f"📋 {name}" for name in timetable_names])
    
    for i, (tab, timetable_name) in enumerate(zip(tabs, timetable_names)):
        with tab:
            timetable_data = st.session_state.timetables[timetable_name]
            df = timetable_data['dataframe']
            
            # 课表信息
            col1, col2 = st.columns([3, 1])
            with col1:
                st.subheader(timetable_name)
                uploader_info = f" | 上传者: {timetable_data.get('uploaded_by', '未知')}" if timetable_data.get('uploaded_by') else ""
                st.caption(f"文件: {timetable_data['file_name']} | 上传时间: {timetable_data['upload_time']}{uploader_info}")
            
            with col2:
                create_download_button(df, timetable_data['file_name'], f"main_{timetable_name}_{i}")
            
            # 显示完整课表数据
            st.dataframe(df, use_container_width=True, height=400)
            
            # 统计信息
            with st.expander("📊 统计信息"):
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("总行数", len(df))
                with col2:
                    st.metric("总列数", len(df.columns))
                with col3:
                    st.metric("数据量", f"{df.size}")
                with col4:
                    # 计算文本列和数值列的数量
                    text_cols = len(df.select_dtypes(include=['object']).columns)
                    num_cols = len(df.select_dtypes(include=['number']).columns)
                    st.metric("数据类型", f"{text_cols}文本/{num_cols}数值")

def get_storage_info():
    """获取存储信息"""
    try:
        if os.path.exists(TIMETABLES_FILE):
            file_size = os.path.getsize(TIMETABLES_FILE)
            file_size_kb = file_size / 1024
            user_count = len(set(data.get('uploaded_by', '未知') for data in st.session_state.timetables.values()))
            return f"{len(st.session_state.timetables)}个课表, {user_count}个用户 ({file_size_kb:.1f}KB)"
        else:
            return "未初始化"
    except:
        return "未知"

def import_timetable_section():
    """导入课程表功能部分"""
    st.header("📤 导入课程表")
    
    # 检查登录状态
    if not st.session_state.current_user:
        st.warning("请先登录以上传课表")
        return
    
    # 依赖检查
    try:
        import xlrd
        st.sidebar.success("✅ 支持.xls和.xlsx格式")
    except ImportError:
        st.sidebar.warning("⚠️ 仅支持.xlsx格式 (安装xlrd后可支持.xls)")
    
    with st.expander("💡 使用说明", expanded=True):
        st.markdown("""
        ### 导入说明：
        - **支持格式**: Excel文件 (.xlsx, .xls)
        - **依赖要求**: 
          - .xlsx格式: 已支持 ✅
          - .xls格式: 需要安装xlrd库 ⚠️
        - 可以同时导入多个课程表
        - 导入后可以在主页面查看课程表
        - **数据持久化**: 课表数据会自动保存，下次打开页面时自动加载
        - **多用户支持**: 所有用户上传的课表都会共享显示
        """)
    
    # 文件上传
    uploaded_files = st.file_uploader(
        "选择Excel课程表文件",
        type=['xlsx', 'xls'],
        accept_multiple_files=True,
        help="支持 .xlsx 和 .xls 格式的Excel文件",
        key="file_uploader"
    )
    
    # 处理上传的文件
    if uploaded_files:
        success_count = 0
        for file in uploaded_files:
            # 检查文件是否已经上传过
            file_hash = get_file_hash(file)
            if file_hash in st.session_state.uploaded_file_hashes:
                st.info(f"ℹ️ 文件 {file.name} 已经上传过了，跳过")
                continue
                
            if validate_excel_file(file):
                try:
                    # 检查.xls文件的依赖
                    if file.name.lower().endswith('.xls'):
                        try:
                            import xlrd
                        except ImportError:
                            st.error(f"❌ 无法读取 {file.name}: 需要安装xlrd库。请运行: pip install xlrd")
                            continue
                    
                    # 读取Excel文件
                    df, error = read_excel_file(file)
                    
                    if error:
                        st.error(f"❌ 读取文件 {file.name} 时出错: {error}")
                        continue
                    
                    if df is None or df.empty:
                        st.warning(f"⚠️ 文件 {file.name} 为空文件或读取失败")
                        continue
                    
                    # 生成课表名称
                    timetable_name = file.name.rsplit('.', 1)[0]
                    
                    # 保存课表
                    timetable_name = save_timetable(file, df, timetable_name)
                    success_count += 1
                    
                    st.success(f"✅ 成功导入: {file.name}")
                    
                    # 显示简要预览
                    with st.expander(f"预览: {file.name}", expanded=False):
                        st.write(f"数据维度: {df.shape[0]} 行 × {df.shape[1]} 列")
                        st.dataframe(df.head(5), use_container_width=True)
                    
                except Exception as e:
                    st.error(f"❌ 处理文件 {file.name} 时出错: {str(e)}")
            else:
                st.error(f"❌ 文件 {file.name} 不是有效的Excel格式")
        
        if success_count > 0:
            st.balloons()
            st.success(f"🎉 成功导入 {success_count} 个课程表！")
            
            # 显示存储状态
            storage_info = get_storage_info()
            st.info(f"💾 课表数据已保存: {storage_info}")
            
            # 立即刷新页面
            st.rerun()
        else:
            st.info("没有新文件需要导入")

def download_timetable_section():
    """下载课程表功能部分"""
    st.header("📥 下载课程表")
    
    if not st.session_state.timetables:
        st.warning("⚠️ 还没有导入任何课程表")
        return
    
    st.subheader("选择下载方式")
    
    # 单个下载
    st.markdown("#### 单个下载")
    timetable_names = list(st.session_state.timetables.keys())
    
    for i, timetable_name in enumerate(timetable_names):
        timetable_data = st.session_state.timetables[timetable_name]
        
        create_download_button(
            timetable_data['dataframe'], 
            timetable_data['file_name'],
            f"download_page_{timetable_name}_{i}"
        )
    
    # 批量下载 - 修复版本
    st.markdown("#### 批量下载")
    if len(timetable_names) > 1:
        # 直接创建打包文件，不使用中间按钮
        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            for idx, timetable_name in enumerate(timetable_names):
                df = st.session_state.timetables[timetable_name]['dataframe']
                # 创建唯一的sheet名称
                sheet_name = f"{timetable_name[:28]}_{idx+1}"  # 限制长度并添加序号
                df.to_excel(writer, index=False, sheet_name=sheet_name)
        
        processed_data = output.getvalue()
        
        # 直接提供下载按钮
        st.download_button(
            label="📦 打包下载所有课表",
            data=processed_data,
            file_name=f"课程表合集_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True,
            key=f"batch_download_{uuid.uuid4().hex[:8]}"
        )
    else:
        st.info("导入多个课表后可进行打包下载")

def enhanced_user_management_section():
    """增强的用户管理部分"""
    # 检查当前用户是否为管理员
    if not st.session_state.current_user:
        return
        
    current_user_info = st.session_state.users.get(st.session_state.current_user, {})
    if current_user_info.get("role") != "admin":
        return
    
    st.header("👑 管理员面板")
    
    # 用户统计
    total_users = len(st.session_state.users)
    admin_users = [u for u, info in st.session_state.users.items() if info.get('role') == 'admin']
    admin_count = len(admin_users)
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("总用户数", total_users)
    with col2:
        st.metric("管理员数", admin_count)
    with col3:
        st.metric("普通用户数", total_users - admin_count)
    
    # 用户管理
    st.subheader("用户管理")
    for username, user_info in st.session_state.users.items():
        with st.expander(f"{username} - {user_info.get('role', 'user')}", expanded=False):
            col1, col2 = st.columns([3, 1])
            
            with col1:
                st.write(f"注册时间: {user_info.get('created_at', '未知')}")
                if user_info.get('invite_used'):
                    st.write(f"使用的邀请码: {user_info.get('invite_used')}")
                
                # 角色管理
                current_role = user_info.get('role', 'user')
                if current_role == 'admin':
                    st.success("👑 管理员")
                    if username != st.session_state.current_user:  # 不能降级自己
                        if st.button(f"降级为普通用户", key=f"demote_{username}"):
                            user_info['role'] = 'user'
                            save_users()
                            st.success(f"已降级用户: {username}")
                            st.rerun()
                else:
                    st.info("👤 普通用户")
                    if st.button(f"提升为管理员", key=f"promote_{username}"):
                        user_info['role'] = 'admin'
                        save_users()
                        st.success(f"已提升用户: {username} 为管理员")
                        st.rerun()
            
            with col2:
                # 删除用户（不能删除自己）
                if username != st.session_state.current_user:
                    if st.button("🗑️ 删除", key=f"delete_{username}"):
                        del st.session_state.users[username]
                        save_users()
                        st.success(f"已删除用户: {username}")
                        st.rerun()
                else:
                    st.write("当前用户")
    
    # 邀请码管理
    st.subheader("邀请码管理")
    
    # 显示当前有效邀请码
    st.markdown("#### 当前有效邀请码")
    active_codes = {code: info for code, info in st.session_state.invite_codes.items() if not info.get("used", False)}
    
    if active_codes:
        for code, info in active_codes.items():
            col1, col2, col3 = st.columns([3, 1, 1])
            with col1:
                role_display = "👑 管理员" if info.get("role") == "admin" else "👤 普通用户"
                st.write(f"**{code}** - {role_display}")
                st.caption(f"创建者: {info.get('created_by', '未知')} | 创建时间: {info.get('created_at', '未知')}")
            with col2:
                if st.button("复制", key=f"copy_{code}"):
                    st.session_state.clipboard = code
                    st.success(f"已复制邀请码: {code}")
            with col3:
                if st.button("删除", key=f"delete_code_{code}"):
                    del st.session_state.invite_codes[code]
                    save_invite_codes()
                    st.success(f"已删除邀请码: {code}")
                    st.rerun()
    else:
        st.info("暂无有效邀请码")
    
    # 生成新邀请码
    st.markdown("#### 生成新邀请码")
    col1, col2, col3 = st.columns([2, 2, 1])
    
    with col1:
        new_code_role = st.selectbox("权限级别", ["admin", "user"], key="new_code_role")
    with col2:
        code_prefix = st.text_input("前缀(可选)", key="code_prefix", max_chars=10)
    with col3:
        code_length = st.number_input("长度", min_value=6, max_value=20, value=8, key="code_length")
    
    if st.button("🎫 生成新邀请码", use_container_width=True):
        new_code = generate_invite_code(
            role=new_code_role,
            prefix=code_prefix,
            length=code_length
        )
        st.success(f"🎉 新邀请码已生成: **{new_code}**")
        st.info(f"权限级别: {'👑 管理员' if new_code_role == 'admin' else '👤 普通用户'}")
        st.rerun()
    
    # 显示已使用的邀请码
    st.markdown("#### 已使用的邀请码")
    used_codes = {code: info for code, info in st.session_state.invite_codes.items() if info.get("used", False)}
    
    if used_codes:
        for code, info in used_codes.items():
            with st.expander(f"{code} - 已使用", expanded=False):
                st.write(f"使用者: {info.get('used_by', '未知')}")
                st.write(f"使用时间: {info.get('used_at', '未知')}")
                st.write(f"权限级别: {'👑 管理员' if info.get('role') == 'admin' else '👤 普通用户'}")
                st.write(f"创建者: {info.get('created_by', '未知')}")
    else:
        st.info("暂无已使用的邀请码")

def process_pending_deletions():
    """处理待删除的课表"""
    if st.session_state.timetables_to_delete:
        for timetable_name in st.session_state.timetables_to_delete:
            success, message = delete_timetable(timetable_name)
            if success:
                st.success(message)
            else:
                st.error(message)
        st.session_state.timetables_to_delete = []
        st.rerun()

def timetable_management_tab():
    """课程表管理标签页 - 供主程序调用"""
    # 初始化
    init_timetable_session_state()
    
    # 用户登录系统
    enhanced_user_system()
    
    # 处理待删除的课表
    process_pending_deletions()
    
    # 检查是否需要强制刷新
    if st.session_state.force_refresh:
        st.session_state.force_refresh = False
        st.rerun()
    
    # 创建子标签页
    tab_names = ["主页", "导入课程表", "下载课程表"]
    
    # 检查当前用户是否为管理员
    current_user_info = st.session_state.users.get(st.session_state.current_user, {})
    if current_user_info.get("role") == "admin":
        tab_names.append("管理员面板")
    
    tabs = st.tabs(tab_names)
    
    with tabs[0]:
        display_timetable_main()
    
    with tabs[1]:
        import_timetable_section()
    
    with tabs[2]:
        download_timetable_section()
    
    if len(tabs) > 3:
        with tabs[3]:
            enhanced_user_management_section()
    
    # 侧边栏信息 - 修复删除功能
    with st.sidebar:
        st.header("📚 课程表管理")
        
        # 显示存储信息
        storage_info = get_storage_info()
        st.info(f"💾 数据存储: {storage_info}")
        
        # 显示同步状态
        if st.session_state.current_user:
            user_info = st.session_state.users.get(st.session_state.current_user, {})
            user_role = user_info.get("role", "user")
            if user_role == "admin":
                st.success("👑 管理员权限")
        
        if st.session_state.timetables:
            st.subheader(f"已导入 ({len(st.session_state.timetables)})")
            
            # 使用列表来避免迭代时修改字典的问题
            timetable_items = list(st.session_state.timetables.items())
            
            # 添加单个删除功能
            for name, data in timetable_items:
                with st.expander(f"📋 {name}"):
                    st.caption(f"文件: {data['file_name']}")
                    st.caption(f"上传: {data['upload_time']}")
                    uploader_info = f" | 上传者: {data.get('uploaded_by', '未知')}" if data.get('uploaded_by') else ""
                    st.caption(f"数据: {len(data['dataframe'])}行 × {len(data['dataframe'].columns)}列{uploader_info}")
                    
                    # 检查删除权限 - 修复权限检查
                    current_user = st.session_state.current_user
                    can_delete = False
                    
                    if current_user:
                        # 管理员可以删除任何课表
                        user_info = st.session_state.users.get(current_user, {})
                        if user_info.get("role") == "admin":
                            can_delete = True
                        # 用户只能删除自己上传的课表
                        elif data.get('uploaded_by') == current_user:
                            can_delete = True
                    
                    if can_delete:
                        # 使用更简单的删除逻辑
                        delete_key = f"delete_{name}"
                        if st.button("🗑️ 删除此课表", key=delete_key, use_container_width=True):
                            success, message = delete_timetable(name)
                            if success:
                                st.success(message)
                                # 使用experimental_rerun确保刷新
                                st.rerun()
                            else:
                                st.error(message)
                    else:
                        st.caption("❌ 无删除权限")
            
            # 清空所有课表按钮（仅管理员）
            if st.session_state.current_user and st.session_state.users.get(st.session_state.current_user, {}).get("role") == 'admin':
                st.markdown("---")
                clear_button_key = f"clear_all_timetables"
                if st.button("🗑️ 清空所有课表", use_container_width=True, key=clear_button_key, type="secondary"):
                    success, message = clear_all_timetables()
                    if success:
                        st.success(message)
                        st.rerun()
                    else:
                        st.error(message)
        else:
            st.info("暂无课表数据")


def main():
    """主函数"""
    st.set_page_config(
        page_title="课程表管理系统",
        page_icon="📚",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # 初始化并运行课程表管理
    timetable_management_tab()

if __name__ == "__main__":
    main()