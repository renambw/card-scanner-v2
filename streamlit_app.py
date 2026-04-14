"""
CardScan AI - 名片掃描系統（Streamlit 版本）
完全免費的 Web App，手動複製到 Google Sheets
無需 API 密鑰 - 永久免費！
"""

import streamlit as st
from PIL import Image
import json
from datetime import datetime
import base64
import io
import re
from PIL import ImageOps, ImageFilter, ImageEnhance

# 頁面配置
st.set_page_config(
    page_title="CardScan AI",
    page_icon="📇",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# 自定義樣式
st.markdown("""
<style>
    body {
        background-color: #f5f5f5;
    }
    .main {
        max-width: 600px;
        margin: 0 auto;
    }
    .stButton > button {
        width: 100%;
        padding: 15px;
        font-size: 16px;
        border-radius: 10px;
        background-color: #007AFF;
        color: white;
        border: none;
        cursor: pointer;
    }
    .stButton > button:hover {
        background-color: #0051D5;
    }
    .success-box {
        background-color: #D4EDDA;
        border: 1px solid #C3E6CB;
        color: #155724;
        padding: 15px;
        border-radius: 5px;
        margin: 10px 0;
    }
    .error-box {
        background-color: #F8D7DA;
        border: 1px solid #F5C6CB;
        color: #721C24;
        padding: 15px;
        border-radius: 5px;
        margin: 10px 0;
    }
    .info-box {
        background-color: #D1ECF1;
        border: 1px solid #BEE5EB;
        color: #0C5460;
        padding: 15px;
        border-radius: 5px;
        margin: 10px 0;
    }
    .sheet-guide {
        background-color: #E7F3FF;
        border: 1px solid #B3D9FF;
        color: #004085;
        padding: 15px;
        border-radius: 5px;
        margin: 10px 0;
        font-size: 14px;
    }
    .guide-step {
        background-color: #FFF3CD;
        border-left: 4px solid #FFC107;
        padding: 12px;
        margin: 10px 0;
        border-radius: 3px;
    }
</style>
""", unsafe_allow_html=True)

# 初始化 session state
if "card_data" not in st.session_state:
    st.session_state.card_data = {
        "company": "",
        "name": "",
        "jobTitle": "",
        "phone": "",
        "email": "",
        "address": "",
        "notes": ""
    }
if "image_data" not in st.session_state:
    st.session_state.image_data = None
if "scan_count" not in st.session_state:
    st.session_state.scan_count = 0

# 標題
st.title("📇 CardScan AI")
st.markdown("### 智能名片掃描系統")
st.markdown("手動輸入名片信息 | 複製到 Google Sheets | 完全免費 🆓")

# 側邊欄設定
with st.sidebar:
    st.header("⚙️ 設定")
    
    st.markdown("### 📊 使用統計")
    st.markdown(f"""
    - 掃描次數: {st.session_state.get('scan_count', 0)}
    - 上次掃描: {st.session_state.get('last_scan', '未掃描')}
    """)
    
    st.markdown("---")
    st.markdown("### 📚 使用指南")
    st.markdown("""
    **方案 E：手動複製到 Google Sheets**
    
    1️⃣ 上傳名片照片
    2️⃣ 手動輸入名片信息
    3️⃣ 複製 TSV 或 JSON 格式
    4️⃣ 粘貼到 Google Sheet
    5️⃣ ✅ 完成！
    
    **優點：**
    - ✅ 完全免費
    - ✅ 無需 API 密鑰
    - ✅ 永久可用
    - ✅ 完全隱私
    """)

# 主要內容
st.markdown("---")

# 標籤頁
tab1, tab2, tab3 = st.tabs(["📸 上傳", "📋 編輯", "💾 複製到 Sheet"])

# 標籤 1: 上傳
with tab1:
    st.markdown("### 📸 上傳名片照片")
    
    # 上傳圖片
    uploaded_file = st.file_uploader(
        "選擇名片圖片",
        type=["jpg", "jpeg", "png", "webp"],
        help="支持 JPG、PNG、WebP 格式"
    )
    
    if uploaded_file is not None:
        # 打開圖片
        image = Image.open(uploaded_file)
        
        # 顯示圖片
        st.image(image, caption="上傳的名片", use_column_width=True)
        
        # 保存圖片數據
        image_bytes = io.BytesIO()
        image.save(image_bytes, format="JPEG")
        image_bytes.seek(0)
        st.session_state.image_data = base64.b64encode(image_bytes.getvalue()).decode()
        
        st.markdown("""
        <div class="guide-step">
        <strong>✅ 圖片已上傳！</strong><br>
        現在請進入「📋 編輯」標籤，手動輸入名片信息。
        </div>
        """, unsafe_allow_html=True)

# 標籤 2: 編輯
with tab2:
    st.markdown("### 📋 輸入名片信息")
    
    st.markdown("""
    <div class="info-box">
    <strong>📝 請手動輸入名片上的信息</strong><br>
    根據上傳的名片照片，填寫以下欄位。
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**公司 (Company)**")
        company = st.text_input(
            "Company",
            value=st.session_state.card_data.get("company", ""),
            label_visibility="collapsed",
            placeholder="例如：Google"
        )
        st.session_state.card_data["company"] = company
        
        st.markdown("**姓名 (Name)**")
        name = st.text_input(
            "Name",
            value=st.session_state.card_data.get("name", ""),
            label_visibility="collapsed",
            placeholder="例如：張三"
        )
        st.session_state.card_data["name"] = name
        
        st.markdown("**職稱 (Job Title)**")
        job_title = st.text_input(
            "Job Title",
            value=st.session_state.card_data.get("jobTitle", ""),
            label_visibility="collapsed",
            placeholder="例如：工程師"
        )
        st.session_state.card_data["jobTitle"] = job_title
        
        st.markdown("**電話 (Phone)**")
        phone = st.text_input(
            "Phone",
            value=st.session_state.card_data.get("phone", ""),
            label_visibility="collapsed",
            placeholder="例如：+852 1234 5678"
        )
        st.session_state.card_data["phone"] = phone
    
    with col2:
        st.markdown("**郵箱 (Email)**")
        email = st.text_input(
            "Email",
            value=st.session_state.card_data.get("email", ""),
            label_visibility="collapsed",
            placeholder="例如：user@example.com"
        )
        st.session_state.card_data["email"] = email
        
        st.markdown("**地址 (Address)**")
        address = st.text_input(
            "Address",
            value=st.session_state.card_data.get("address", ""),
            label_visibility="collapsed",
            placeholder="例如：香港中環"
        )
        st.session_state.card_data["address"] = address
        
        st.markdown("**備註 (Notes)**")
        notes = st.text_area(
            "Notes",
            value=st.session_state.card_data.get("notes", ""),
            label_visibility="collapsed",
            placeholder="例如：掃描時間或其他備註",
            height=120
        )
        st.session_state.card_data["notes"] = notes
    
    # 添加掃描時間
    if st.button("💾 保存此名片", use_container_width=True):
        if not st.session_state.card_data["notes"]:
            st.session_state.card_data["notes"] = f"掃描時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        
        st.session_state.scan_count += 1
        st.session_state.last_scan = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        st.success("✅ 名片已保存！")

# 標籤 3: 複製到 Google Sheets
with tab3:
    st.markdown("### 💾 複製到 Google Sheets")
    
    if st.session_state.card_data.get("name") or st.session_state.card_data.get("company"):
        st.markdown("""
        <div class="sheet-guide">
        <strong>📋 使用指南：</strong><br><br>
        1️⃣ 複製下面的數據（TSV 或 JSON）<br>
        2️⃣ 打開您的 Google Sheet<br>
        3️⃣ 粘貼數據（Ctrl+V）<br>
        4️⃣ ✅ 完成！
        </div>
        """, unsafe_allow_html=True)
        
        # TSV 格式（制表符分隔）
        st.markdown("**📊 TSV 格式（推薦）**")
        st.markdown("直接粘貼到 Google Sheet，會自動填充各欄位")
        
        tsv_data = "\t".join([
            st.session_state.card_data.get("company", ""),
            st.session_state.card_data.get("name", ""),
            st.session_state.card_data.get("jobTitle", ""),
            st.session_state.card_data.get("phone", ""),
            st.session_state.card_data.get("email", ""),
            st.session_state.card_data.get("address", ""),
            st.session_state.card_data.get("notes", "")
        ])
        
        st.text_area(
            "TSV 格式數據",
            value=tsv_data,
            height=60,
            label_visibility="collapsed"
        )
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**複製 TSV 格式：**")
            st.markdown("""
            1. 選擇上面的文本
            2. Ctrl+C 複製
            3. 打開 Google Sheet
            4. 粘貼（Ctrl+V）
            """)
        
        # JSON 格式
        st.markdown("**📄 JSON 格式**")
        st.markdown("用於其他應用或備份")
        
        json_data = json.dumps(st.session_state.card_data, ensure_ascii=False, indent=2)
        
        st.text_area(
            "JSON 格式數據",
            value=json_data,
            height=150,
            label_visibility="collapsed"
        )
        
        with col2:
            st.markdown("**下載 JSON 文件：**")
            st.download_button(
                label="⬇️ 下載 JSON 文件",
                data=json_data,
                file_name=f"card_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json",
                use_container_width=True
            )
        
        # 清空按鈕
        st.markdown("---")
        if st.button("🔄 清空所有數據", use_container_width=True):
            st.session_state.card_data = {
                "company": "",
                "name": "",
                "jobTitle": "",
                "phone": "",
                "email": "",
                "address": "",
                "notes": ""
            }
            st.rerun()
    else:
        st.info("📸 請先在「📋 編輯」標籤中輸入名片信息")

st.markdown("---")
st.markdown("""
<div class="info-box">
<strong>💡 提示：</strong><br>
- 無需 API 密鑰
- 完全免費
- 永久可用
- 完全隱私（數據不上傳到任何服務）
</div>
""", unsafe_allow_html=True)
