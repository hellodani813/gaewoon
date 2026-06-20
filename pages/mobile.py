import streamlit as st
import pandas as pd

# 1. 페이지 기본 설정
st.set_page_config(
    page_title="개운중 생기부 모바일 도우미",
    page_icon="📱",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 모바일 가독성을 높이기 위한 커스텀 CSS
st.markdown("""
    <style>
    .main-title { font-size: 24px; font-weight: bold; color: #1E3A8A; margin-bottom: 5px; }
    .sub-title { font-size: 14px; color: #4B5563; margin-bottom: 20px; }
    .stTabs [data-baseweb="tab"] { font-size: 15px; font-weight: bold; padding: 10px 5px; }
    .stButton>button { width: 100%; height: 45px; font-size: 16px; margin-top: 10px; }
    </style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-title">🏫 개운중 생기부 스마트 도우미</div>', unsafe-allow_html=True)
st.markdown('<div class="sub-title">📱 모바일(스마트폰)과 PC에서 모두 편리하게 작성·점검 가능합니다.</div>', unsafe-allow_html=True)

# 2026 개운중 기재요령 기준 금지어 데이터베이스[cite: 1]
FORBIDDEN_WORDS = [
    "토익", "TOEIC", "토플", "TOEFL", "텝스", "TEPS", "오픽", "OPIc", "HSK", "JLPT", "인증시험", "한자검정",
    "대회", "경시", "올림피아드", "시상", "수상경력", "교외상", "표창장", "감사장", "공로상",
    "논문", "학회지", "투고", "등재", "도서출판", "출간", "특허", "실용신안", "상표", "디자인출원",
    "어학연수", "해외 봉사", "해외 활동", "해외 여행",
    "아버지", "어머니", "부모", "친인척", "의사", "교수", "변호사", "검사", "대표", "사장",
    "장학생", "장학금", "대학명", "서울대", "연세대", "고려대", "카이스트", "영재교육원", "발명교실", "학원",
    "자격증", "취득", "방과후학교"
]

# 모바일 화면을 고려하여 심플하게 3개 탭 구성
tab1, tab2, tab3 = st.tabs(["👤 명렬표/행발", "📚 독서(ISBN)", "🚫 금지어 검사"])

# -----------------------------------------------------------------------------
# TAB 1: 학생 명렬 및 행발 작성
# -----------------------------------------------------------------------------
with tab1:
    st.subheader("👤 모바일 행발 작성방")
    
    if "student_df" not in st.session_state:
        st.session_state.student_df = pd.DataFrame({
            "번호": [1, 2, 3], 
            "이름": ["홍길동", "이순신", "강감찬"], 
            "행동특성 및 종합의견": ["", "", ""]
        })

    uploaded_file = st.file_uploader("📂 명렬표 파일 업로드 (Excel/CSV)", type=["xlsx", "csv"])
    
    if uploaded_file is not None:
        try:
            if uploaded_file.name.endswith('.csv'):
                st.session_state.student_df = pd.read_csv(uploaded_file)
            else:
                st.session_state.student_df = pd.read_excel(uploaded_file)
            st.success("📂 파일을 성공적으로 불러왔습니다!")
        except Exception as e:
            st.error(f"파일 로드 실패: {e}")
            
    df = st.session_state.student_df

    if "이름" in df.columns and "번호" in df.columns:
        if "행동특성 및 종합의견" not in df.columns:
            df["행동특성 및 종합의견"] = ""
            
        student_list = [f"{int(row['번호'])}번 {row['이름']}" for _, row in df.iterrows()]
        selected_student = st.selectbox("🎯 학생 선택:", student_list)
        
        idx = student_list.index(selected_student)
        current_text = df.at[idx, "행동특성 및 종합의견"] if pd.notna(df.at[idx, "행동특성 및 종합의견"]) else ""
        
        input_text = st.text_area(
            f"✍ lobby {selected_student} 입력창", 
            value=current_text, 
            height=150,
            placeholder="~함. 형태로 입력해 주세요."
        )
        
        char_count = len(input_text)
        if char_count > 300: # 2026 기재요령 행발 300자 제한[cite: 1]
            st.error(f"🚨 글자 수 초과! 현재 {char_count}자 (최대 300자)")
        else:
            st.caption(f"📝 글자 수: {char_count}자 / 300자 제한")
            
        found_forbidden = [word for word in FORBIDDEN_WORDS if word.lower() in input_text.lower()]
        if found_forbidden:
            st.error(f"❌ 기재 금지어 포함됨: {', '.join(found_forbidden)}")
            
        if st.button("💾 이 학생 내용 폰에 임시 저장"):
            st.session_state.student_df.at[idx, "행동특성 및 종합의견"] = input_text
            st.success(f"✅ {selected_student} 저장 완료!")
            
        st.write("---")
        st.subheader("📊 작성 현황 확인")
        st.dataframe(st.session_state.student_df, use_container_width=True)
        
        final_csv = st.session_state.student_df.to_csv(index=False).encode('utf-8-sig')
        st.download_button(
            label="📥 최종 파일 스마트폰에 다운로드",
            data=final_csv,
            file_name="개운중_모바일_생기부_작성본.csv",
            mime="text/csv"
        )

# -----------------------------------------------------------------------------
# TAB 2: 독서활동상황 점검
# -----------------------------------------------------------------------------
with tab2:
    st.subheader("📚 독서활동상황(ISBN) 지침 확인")
    st.info("💡 2026 지침: ISBN 도서만 입력 가능 (정기간행물/ISSN 입력 불가), '책제목(저자)' 형식 준수[cite: 1]")
    
    query = st.text_input("🔍 도서명/저자명 입력:")
    if query:
        st.success(f"📝 입력 서식 예시: {query}(저자명)")
        st.markdown("* 중복 기재 주의: 2026학년도부터는 증빙자료가 다르면 동일 도서의 중복 입력이 허용되나, 이전 학년 기록과의 중복은 정정 대상입니다.[cite: 1]")

# -----------------------------------------------------------------------------
# TAB 3: 기재 금지어 실시간 원터치 점검
# -----------------------------------------------------------------------------
with tab3:
    st.subheader("🚫 실시간 기재 금지 검사기")
    st.caption("집이나 밖에서 나이스 텍스트를 카톡 등으로 복사해와서 여기에 붙여넣으면 즉시 검사합니다.")
    
    st.warning("🚨 2026 핵심 규정: AI가 작성해 준 문장을 그대로 생기부에 붙여넣는 행위는 절대 불가합니다.[cite: 1]")
    
    check_text = st.text_area("📱 검사할 문장 붙여넣기", height=200)
    
    if check_text:
        detected = [word for word in FORBIDDEN_WORDS if word.lower() in check_text.lower()]
        
        if detected:
            st.error(f"❌ 금지 의심 단어 발견 ({len(detected)}개): {', '.join(detected)}")
            highlighted = check_text
            for word in detected:
                highlighted = highlighted.replace(word, f" **[{word}]** ")
            st.markdown(highlighted)
        else:
            st.success("✅ 지침을 준수한 안전한 문장입니다!")
            
        if any(date in check_text for date in ["2026.", "2026.03"]):
            st.error("❌ 서술형 항목에는 날짜를 입력하지 않습니다.[cite: 1]")
