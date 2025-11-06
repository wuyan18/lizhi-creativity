# main_modern.py
import streamlit as st
import course2
from modern_styles import get_modern_css
from auth import *
from schedule import display_schedule_section

# 设置页面配置
st.set_page_config(
    page_title="荔枝营地 - 集体学习平台",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 应用现代化样式
st.markdown(get_modern_css(), unsafe_allow_html=True)

# 初始化session state
if 'active_tab' not in st.session_state:
    st.session_state.active_tab = "网站介绍"
if 'show_login_modal' not in st.session_state:
    st.session_state.show_login_modal = False

# 初始化用户系统
if 'users' not in st.session_state:
    st.session_state.users = course2.load_users()
if 'current_user' not in st.session_state:
    st.session_state.current_user = None
if 'user_relationships' not in st.session_state:
    st.session_state.user_relationships = load_user_relationships()

def modern_login_system():
    """现代化登录系统"""
    # 顶部标题区域
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown('<div class="main-title">🍈 荔枝营地</div>', unsafe_allow_html=True)
        st.markdown('<div class="subtitle">集体学习平台 • 让学习更有趣</div>', unsafe_allow_html=True)
    
    with col3:
        if st.session_state.current_user:
            st.markdown(f'''
            <div class="user-status-card">
                <div style="font-size: 1.2rem; font-weight: 600;">👋 {st.session_state.current_user}</div>
                <div style="font-size: 0.9rem; opacity: 0.9;">
                    👤 学习者
                </div>
            </div>
            ''', unsafe_allow_html=True)
            
            if st.button("🚪 退出登录", key="logout_btn", use_container_width=True):
                st.session_state.current_user = None
                st.rerun()
        else:
            if st.button("🔐 登录 / 注册", key="login_btn", use_container_width=True, type="primary"):
                st.session_state.show_login_modal = True
                st.rerun()

def modern_login_modal():
    """简化版登录界面 - 不使用模态框"""
    if st.session_state.show_login_modal:
        # 创建一个居中的登录框
        st.markdown("""
        <style>
        .login-container {
            max-width: 500px;
            margin: 2rem auto;
            padding: 2rem;
            background: white;
            border-radius: 15px;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
        }
        </style>
        """, unsafe_allow_html=True)
        
        st.markdown('<div class="login-container">', unsafe_allow_html=True)
        
        st.markdown('<h2 style="text-align: center; margin-bottom: 1.5rem;">🔐 欢迎回来</h2>', unsafe_allow_html=True)
        
        tab1, tab2 = st.tabs(["登录账户", "注册账户"])
        
        with tab1:
            username = st.text_input("👤 用户名", key="modal_login_username", placeholder="请输入用户名")
            password = st.text_input("🔒 密码", type="password", key="modal_login_password", placeholder="请输入密码")
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("🚀 立即登录", use_container_width=True, key="login_submit"):
                    if authenticate_user(username, password, st.session_state.users):
                        st.session_state.current_user = username
                        st.session_state.show_login_modal = False
                        st.success("🎉 登录成功！")
                        st.rerun()
                    else:
                        st.error("❌ 用户名或密码错误")
            with col2:
                if st.button("❌ 关闭", use_container_width=True, key="login_cancel"):
                    st.session_state.show_login_modal = False
                    st.rerun()
        
        with tab2:
            new_username = st.text_input("👤 新用户名", key="modal_reg_username", placeholder="创建用户名")
            new_password = st.text_input("🔒 设置密码", type="password", key="modal_reg_password", placeholder="设置登录密码")
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("✨ 创建账户", use_container_width=True, key="reg_submit"):
                    success, message = register_user(new_username, new_password, st.session_state.users)
                    if success:
                        course2.save_users(st.session_state.users)
                        st.session_state.current_user = new_username
                        st.session_state.show_login_modal = False
                        st.success(f"🎉 {message}")
                        st.rerun()
                    else:
                        st.error(f"❌ {message}")
            with col2:
                if st.button("❌ 关闭", use_container_width=True, key="reg_cancel"):
                    st.session_state.show_login_modal = False
                    st.rerun()
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # 添加一个关闭按钮在容器外
        if st.button("← 返回首页", key="back_to_home"):
            st.session_state.show_login_modal = False
            st.rerun()

def modern_account_binding():
    """现代化账号绑定界面"""
    st.header("🔗 伙伴连接")
    
    if not st.session_state.current_user:
        st.warning("👋 请先登录以连接学习伙伴")
        return
    
    # 发送请求卡片
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div class="modern-card">
            <h3>📤 发送连接请求</h3>
            <p>输入伙伴的用户名，发送学习连接邀请</p>
        """, unsafe_allow_html=True)
        target_username = st.text_input("伙伴用户名:", key="bind_target", placeholder="输入用户名")
        if st.button("🚀 发送邀请", use_container_width=True, key="send_bind_request"):
            success, message = send_binding_request(target_username, st.session_state.current_user, st.session_state.user_relationships)
            if success:
                save_user_relationships(st.session_state.user_relationships)
                st.success(f"✅ {message}")
                st.rerun()
            else:
                st.error(f"❌ {message}")
        st.markdown("</div>", unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="modern-card">
            <h3>📥 待处理请求</h3>
        """, unsafe_allow_html=True)
        user_rels = st.session_state.user_relationships.get(st.session_state.current_user, {})
        received_requests = user_rels.get("received_requests", [])
        
        if received_requests:
            for req_user in received_requests:
                col_req1, col_req2 = st.columns([2, 1])
                with col_req1:
                    st.write(f"**{req_user}** 想要连接")
                with col_req2:
                    col_btn1, col_btn2 = st.columns(2)
                    with col_btn1:
                        if st.button("✅", key=f"accept_{req_user}", use_container_width=True):
                            success, message = accept_binding_request(req_user, st.session_state.current_user, st.session_state.user_relationships)
                            if success:
                                save_user_relationships(st.session_state.user_relationships)
                                st.success(f"✅ {message}")
                                st.rerun()
                    with col_btn2:
                        if st.button("❌", key=f"reject_{req_user}", use_container_width=True):
                            success, message = reject_binding_request(req_user, st.session_state.current_user, st.session_state.user_relationships)
                            if success:
                                save_user_relationships(st.session_state.user_relationships)
                                st.success(f"✅ {message}")
                                st.rerun()
        else:
            st.info("📭 暂无待处理请求")
        st.markdown("</div>", unsafe_allow_html=True)
    
    # 连接状态卡片
    col3, col4 = st.columns(2)
    
    with col3:
        st.markdown("""
        <div class="modern-card">
            <h3>🤝 已连接伙伴</h3>
        """, unsafe_allow_html=True)
        binded_users = get_binded_users(st.session_state.current_user, st.session_state.user_relationships)
        if binded_users:
            for binded_user in binded_users:
                col_user, col_action = st.columns([3, 1])
                with col_user:
                    st.success(f"👥 {binded_user}")
                with col_action:
                    # 添加解除绑定按钮
                    if st.button("🔓 解除", key=f"unbind_{binded_user}", use_container_width=True):
                        success, message = unbind_user(binded_user, st.session_state.current_user, st.session_state.user_relationships)
                        if success:
                            save_user_relationships(st.session_state.user_relationships)
                            st.success(f"✅ {message}")
                            st.rerun()
                        else:
                            st.error(f"❌ {message}")
        else:
            st.info("🔍 暂无连接伙伴")
        st.markdown("</div>", unsafe_allow_html=True)
    
    with col4:
        st.markdown("""
        <div class="modern-card">
            <h3>⏳ 已发送请求</h3>
        """, unsafe_allow_html=True)
        user_rels = st.session_state.user_relationships.get(st.session_state.current_user, {})
        sent_requests = user_rels.get("sent_requests", [])
        if sent_requests:
            for sent_user in sent_requests:
                col_sent, col_cancel = st.columns([3, 1])
                with col_sent:
                    st.info(f"📤 已向 {sent_user} 发送请求")
                with col_cancel:
                    # 添加取消请求按钮
                    if st.button("❌", key=f"cancel_{sent_user}", use_container_width=True):
                        # 取消请求实际上是拒绝自己发送的请求
                        success, message = reject_binding_request(sent_user, st.session_state.current_user, st.session_state.user_relationships)
                        if success:
                            save_user_relationships(st.session_state.user_relationships)
                            st.success(f"✅ {message}")
                            st.rerun()
                        else:
                            st.error(f"❌ {message}")
        else:
            st.info("📤 暂无已发送请求")
        st.markdown("</div>", unsafe_allow_html=True)
    
    # 批量解除绑定功能
    st.markdown("""
    <div class="modern-card">
        <h3>🔄 批量管理</h3>
        <p>快速解除所有绑定关系</p>
    """, unsafe_allow_html=True)
    
    if binded_users:
        st.warning("⚠️ 此操作将解除与所有伙伴的连接关系")
        if st.button("🗑️ 解除所有绑定", key="unbind_all", use_container_width=True, type="secondary"):
            # 解除所有绑定
            for binded_user in binded_users[:]:  # 使用副本进行迭代
                success, message = unbind_user(binded_user, st.session_state.current_user, st.session_state.user_relationships)
                if success:
                    st.success(f"✅ 已解除与 {binded_user} 的绑定")
                else:
                    st.error(f"❌ 解除 {binded_user} 绑定时出错: {message}")
            
            save_user_relationships(st.session_state.user_relationships)
            st.success("🎉 所有绑定关系已解除")
            st.rerun()
    else:
        st.info("暂无绑定关系可管理")
    
    st.markdown("</div>", unsafe_allow_html=True)

def modern_home_page():
    """现代化首页"""
    st.markdown("""
    <div class="modern-card">
        <h1>🎯 欢迎来到荔枝营地！</h1>
        <p style="font-size: 1.2rem; color: #64748b; margin-bottom: 2rem;">
        一个专为学习者打造的智能协作平台，让学习变得更简单、更有趣
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # 功能特性展示 - 使用统一高度的卡片
    st.subheader("✨ 平台特色")
    
    # 创建列并添加CSS类确保高度一致
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("""
        <div class="feature-card">
            <h3>🤝 智能连接</h3>
            <p>快速找到志同道合的学习伙伴，建立学习小组</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="feature-card">
            <h3>📅 日程同步</h3>
            <p>实时同步学习计划，避免时间冲突</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="feature-card">
            <h3>📚 课程管理</h3>
            <p>智能课表管理，学习进度一目了然</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown("""
        <div class="feature-card">
            <h3>🎯 进度追踪</h3>
            <p>可视化学习进度，激励持续进步</p>
        </div>
        """, unsafe_allow_html=True)
    
    # 使用指南
    st.markdown("""
    <div class="modern-card">
        <h2>🚀 快速开始</h2>
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 1.5rem; margin-top: 1.5rem;">
            <div style="text-align: center; padding: 1.5rem; background: #f8fafc; border-radius: 15px;">
                <div style="font-size: 2rem; margin-bottom: 1rem;">1️⃣</div>
                <h4>注册登录</h4>
                <p style="color: #64748b;">创建个人学习账户</p>
            </div>
            <div style="text-align: center; padding: 1.5rem; background: #f8fafc; border-radius: 15px;">
                <div style="font-size: 2rem; margin-bottom: 1rem;">2️⃣</div>
                <h4>连接伙伴</h4>
                <p style="color: #64748b;">添加学习小伙伴</p>
            </div>
            <div style="text-align: center; padding: 1.5rem; background: #f8fafc; border-radius: 15px;">
                <div style="font-size: 2rem; margin-bottom: 1rem;">3️⃣</div>
                <h4>设置计划</h4>
                <p style="color: #64748b;">上传课表和日程</p>
            </div>
            <div style="text-align: center; padding: 1.5rem; background: #f8fafc; border-radius: 15px;">
                <div style="font-size: 2rem; margin-bottom: 1rem;">4️⃣</div>
                <h4>开始学习</h4>
                <p style="color: #64748b;">协作共享信息</p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # 统计信息（如果已登录）
    if st.session_state.current_user:
        st.markdown("""
        <div class="modern-card">
            <h2>📊 学习统计</h2>
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 1rem; margin-top: 1rem;">
        """, unsafe_allow_html=True)
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("连接伙伴", "3", "+1")
        with col2:
            st.metric("学习日程", "12", "2 new")
        with col3:
            st.metric("在线时长", "36h", "+5h")
        with col4:
            st.metric("学习进度", "78%", "+5%")
        
        st.markdown("</div></div>", unsafe_allow_html=True)

def main():
    """主函数"""
    # 显示现代化登录系统
    modern_login_system()
    
    # 显示登录模态框（如果需要）
    modern_login_modal()
    
    # 使用Streamlit原生标签页
    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
    
    tab1, tab2, tab3, tab4 = st.tabs(["🎯 首页", "📅 学习日程", "📚 我的课表", "🤝 伙伴连接"])
    
    with tab1:
        modern_home_page()
    
    with tab2:
        st.header("📅 学习日程管理")
        st.write("规划你的学习时间，与伙伴同步进度")
        display_schedule_section(st.session_state.current_user, 
                               lambda: get_binded_users(st.session_state.current_user, st.session_state.user_relationships))
    
    with tab3:
        st.header("📚 智能课表")
        st.write("管理课程安排，智能提醒学习时间")
        
        if not st.session_state.current_user:
            st.warning("👋 请先登录以使用课表功能")
        else:
            try:
                import importlib
                importlib.reload(course2)
                
                binded_users = get_binded_users(st.session_state.current_user, st.session_state.user_relationships)
                course2.timetable_management_tab_modified(binded_users)
                
            except Exception as e:
                st.error(f"❌ 加载课表功能时出现错误: {str(e)}")
                st.info("💡 请检查控制台获取完整错误信息")
    
    with tab4:
        modern_account_binding()

# 运行主程序
if __name__ == "__main__":
    main()