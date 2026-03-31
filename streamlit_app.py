"""
CardScan AI - 名片掃描系統（Streamlit 版本）
完全免費的 Web App，使用 Google Gemini API
"""

import streamlit as st
import google.generativeai as genai
from PIL import Image
import io
import json
from datetime import datetime
import base64

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
</style>
""", unsafe_allow_html=True)

# 初始化 session state
if "api_key" not in st.session_state:
    # 自動從 Streamlit Secrets 讀取 API 密鑰
    st.session_state.api_key = st.secrets.get("GEMINI_API_KEY", "")
if "card_data" not in st.session_state:
    st.session_state.card_data = None
if "image_data" not in st.session_state:
    st.session_state.image_data = None

# 標題
st.title("📇 CardScan AI")
st.markdown("### Rena的智能名片掃描系統")
st.markdown("使用 AI 自動識別名片信息 | 完全免費 🆓")

# 側邊欄設定
with st.sidebar:
    st.header("⚙️ 設定")
    
    st.markdown("### 🔑 API 密鑰設定")
    
    # 顯示當前狀態
    if st.session_state.api_key:
        st.success("✅ API 密鑰已設定")
    else:
        st.warning("⚠️ 請設定 API 密鑰")
    
    # API 密鑰輸入
    api_key_input = st.text_input(
        "Google Gemini API 密鑰",
        value=st.session_state.api_key,
        type="password",
        help="訪問 https://ai.google.dev/ 獲取免費 API 密鑰"
     )
    
    if api_key_input:
        st.session_state.api_key = api_key_input
    
    # 幫助信息
    st.markdown("---")
    st.markdown("### 📚 幫助")
    st.markdown("""
    **如何獲取 API 密鑰？**
    
    1. 訪問 https://ai.google.dev/
    2. 點擊「Get API key」
    3. 選擇「Create API key in new project」
    4. 複製生成的密鑰
    5. 粘貼到上方
    
    **完全免費！**
    - 每天 1,500 個免費請求
    - 無需信用卡
    - 永遠免費
    """ )
    
    st.markdown("---")
    st.markdown("### 📊 使用統計")
    st.markdown(f"""
    - 掃描次數: {st.session_state.get('scan_count', 0)}
    - 上次掃描: {st.session_state.get('last_scan', '未掃描')}
    """)

# 主要內容
if not st.session_state.api_key:
    st.markdown("""
    <div class="info-box">
    <strong>🔐 需要設定 API 密鑰</strong>  

    請在左側邊欄中設定您的 Google Gemini API 密鑰才能使用此應用。
    </div>
    """, unsafe_allow_html=True)
else:
    # 配置 Gemini API
    genai.configure(api_key=st.session_state.api_key)
    
    # 標籤頁
    tab1, tab2, tab3 = st.tabs(["📸 掃描", "📋 結果", "💾 Google Sheets"])
    
    # 標籤 1: 掃描
    with tab1:
        st.markdown("### 📸 拍攝或上傳名片")
        
        # 上傳圖片
        uploaded_file = st.file_uploader(
            "選擇名片圖片",
            type=["jpg", "jpeg", "png", "webp"],
            help="支持 JPG、PNG、WebP 格式"
        )
        
        if uploaded_file is not None:
            # 顯示圖片
            image = Image.open(uploaded_file)
            st.image(image, caption="上傳的名片", use_column_width=True)
            
            # 掃描按鈕
            if st.button("🔍 掃描名片", key="scan_button"):
                with st.spinner("🤖 AI 正在識別名片..."):
                    try:
                        # 轉換為 Base64
                        image_bytes = io.BytesIO()
                        image.save(image_bytes, format="JPEG")
                        image_base64 = base64.b64encode(image_bytes.getvalue()).decode()
                        
                        # 調用 Gemini API
                        model = genai.GenerativeModel("gemini-pro-vision")
                        
                        prompt = """你是一個名片識別專家。請仔細分析這張名片圖片，並提取以下信息：

1. 姓名（Name）
2. 公司（Company）
3. 職稱（Job Title）
4. 電話（Phone）
5. 郵箱（Email）
6. 地址（Address）
7. 其他備註（Notes）

請以 JSON 格式返回結果，格式如下：
{
  "name": "提取的姓名",
  "company": "提取的公司名稱",
  "jobTitle": "提取的職稱",
  "phone": "提取的電話號碼",
  "email": "提取的郵箱地址",
  "address": "提取的地址",
  "notes": "其他備註或掃描時間"
}

如果某些信息在名片上找不到，請使用空字符串 ""。
請只返回 JSON，不要返回其他文本。"""
                        
                        response = model.generate_content([
                            {
                                "mime_type": "image/jpeg",
                                "data": image_base64
                            },
                            prompt
                        ])
                        
                        # 解析響應
                        response_text = response.text.strip()
                        
                        # 嘗試提取 JSON
                        try:
                            card_data = json.loads(response_text)
                        except:
                            # 如果直接解析失敗，嘗試提取 JSON
                            import re
                            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
                            if json_match:
                                card_data = json.loads(json_match.group())
                            else:
                                raise ValueError("無法解析 AI 響應")
                        
                        # 添加掃描時間
                        if not card_data.get("notes"):
                            card_data["notes"] = f"掃描時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                        
                        # 保存到 session state
                        st.session_state.card_data = card_data
                        st.session_state.image_data = image_base64
                        st.session_state.scan_count = st.session_state.get("scan_count", 0) + 1
                        st.session_state.last_scan = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                        
                        st.success("✅ 名片識別成功！")
                        st.rerun()
                        
                    except Exception as e:
                        st.markdown(f"""
                        <div class="error-box">
                        <strong>❌ 識別失敗</strong>  

                        {str(e)}
                        </div>
                        """, unsafe_allow_html=True)
    
    # 標籤 2: 結果
    with tab2:
        st.markdown("### 📋 識別結果")
        
        if st.session_state.card_data:
            card_data = st.session_state.card_data
            
            # 顯示結果
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**👤 姓名**")
                name = st.text_input("姓名", value=card_data.get("name", ""), key="name_input")
                card_data["name"] = name
                
                st.markdown("**🏢 公司**")
                company = st.text_input("公司", value=card_data.get("company", ""), key="company_input")
                card_data["company"] = company
                
                st.markdown("**💼 職稱**")
                job_title = st.text_input("職稱", value=card_data.get("jobTitle", ""), key="job_title_input")
                card_data["jobTitle"] = job_title
            
            with col2:
                st.markdown("**📞 電話**")
                phone = st.text_input("電話", value=card_data.get("phone", ""), key="phone_input")
                card_data["phone"] = phone
                
                st.markdown("**📧 郵箱**")
                email = st.text_input("郵箱", value=card_data.get("email", ""), key="email_input")
                card_data["email"] = email
                
                st.markdown("**📍 地址**")
                address = st.text_input("地址", value=card_data.get("address", ""), key="address_input")
                card_data["address"] = address
            
            st.markdown("**📝 備註**")
            notes = st.text_area("備註", value=card_data.get("notes", ""), key="notes_input", height=80)
            card_data["notes"] = notes
            
            # 更新 session state
            st.session_state.card_data = card_data
            
            # 操作按鈕
            col1, col2, col3 = st.columns(3)
            
            with col1:
                if st.button("✅ 保存", key="save_button"):
                    st.markdown("""
                    <div class="success-box">
                    <strong>✅ 數據已保存</strong>  

                    您可以將其保存到 Google Sheets 或導出為 JSON。
                    </div>
                    """, unsafe_allow_html=True)
            
            with col2:
                if st.button("🔄 重新掃描", key="rescan_button"):
                    st.session_state.card_data = None
                    st.session_state.image_data = None
                    st.rerun()
            
            with col3:
                # 導出為 JSON
                json_str = json.dumps(card_data, ensure_ascii=False, indent=2)
                st.download_button(
                    label="📥 導出 JSON",
                    data=json_str,
                    file_name=f"card_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                    mime="application/json"
                )
        
        else:
            st.markdown("""
            <div class="info-box">
            <strong>📋 沒有結果</strong>  

            請先在「掃描」標籤中上傳名片並掃描。
            </div>
            """, unsafe_allow_html=True)
    
    # 標籤 3: Google Sheets
    with tab3:
        st.markdown("### 💾 Google Sheets 集成")
        
        st.markdown("""
        **功能說明：**
        - 將識別的名片信息自動保存到 Google Sheets
        - 完全免費
        - 支持多個試算表
        
        **設定步驟：**
        1. 建立 Google Sheets 試算表
        2. 獲取試算表 ID
        3. 獲取 Google API 令牌
        4. 在此設定並保存
        
        **目前狀態：** ⏳ 開發中
        """)
        
        st.info("💡 提示：您可以手動將導出的 JSON 複製到 Google Sheets 中。")

# 頁腳
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666; font-size: 12px;">
    <p>CardScan AI v1.0 | 完全免費 🆓 | 使用 Google Gemini API</p>
    <p>📧 隱私政策：照片只在瀏覽器中處理，不被保存</p>
</div>
""", unsafe_allow_html=True)
