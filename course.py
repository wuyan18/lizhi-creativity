# timetable_module.py
import streamlit as st
import pandas as pd
from io import BytesIO
import datetime
import uuid
import hashlib

def init_timetable_session_state():
    """初始化课程表相关的session state"""
    if 'timetables' not in st.session_state:
        st.session_state.timetables = {}
    if 'uploaded_file_hashes' not in st.session_state:
        st.session_state.uploaded_file_hashes = set()
    if 'delete_triggered' not in st.session_state:
        st.session_state.delete_triggered = False

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
            df = pd.read_excel(file, engine='xlrd')
        else:
            return None, "不支持的文件格式"
        return df, None
    except Exception as e:
        return None, f"读取文件时出错: {str(e)}"

def save_timetable(file, df, timetable_name):
    """保存课表到session state"""
    # 确保timetable_name是唯一的
    if timetable_name in st.session_state.timetables:
        # 如果名称已存在，添加时间戳
        timestamp = datetime.datetime.now().strftime("%H%M%S")
        timetable_name = f"{timetable_name}_{timestamp}"
    
    st.session_state.timetables[timetable_name] = {
        'file_name': file.name,
        'dataframe': df,
        'upload_time': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    
    # 记录文件哈希值，避免重复上传
    file_hash = get_file_hash(file)
    st.session_state.uploaded_file_hashes.add(file_hash)
    
    return timetable_name

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
    
    if not st.session_state.timetables:
        st.info("📚 暂无课程表数据，请在导入页面上传课程表文件")
        return
    
    # 显示所有课表的概览
    timetable_names = list(st.session_state.timetables.keys())
    
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
                st.caption(f"文件: {timetable_data['file_name']} | 上传时间: {timetable_data['upload_time']}")
            
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

def import_timetable_section():
    """导入课程表功能部分"""
    st.header("📤 导入课程表")
    
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
        """)
    
    # 文件上传 - 使用固定key避免重复创建
    uploaded_files = st.file_uploader(
        "选择Excel课程表文件",
        type=['xlsx', 'xls'],
        accept_multiple_files=True,
        help="支持 .xlsx 和 .xls 格式的Excel文件",
        key="file_uploader"  # 使用固定key
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
                    
                    if df.empty:
                        st.warning(f"⚠️ 文件 {file.name} 为空文件")
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
            st.success(f"🎉 成功导入 {success_count} 个课程表！请切换到'主页'查看课程表。")
            
            # 添加一个按钮直接跳转到主页
            if st.button("📋 立即查看课程表", key=f"view_timetable_{uuid.uuid4().hex[:8]}"):
                st.info("请手动切换到'主页'标签查看课程表")
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
        # 为批量下载按钮生成唯一key
        batch_button_key = f"batch_download_{uuid.uuid4().hex[:8]}"
        if st.button("📦 打包下载所有课表", use_container_width=True, key=batch_button_key):
            # 创建包含多个sheet的Excel文件
            output = BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                for timetable_name in timetable_names:
                    df = st.session_state.timetables[timetable_name]['dataframe']
                    # 截断sheet名称（Excel限制31字符）
                    sheet_name = timetable_name[:31]
                    df.to_excel(writer, index=False, sheet_name=sheet_name)
            
            processed_data = output.getvalue()
            
            # 为批量下载的下载按钮生成唯一key
            batch_download_key = f"batch_download_file_{uuid.uuid4().hex[:8]}"
            st.download_button(
                label="📦 下载打包文件",
                data=processed_data,
                file_name=f"课程表合集_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True,
                key=batch_download_key
            )
    else:
        st.info("导入多个课表后可进行打包下载")

def timetable_management_tab():
    """课程表管理标签页 - 供主程序调用"""
    # 初始化
    init_timetable_session_state()
    
    # 处理删除操作
    if st.session_state.delete_triggered:
        st.session_state.delete_triggered = False
        st.rerun()
    
    # 创建子标签页
    tab1, tab2, tab3 = st.tabs(["主页", "导入课程表", "下载课程表"])
    
    with tab1:
        display_timetable_main()
    
    with tab2:
        import_timetable_section()
    
    with tab3:
        download_timetable_section()
    
    # 侧边栏信息
    with st.sidebar:
        st.header("📚 课程表管理")
        
        if st.session_state.timetables:
            st.subheader(f"已导入 ({len(st.session_state.timetables)})")
            
            # 添加单个删除功能
            for name, data in st.session_state.timetables.items():
                with st.expander(f"📋 {name}"):
                    st.caption(f"文件: {data['file_name']}")
                    st.caption(f"上传: {data['upload_time']}")
                    st.caption(f"数据: {len(data['dataframe'])}行 × {len(data['dataframe'].columns)}列")
                    
                    # 单个删除按钮
                    delete_key = f"delete_{name}"
                    if st.button("🗑️ 删除此课表", key=delete_key, use_container_width=True):
                        # 删除特定课表
                        del st.session_state.timetables[name]
                        st.session_state.delete_triggered = True
                        st.success(f"已删除课表: {name}")
            
            # 清空所有课表按钮
            st.markdown("---")
            clear_button_key = "clear_all_timetables"
            if st.button("🗑️ 清空所有课表", use_container_width=True, key=clear_button_key, type="secondary"):
                # 清空所有课表
                st.session_state.timetables = {}
                st.session_state.uploaded_file_hashes = set()
                st.session_state.delete_triggered = True
                st.success("已清空所有课表")
        else:
            st.info("暂无课表数据")