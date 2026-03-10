import streamlit as st
import pandas as pd
import numpy as np
import os

# 1. 페이지 설정
st.set_page_config(page_title="H&M GNN Cold-Start Recommender", layout="wide")

# --- 🎨 커스텀 CSS (너비 극대화 및 이미지 레이아웃 조정) ---
st.markdown("""
    <style>
    /* 전체 배경색 및 폰트 설정 */
    .stApp { background-color: #F5F0E1; }
    [data-testid="stSidebar"] { background-color: #FAF6F0; border-right: 1px solid #E5E0D5; }
    .stApp, .stMarkdown, p, span, h1, h2, h3, label { color: #000000 !important; }

    /* 상단 타이틀 바 (가로 꽉 차게) */
    .header-container { 
        width: 100%;
        padding: 40px 0 20px 0; 
        border-bottom: 2px solid #000000; 
        margin-bottom: 40px; 
    }
    .main-title { 
        font-size: 6rem; 
        font-weight: 900; 
        letter-spacing: -2px; 
        line-height: 0.9; 
        color: #AA3D1C !important; 
        text-transform: uppercase; 
    }
    .main-subtitle { font-size: 1.8rem; font-weight: 700; margin-top: 5px; }

    /* 데이터프레임 너비 100% 강제 */
    .stDataFrame { width: 100% !important; }

    /* 구매 섹션: 컬럼 내부 요소가 끝까지 차도록 설정 */
    div[data-testid="column"] {
        display: flex;
        align-items: flex-end;
        width: 100%;
    }

    /* 선택 상자(Selectbox) 너비 최적화 */
    div[data-testid="stSelectbox"] {
        width: 100% !important;
    }

    /* BUY NOW 버튼 스타일 (오른쪽 끝 정렬) */
    div.stButton > button {
        width: 100%;
        background-color: #AA3D1C !important;
        color: white !important;
        border: none;
        height: 2.8rem;
        font-weight: bold;
        border-radius: 5px;
        white-space: nowrap;
    }
    
    /* 이미지 그리드 시스템: 높이 통일 및 여백 조절 */
    .styled-image img {
        width: 100%;
        height: 450px !important;
        object-fit: cover;
        border-radius: 10px;
        border: 1px solid #000;
        margin-bottom: 20px; /* 이미지 간 세로 간격 */
    }
    </style>
    """, unsafe_allow_html=True)

# 2. 데이터 로드 (샘플링)
@st.cache_data
def load_data():
    product_groups = ['Garment Lower body', 'Socks & Tights', 'Garment Upper body', 'Underwear', 'Swimwear', 'Accessories', 'Shoes']
    color_groups = ['Black', 'White', 'Blue', 'Beige', 'Grey', 'Red']
    
    cust = pd.DataFrame({
        'customer_id': range(1, 201),
        'gnn_persona': np.random.choice(['Trendy', 'Basic', 'Sporty', 'Classic', 'Luxury'], 200),
        'age': np.random.randint(15, 80, 200),
        'channel_preference': np.random.choice(['Online', 'Store'], 200)
    })
    
    prod = pd.DataFrame({
        'article_id': range(1001, 1501),
        'prod_name': [f"H&M New Arrival {i}" for i in range(1001, 1501)],
        'product_group_name': np.random.choice(product_groups, 500),
        'colour_group_name': np.random.choice(color_groups, 500),
        'price_tier': np.random.choice(['Budget', 'Regular', 'Premium'], 500),
        'gnn_persona': np.random.choice(['Trendy', 'Basic', 'Sporty', 'Classic', 'Luxury'], 500),
        'is_cold': np.random.choice([True, False], 500, p=[0.4, 0.6])
    })
    return cust, prod, product_groups, color_groups

customers, products, PROD_LIST, COLOR_LIST = load_data()

# --- 사이드바 ---
with st.sidebar:
    st.title("맞춤 필터")
    age_range = st.slider("연령대", 15, 80, (20, 35))
    channel_val = st.selectbox("선호 채널", customers['channel_preference'].unique())
    st.divider()
    prod_group = st.multiselect("상품군", options=PROD_LIST, default=['Garment Upper body'])
    color_group = st.multiselect("색상", options=COLOR_LIST, default=['Black', 'White'])
    price_val = st.select_slider("가격대", options=['Budget', 'Regular', 'Premium'], value=('Budget', 'Regular'))

# --- 메인 화면 ---

# 1. 헤더
st.markdown("""
    <div class="header-container">
        <div class="main-title">LOG & LOOK</div>
        <div class="main-subtitle">WHEN LOG MEETS LOOK</div>
    </div>
    """, unsafe_allow_html=True)

# 2. 분석 결과 도출
filtered_customers = customers[(customers['age'].between(age_range[0], age_range[1])) & (customers['channel_preference'] == channel_val)]

if not filtered_customers.empty:
    target_persona = filtered_customers['gnn_persona'].mode()[0]
    
    m_col1, m_col2 = st.columns(2)
    m_col1.metric("선택된 그룹", target_persona)
    m_col2.metric("선택 그룹 고객 수", f"{len(filtered_customers)}명")

    recommendations = products[
        (products['is_cold'] == True) & 
        (products['gnn_persona'] == target_persona) &
        (products['product_group_name'].isin(prod_group)) &
        (products['colour_group_name'].isin(color_group)) &
        (products['price_tier'].isin(price_val))
    ]

    # 3. 추천 리스트 및 구매 섹션
    st.subheader("추천 상품 리스트")
    if not recommendations.empty:
        st.dataframe(recommendations[['prod_name', 'product_group_name', 'colour_group_name', 'price_tier']], 
                     hide_index=True, use_container_width=True)
        
        # 구매 섹션 (9:1 비율로 가로 꽉 차게 설정)
        buy_col1, buy_col2 = st.columns([9, 1]) 
        with buy_col1:
            selected_item = st.selectbox("상품 선택", recommendations['prod_name'].tolist(), label_visibility="collapsed")
        with buy_col2:
            if st.button("BUY NOW"):
                st.balloons()
                st.success(f"**{selected_item}** 구매 완료!")
    else:
        st.warning("조건에 부합하는 상품이 없습니다.")
    
    st.divider()
    
    # 4. 스타일 프리뷰 (hm (1) 밑에 hm (4) 배치)
    img_col1, img_col2, img_col3 = st.columns(3)
    
    with img_col1:
        # 첫 번째 사진: hm (1).png
        if os.path.exists("hm (1).png"):
            st.markdown('<div class="styled-image">', unsafe_allow_html=True)
            st.image("hm (1).png", use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)
        # 두 번째 사진 (hm (1) 바로 아래): hm (4).png
        if os.path.exists("hm (4).png"):
            st.markdown('<div class="styled-image">', unsafe_allow_html=True)
            st.image("hm (4).png", use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)
            
    with img_col2:
        if os.path.exists("hm (2).png"):
            st.markdown('<div class="styled-image">', unsafe_allow_html=True)
            st.image("hm (2).png", use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)
            
    with img_col3:
        if os.path.exists("hm (3).png"):
            st.markdown('<div class="styled-image">', unsafe_allow_html=True)
            st.image("hm (3).png", use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)

else:
    st.error("데이터가 없습니다.")

st.divider()
st.caption("H&M Data Science Project | GNN-based Cold Start Recommendation System")