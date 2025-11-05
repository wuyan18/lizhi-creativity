# schedule.py
import streamlit as st
import json
import os
from datetime import datetime

def load_schedule_data():
    """加载日程数据"""
    DATA_FILE = "saved_texts.json"
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return []
    return []

def save_schedule_data(data):
    """保存日程数据"""
    DATA_FILE = "saved_texts.json"
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def display_schedule_section(current_user, get_binded_users_func):
    """显示日程分享部分"""
    
    # 初始化数据
    if 'saved_texts' not in st.session_state:
        st.session_state.saved_texts = load_schedule_data()
    
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
    if not current_user:
        st.warning("请先登录以查看和分享日程")
        return
    
    # 获取绑定用户列表
    binded_users = get_binded_users_func()
    
    # 显示保存的文本 - 只显示当前用户和绑定用户的文本
    st.markdown("---")
    
    # 过滤文本：只显示当前用户和绑定用户的文本
    visible_texts = []
    for text in st.session_state.saved_texts:
        author = text.get('author', '未知')
        if author == current_user or author in binded_users:
            visible_texts.append(text)
    
    # 顶部统计卡片
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("总日程数", len(visible_texts))
    with col2:
        total_chars = sum(text['char_count'] for text in visible_texts)
        st.metric("总字符数", f"{total_chars:,}")
    with col3:
        unique_authors = len(set(text.get('author', '') for text in visible_texts))
        st.metric("共享用户", unique_authors)
    
    if not visible_texts:
        st.info("✨ 还没有导入过任何日程，请在下方输入并保存您的第一条日程。")
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
        
        # 显示过滤后的文本
        if not filtered_texts:
            st.warning("没有找到符合条件的文本")
        else:
            for i, text_entry in enumerate(filtered_texts):
                with st.container():
                    st.markdown('<div class="custom-card">', unsafe_allow_html=True)
                    
                    # 标题和元信息
                    col_title, col_meta = st.columns([3, 1])
                    with col_title:
                        st.markdown(f"**{text_entry['title']}**")
                    with col_meta:
                        author = text_entry.get('author', '未知')
                        if author == current_user:
                            st.caption("👤 我的日程")
                        else:
                            st.caption(f"👥 {author}")
                    
                    # 分类和标签
                    col_cat, col_tags = st.columns(2)
                    with col_cat:
                        if text_entry.get('category') != '未分类':
                            st.caption(f"📁 {text_entry.get('category', '未分类')}")
                    with col_tags:
                        if text_entry['tags']:
                            st.caption(f"🏷️ {', '.join(text_entry['tags'])}")
                    
                    # 文本内容
                    with st.expander("📝 查看日程内容", expanded=(i == 0)):
                        st.text_area(
                            "内容:",
                            value=text_entry['content'],
                            height=min(200, max(100, len(text_entry['content']) // 4)),
                            key=f"content_{text_entry['id']}",
                            disabled=True
                        )
                    
                    # 操作按钮
                    col1, col2, col3, col4 = st.columns([1, 1, 1, 2])
                    
                    with col1:
                        if st.button("📋 复制", key=f"copy_{text_entry['id']}"):
                            st.code(text_entry['content'], language="text")
                            st.success("内容已复制到代码块")
                    
                    # 只有作者本人可以编辑和删除
                    if text_entry.get('author') == current_user:
                        with col2:
                            if st.button("✏️ 编辑", key=f"edit_{text_entry['id']}"):
                                st.session_state.editing_id = text_entry['id']
                                st.rerun()
                        
                        with col3:
                            if st.button("🗑️ 删除", key=f"delete_{text_entry['id']}"):
                                st.session_state.saved_texts = [
                                    text for text in st.session_state.saved_texts 
                                    if text['id'] != text_entry['id']
                                ]
                                save_schedule_data(st.session_state.saved_texts)
                                st.success("日程已删除")
                                st.rerun()
                    else:
                        with col2:
                            st.button("🔒 锁定", key=f"lock_{text_entry['id']}", disabled=True)
                    
                    with col4:
                        st.caption(f"📅 {text_entry['created_at']} • {text_entry['char_count']} 字符")
                    
                    st.markdown('</div>', unsafe_allow_html=True)
            
            # 编辑功能
            if 'editing_id' in st.session_state:
                editing_id = st.session_state.editing_id
                text_to_edit = next((text for text in st.session_state.saved_texts if text['id'] == editing_id), None)
                
                if text_to_edit:
                    st.markdown('<div class="custom-card">', unsafe_allow_html=True)
                    st.subheader("✏️ 编辑日程")
                    
                    edited_title = st.text_input("标题:", value=text_to_edit['title'], key="edit_title_schedule")
                    edited_content = st.text_area("内容:", value=text_to_edit['content'], height=200, key="edit_content_schedule")
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button("💾 保存修改", key="save_edit_schedule", use_container_width=True):
                            text_to_edit['title'] = edited_title
                            text_to_edit['content'] = edited_content
                            text_to_edit['updated_at'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                            text_to_edit['char_count'] = len(edited_content)
                            
                            save_schedule_data(st.session_state.saved_texts)
                            del st.session_state.editing_id
                            st.success("修改已保存!")
                            st.rerun()
                    
                    with col2:
                        if st.button("❌ 取消编辑", key="cancel_edit_schedule", use_container_width=True):
                            del st.session_state.editing_id
                            st.rerun()
                    st.markdown('</div>', unsafe_allow_html=True)
    
    # 添加新日程
    st.markdown("---")
    st.subheader("✨ 添加新日程")
    
    st.markdown('<div class="custom-card">', unsafe_allow_html=True)
    
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
    
    # 保存按钮
    if st.button("💾 保存日程", use_container_width=True, key="save_schedule_btn"):
        if st.session_state.current_text.strip():
            # 创建文本条目
            text_entry = {
                'id': st.session_state.text_counter,
                'title': st.session_state.current_title if st.session_state.current_title else f"文本_{st.session_state.text_counter + 1}",
                'content': st.session_state.current_text,
                'tags': [tag.strip() for tag in tags.split(",")] if tags else [],
                'category': category,
                'author': current_user,
                'created_at': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                'updated_at': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                'char_count': len(st.session_state.current_text)
            }
            
            # 添加到保存的文本列表
            st.session_state.saved_texts.append(text_entry)
            st.session_state.text_counter += 1
            
            # 保存到文件
            save_schedule_data(st.session_state.saved_texts)
            
            # 清空当前输入
            st.session_state.current_text = ""
            st.session_state.current_title = f"文本_{st.session_state.text_counter + 1}"
            
            st.success("✅ 日程已保存!")
            st.rerun()
        else:
            st.warning("⚠️ 请输入日程内容")
    
    st.markdown('</div>', unsafe_allow_html=True)