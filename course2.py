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
    if 'delete_success' not in st.session_state:
        st.session_state.delete_success = False
    if 'timetables_to_delete' not in st.session_state:
        st.session_state.timetables_to_delete = []
    if 'force_refresh' not in st.session_state:
        st.session_state.force_refresh = False
    if 'last_upload_time' not in st.session_state:
        st.session_state.last_upload_time = None
    
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

def display_timetable_main_modified(binded_users):
    """修改后的主界面显示课程表 - 只显示绑定用户的课表"""
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
    
    # 过滤课表：只显示当前用户和绑定用户的课表
    visible_timetables = {}
    for name, data in st.session_state.timetables.items():
        uploader = data.get('uploaded_by')
        if uploader == st.session_state.current_user or uploader in binded_users:
            visible_timetables[name] = data
    
    if not visible_timetables:
        st.info("📚 暂无可见的课程表数据，请先绑定账号或上传自己的课表")
        return
    
    # 显示所有课表的概览
    timetable_names = list(visible_timetables.keys())
    
    # 添加筛选选项
    col1, col2 = st.columns([3, 1])
    with col2:
        filter_option = st.selectbox(
            "筛选显示:",
            ["所有课表", "我上传的课表", "绑定用户课表"]
        )
    
    # 根据筛选条件过滤课表
    if filter_option == "我上传的课表" and st.session_state.current_user:
        timetable_names = [name for name in timetable_names 
                          if visible_timetables[name].get('uploaded_by') == st.session_state.current_user]
    elif filter_option == "绑定用户课表" and st.session_state.current_user:
        timetable_names = [name for name in timetable_names 
                          if visible_timetables[name].get('uploaded_by') != st.session_state.current_user]
    
    if not timetable_names:
        st.info("没有找到符合条件的课表")
        return
    
    # 创建选项卡显示不同的课表
    tabs = st.tabs([f"📋 {name}" for name in timetable_names])
    
    for i, (tab, timetable_name) in enumerate(zip(tabs, timetable_names)):
        with tab:
            timetable_data = visible_timetables[timetable_name]
            df = timetable_data['dataframe']
            
            # 课表信息
            col1, col2 = st.columns([3, 1])
            with col1:
                st.subheader(timetable_name)
                uploader = timetable_data.get('uploaded_by', '未知')
                if uploader == st.session_state.current_user:
                    uploader_info = " | 上传者: 👤 我"
                else:
                    uploader_info = f" | 上传者: 👥 {uploader}"
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
        - **账号绑定**: 只有绑定的用户才能查看彼此的课表
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
    
    # 批量下载
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

def timetable_management_tab_modified(binded_users):
    """修改后的课程表管理标签页 - 只显示绑定用户的课表"""
    # 初始化
    init_timetable_session_state()
    
    # 处理待删除的课表
    process_pending_deletions()
    
    # 检查是否需要强制刷新
    if st.session_state.force_refresh:
        st.session_state.force_refresh = False
        st.rerun()
    
    # 检查登录状态
    if not st.session_state.current_user:
        st.warning("请先登录以使用课表功能")
        return
    
    # 创建子标签页
    tab_names = ["主页", "导入课程表", "下载课程表"]
    
    tabs = st.tabs(tab_names)
    
    with tabs[0]:
        display_timetable_main_modified(binded_users)
    
    with tabs[1]:
        import_timetable_section()
    
    with tabs[2]:
        download_timetable_section()
    
    # 侧边栏信息
    with st.sidebar:
        st.header("📚 课程表管理")
        
        # 显示存储信息
        storage_info = get_storage_info()
        st.info(f"💾 数据存储: {storage_info}")
        
        # 显示绑定状态
        if st.session_state.current_user:
            if binded_users:
                st.success(f"🔗 已绑定 {len(binded_users)} 个用户")
            else:
                st.info("🔗 暂无绑定用户")
        
        visible_timetables = {}
        for name, data in st.session_state.timetables.items():
            uploader = data.get('uploaded_by')
            if uploader == st.session_state.current_user or uploader in binded_users:
                visible_timetables[name] = data
        
        if visible_timetables:
            st.subheader(f"可见课表 ({len(visible_timetables)})")
            
            # 使用列表来避免迭代时修改字典的问题
            timetable_items = list(visible_timetables.items())
            
            # 添加单个删除功能
            for name, data in timetable_items:
                with st.expander(f"📋 {name}"):
                    st.caption(f"文件: {data['file_name']}")
                    st.caption(f"上传: {data['upload_time']}")
                    uploader = data.get('uploaded_by', '未知')
                    if uploader == st.session_state.current_user:
                        uploader_info = " | 上传者: 👤 我"
                    else:
                        uploader_info = f" | 上传者: 👥 {uploader}"
                    st.caption(f"数据: {len(data['dataframe'])}行 × {len(data['dataframe'].columns)}列{uploader_info}")
                    
                    # 检查删除权限
                    can_delete = (
                        st.session_state.current_user and (
                            st.session_state.current_user == 'admin' or 
                            st.session_state.current_user == data.get('uploaded_by')
                        )
                    )
                    
                    if can_delete:
                        delete_key = f"delete_{name}"
                        if st.button("🗑️ 删除此课表", key=delete_key, use_container_width=True):
                            # 直接删除课表
                            success, message = delete_timetable(name)
                            if success:
                                st.success(message)
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
                    # 清空所有课表
                    success, message = clear_all_timetables()
                    if success:
                        st.success(message)
                        st.rerun()
                    else:
                        st.error(message)
        else:
            st.info("暂无可见课表数据")