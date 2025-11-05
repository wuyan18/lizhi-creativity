# modern_styles.py
def get_modern_css():
    return """
    <style>
    /* 全局重置和基础样式 */
    .main {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        min-height: 100vh;
    }
    
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        background: rgba(255, 255, 255, 0.95);
        border-radius: 20px;
        margin-top: 1rem;
        box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
        backdrop-filter: blur(10px);
    }
    
    /* 标题样式 */
    .main-title {
        font-size: 3rem;
        font-weight: 800;
        background: linear-gradient(135deg, #FF6B6B, #4ECDC4, #45B7D1, #96CEB4, #FFEAA7);
        background-size: 400% 400%;
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        animation: gradient 8s ease infinite;
        text-align: center;
        margin-bottom: 0.5rem;
        font-family: 'Arial Rounded MT Bold', 'Arial', sans-serif;
    }
    
    @keyframes gradient {
        0% { background-position: 0% 50% }
        50% { background-position: 100% 50% }
        100% { background-position: 0% 50% }
    }
    
    .subtitle {
        text-align: center;
        color: #64748b;
        font-size: 1.2rem;
        margin-bottom: 2rem;
        font-weight: 300;
        letter-spacing: 1px;
    }
    
    /* 现代化标签页样式 */
    .stTabs [data-baseweb="tab-list"] {
        gap: 2px;
        background-color: #f8fafc;
        padding: 4px;
        border-radius: 15px;
        margin-bottom: 2rem;
    }
    
    .stTabs [data-baseweb="tab"] {
        height: 60px;
        background-color: transparent;
        border-radius: 12px;
        padding: 0 24px;
        font-weight: 600;
        font-size: 1rem;
        border: none;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        color: #64748b;
    }
    
    .stTabs [data-baseweb="tab"]:hover {
        background-color: rgba(99, 102, 241, 0.1);
        color: #6366f1;
        transform: translateY(-2px);
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #6366f1, #8b5cf6) !important;
        color: white !important;
        box-shadow: 0 8px 25px rgba(99, 102, 241, 0.3);
    }
    
    /* 现代化卡片设计 */
    .modern-card {
        background: white;
        padding: 2rem;
        border-radius: 20px;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.08);
        border: 1px solid rgba(255, 255, 255, 0.2);
        margin-bottom: 1.5rem;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        position: relative;
        overflow: hidden;
    }
    
    .modern-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 4px;
        background: linear-gradient(135deg, #6366f1, #8b5cf6);
    }
    
    .modern-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 20px 40px rgba(0, 0, 0, 0.15);
    }
    
    /* 功能卡片 */
    .feature-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 2rem;
        border-radius: 20px;
        margin: 1rem 0;
        position: relative;
        overflow: hidden;
        transition: all 0.3s ease;
    }
    
    .feature-card::before {
        content: '';
        position: absolute;
        top: -50%;
        left: -50%;
        width: 200%;
        height: 200%;
        background: linear-gradient(45deg, transparent, rgba(255,255,255,0.1), transparent);
        transform: rotate(45deg);
        transition: all 0.6s ease;
    }
    
    .feature-card:hover::before {
        transform: rotate(45deg) translate(50%, 50%);
    }
    
    .feature-card:hover {
        transform: translateY(-8px);
        box-shadow: 0 25px 50px rgba(102, 126, 234, 0.3);
    }
    
    /* 现代化按钮 */
    .stButton>button {
        border-radius: 15px;
        border: none;
        padding: 1rem 2rem;
        font-weight: 600;
        font-size: 1rem;
        background: linear-gradient(135deg, #6366f1, #8b5cf6);
        color: white;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        box-shadow: 0 4px 15px rgba(99, 102, 241, 0.3);
    }
    
    .stButton>button:hover {
        transform: translateY(-3px);
        box-shadow: 0 8px 25px rgba(99, 102, 241, 0.4);
        background: linear-gradient(135deg, #5a63d8, #7c4feb);
    }
    
    .stButton>button:active {
        transform: translateY(-1px);
    }
    
    /* 次要按钮 */
    .secondary-button {
        background: linear-gradient(135deg, #94a3b8, #64748b) !important;
    }
    
    /* 输入框样式 */
    .stTextInput>div>div>input {
        border-radius: 12px;
        border: 2px solid #e2e8f0;
        padding: 1rem;
        font-size: 1rem;
        transition: all 0.3s ease;
    }
    
    .stTextInput>div>div>input:focus {
        border-color: #6366f1;
        box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.1);
        transform: translateY(-2px);
    }
    
    /* 选择框样式 */
    .stSelectbox>div>div {
        border-radius: 12px;
        border: 2px solid #e2e8f0;
    }
    
    /* 文本区域样式 */
    .stTextArea>div>div>textarea {
        border-radius: 12px;
        border: 2px solid #e2e8f0;
        padding: 1rem;
    }
    
    /* 指标卡片 */
    .metric-card {
        background: linear-gradient(135deg, #f8fafc, #e2e8f0);
        padding: 1.5rem;
        border-radius: 15px;
        text-align: center;
        border-left: 4px solid #6366f1;
    }
    
    /* 用户状态卡片 */
    .user-status-card {
        background: linear-gradient(135deg, #6366f1, #8b5cf6);
        color: white;
        padding: 1.5rem;
        border-radius: 15px;
        text-align: center;
        box-shadow: 0 8px 25px rgba(99, 102, 241, 0.3);
    }
    
    /* 标签样式 */
    .tag {
        display: inline-block;
        background: linear-gradient(135deg, #4ade80, #22d3ee);
        color: white;
        padding: 0.25rem 0.75rem;
        border-radius: 20px;
        font-size: 0.875rem;
        font-weight: 500;
        margin: 0.25rem;
    }
    
    /* 响应式调整 */
    @media (max-width: 768px) {
        .main-title {
            font-size: 2rem;
        }
        
        .modern-card {
            padding: 1.5rem;
        }
        
        .stTabs [data-baseweb="tab"] {
            height: 50px;
            padding: 0 16px;
            font-size: 0.9rem;
        }
    }
    
    /* 自定义滚动条 */
    ::-webkit-scrollbar {
        width: 8px;
    }
    
    ::-webkit-scrollbar-track {
        background: #f1f5f9;
        border-radius: 10px;
    }
    
    ::-webkit-scrollbar-thumb {
        background: linear-gradient(135deg, #6366f1, #8b5cf6);
        border-radius: 10px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: linear-gradient(135deg, #5a63d8, #7c4feb);
    }
    
    /* 分割线样式 */
    .divider {
        height: 2px;
        background: linear-gradient(90deg, transparent, #6366f1, transparent);
        margin: 2rem 0;
        border: none;
    }
    
    /* 动画效果 */
    @keyframes fadeInUp {
        from {
            opacity: 0;
            transform: translateY(30px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    .fade-in-up {
        animation: fadeInUp 0.6s ease-out;
    }
    </style>
    """