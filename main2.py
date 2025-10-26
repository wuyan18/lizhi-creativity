import streamlit as st
import pandas as pd
import json
import os
import course


# 设置页面配置
st.set_page_config(
    page_title="荔枝营地 - 集体学习平台",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 自定义CSS样式 - 贯穿顶部的青色渐变
st.markdown("""
<style>
/* 贯穿顶部的标题栏 */
.full-width-header {
    background: linear-gradient(135deg, #20B2AA 0%, #48D1CC 50%, #40E0D0 100%);
    padding: 1.5rem 0;
    margin: -1rem -1rem 2rem -1rem;
    box-shadow: 0 4px 12px rgba(32, 178, 170, 0.3);
    border-bottom: 3px solid #008B8B;
}

/* 标题内容容器 */
.header-content {
    max-width: 1200px;
    margin: 0 auto;
    padding: 0 2rem;
}

/* 主标题样式 */
.main-title {
    font-size: 2.5rem;
    font-weight: 800;
    color: white;
    text-align: center;
    margin: 0;
    text-shadow: 1px 1px 3px rgba(0,0,0,0.3);
    letter-spacing: 1px;
}

/* 副标题样式 */
.sub-title {
    font-size: 1.2rem;
    color: rgba(255,255,255,0.95);
    text-align: center;
    margin: 0.5rem 0 0 0;
    font-weight: 400;
}

/* 导航标签样式 - 替换原来的功能标签 */
.nav-tabs {
    display: flex;
    justify-content: center;
    gap: 20px;
    margin-top: 15px;
}

.nav-tab {
    background: rgba(255, 255, 255, 0.2);
    padding: 8px 20px;
    border-radius: 25px;
    font-size: 1rem;
    color: white;
    border: 1px solid rgba(255, 255, 255, 0.3);
    cursor: pointer;
    transition: all 0.3s ease;
    text-decoration: none;
}

.nav-tab:hover {
    background: rgba(255, 255, 255, 0.3);
    transform: translateY(-2px);
}

.nav-tab.active {
    background: rgba(255, 255, 255, 0.4);
    font-weight: 600;
    box-shadow: 0 4px 8px rgba(0,0,0,0.2);
}
</style>
""", unsafe_allow_html=True)

# 初始化session state
if 'active_tab' not in st.session_state:
    st.session_state.active_tab = "网站介绍"

# 创建贯穿顶部的标题栏
st.markdown(f"""
<div class="full-width-header">
    <div class="header-content">
        <h1 class="main-title">🍈 荔枝营地</h1>
        <p class="sub-title">集体学习平台 • 日程与课表汇总</p>
    </div>
</div>
""", unsafe_allow_html=True)

# 创建三个按钮用于切换标签
col1, col2, col3 = st.columns(3)

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

# 页面内容从这里开始


# 根据选中的标签显示内容
if st.session_state.active_tab == "网站介绍":
    st.success("✨ 欢迎来到荔枝营地集体学习平台！")
    st.markdown("这是一个专为学生设计的学习和交流平台。")
    st.write("在这里，你可以找到志同道合的学习伙伴，分享学习资源，制定学习计划。无论你是想提高学业成绩，还是寻找合作伙伴完成项目，荔枝营地都是你的理想选择。")
    st.markdown("主要功能包括：")
    st.markdown("- **课程分享** ：与你的搭子一起共享课程信息，确保你们的信息共享吧！")
    st.markdown("- **日程安排** ：轻松管理你的学习和生活日程，确保你不会错过任何重要的事情。")

elif st.session_state.active_tab == "课表窗口":
    st.write("欢迎来到课表窗口，引入你的课表，来告诉ta你今天上什么课吧！")
    course.timetable_management_tab()
    
elif st.session_state.active_tab == "日程分享":
    st.write("这里是日程分享内容。")
    import os
    from datetime import datetime

    
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
    
    # 使用自定义的session state来存储当前文本，而不是绑定到widget
    if 'current_text' not in st.session_state:
        st.session_state.current_text = ""
    
    if 'current_title' not in st.session_state:
        st.session_state.current_title = f"文本_{st.session_state.text_counter + 1}"
    
    # 显示保存的文本
    st.markdown("---")
    st.subheader(f"共享日程 共 ({len(st.session_state.saved_texts)} 条)")
    
    if not st.session_state.saved_texts:
        st.info("还没有导入过任何日程，请在下方输入并保存您的第一条日程。")
    else:
        # 搜索和过滤功能
        st.subheader("🔍 搜索与筛选")
        col1, col2, col3 = st.columns([2, 1, 1])
        
        with col1:
            search_term = st.text_input("搜索文本内容:", placeholder="输入关键词搜索...", key="search")
        
        with col2:
            category_filter = st.selectbox(
                "分类筛选:",
                ["所有分类"] + list(set([text.get('category', '未分类') for text in st.session_state.saved_texts]))
            )
        
        with col3:
            sort_option = st.selectbox("排序方式:", ["最新优先", "最早优先", "标题A-Z", "标题Z-A"])
        
        # 过滤文本
        filtered_texts = st.session_state.saved_texts
        
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
                    col_title, col_category = st.columns([3, 1])
                    with col_title:
                        st.markdown(f"### {text_entry['title']}")
                    with col_category:
                        st.caption(f"📁 {text_entry.get('category', '未分类')}")
                    
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
                    
                    # 操作按钮
                    col_btn1, col_btn2, col_btn3 = st.columns(3)
                    with col_btn1:
                        if st.button(f"📋 复制", key=f"copy_{text_entry['id']}"):
                            st.code(text_entry['content'], language="text")
                            st.success("内容已复制到代码块")
                    
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
                    
                    st.markdown("---")
            
            # 编辑功能
            if 'editing_id' in st.session_state:
                editing_id = st.session_state.editing_id
                text_to_edit = next((text for text in st.session_state.saved_texts if text['id'] == editing_id), None)
                
                if text_to_edit:
                    st.subheader("✏️ 编辑文本")
                    
                    edited_title = st.text_input("标题:", value=text_to_edit['title'], key="edit_title")
                    edited_content = st.text_area("内容:", value=text_to_edit['content'], height=200, key="edit_content")
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button("💾 保存修改"):
                            text_to_edit['title'] = edited_title
                            text_to_edit['content'] = edited_content
                            text_to_edit['updated_at'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                            text_to_edit['char_count'] = len(edited_content)
                            
                            save_data(st.session_state.saved_texts)
                            del st.session_state.editing_id
                            st.success("修改已保存!")
                            st.rerun()
                    
                    with col2:
                        if st.button("❌ 取消编辑"):
                            del st.session_state.editing_id
                            st.rerun()
    
    # 文本输入区域 - 使用value参数绑定到自定义session state
    st.subheader("添加新文本")
    
    # 文本标题
    st.session_state.current_title = st.text_input(
        "文本标题:",
        placeholder="给这段文本起个名字",
        value=st.session_state.current_title
    )
    
    # 文本内容
    new_text = st.text_area(
        "输入您要保存的文本内容:",
        placeholder="在这里输入您的文本...",
        height=150,
        value=st.session_state.current_text
    )
    
    # 更新自定义session state
    st.session_state.current_text = new_text
    
    # 标签和分类
    col1, col2 = st.columns(2)
    with col1:
        tags = st.text_input(
            "标签 (可选):",
            placeholder="用逗号分隔标签，如：工作,重要,笔记"
        )
    with col2:
        category = st.selectbox(
            "分类:",
            ["未分类", "工作", "个人", "学习", "想法", "其他"]
        )
    
    # 保存和清空按钮
    col1, col2, col3 = st.columns([1, 1, 3])
    
    with col1:
        if st.button("💾 保存文本", use_container_width=True):
            if st.session_state.current_text.strip():
                # 创建文本条目
                text_entry = {
                    'id': st.session_state.text_counter,
                    'title': st.session_state.current_title if st.session_state.current_title else f"文本_{st.session_state.text_counter + 1}",
                    'content': st.session_state.current_text,
                    'tags': [tag.strip() for tag in tags.split(",")] if tags else [],
                    'category': category,
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
                
                st.success("✅ 文本已保存!")
                st.rerun()
            else:
                st.warning("⚠️ 请输入文本内容")
    
    
            
    
    