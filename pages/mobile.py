import streamlit as st
import pandas as pd

st.set_page_config(
    page_title="Gaeun Assistant",
    page_icon="📱",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.title("🏫 개운중 생기부 스마트 도우미")
st.write("📱 모바일(스마트폰)과 PC에서 모두 편리하게 작성 및 점검 가능합니다.")

FORBIDDEN_WORDS = [
    "토익", "TOEIC", "토플", "TOEFL", "텝스", "TEPS", "오픽", "OPIc", "HSK", "JLPT", "인증시험", "한자검정",
    "대회", "경시", "올림피아드", "시상", "수상경력", "교외상", "표창장", "감사장", "공로상",
    "논문", "학회지", "투고", "등재", "도서출판", "출간", "특허", "실용신안", "상표", "디자인출원",
    "어학연수", "해외 봉사", "해외 활동", "해외 여행",
    "아버지", "어머니", "부모", "친인척", "의사", "교수", "변호사", "검사", "대표", "사장",
    "장학생", "장학금", "대학명", "서울대", "연세대", "고려대", "카이스트", "영재교육원", "발명교실", "학원",
    "자격증", "취득", "방과후학교"
]

tab1, tab2, tab3 = st.tabs(["👤 명렬표/행발", "📚 독서(ISBN)", "🚫 금지어 검사"])

# TAB 1
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
            st.success("📂 로드 완료")
        except Exception as e:
            st.error("실패")
            
    df = st.session_state.student_df

    if "이름" in df.columns and "번호" in df.columns:
        if "행동특성 및 종합의견" not in df.columns:
            df["행동특성 및 종합의견"] = ""
            
        student_list = [f"{int(row['번호'])}번 {row['이름']}" for _, row in df.iterrows()]
        selected_student = st.selectbox("🎯 학생 선택:", student_list)
        
        idx = student_list.index(selected_student)
        current_text = df.at[idx, "행동특성 및 종합의견"] if pd.notna(df.at[idx, "행동특성 및 종합의견"]) else ""
        
        input_text = st.text_area(
            "✍ 내용 입력창", 
            value=current_text, 
            height=150
        )
        
        char_count = len(input_text)
        if char_count > 300: 
            st.error(f"🚨 글자 수 초과! 현재 {char_count}자 (최대 300자)")
        else:
            st.caption(f"📝 글자 수: {char_count}자 / 300자 제한")
            
        found_forbidden = [word for word in FORBIDDEN_WORDS if word.lower() in input_text.lower()]
        if found_forbidden:
            st.error(f"❌ 기재 금지어 포함됨: {', '.join(found_forbidden)}")
            
        if st.button("💾 이 학생 내용 저장"):
            st.session_state.student_df.at[idx, "행동특성 및 종합의견"] = input_text
            st.success("저장 완료")
            
        st.write("---")
        st.subheader("📊 작성 현황 확인")
        st.dataframe(st.session_state.student_df, use_container_width=True)
        
        final_csv = st.session_state.student_df.to_csv(index=False).encode('utf-8-sig')
        st.download_button(
            label="📥 최종 파일 다운로드",
            data=final_csv,
            file_name="gaeun_result.csv",
            mime="text/csv"
        )

# TAB 2
with tab2:
    st.subheader("📚 독서활동상황 지침 확인")
    st.info("ISBN 도서만 입력 가능합니다. 정기간행물이나 ISSN 도서는 입력할 수 없습니다.")
    
    query = st.text_input("🔍 도서명 또는 저자명 입력:")
    if query:
        st.success(f"서식 예시: {query}(저자)")

# TAB 3
with tab3:
    st.subheader("🚫 실시간 기재 금지 검사기")
    st.warning("AI가 작성한 문장을 그대로 생기부에 복사하여 붙여넣는 행위는 금지됩니다.")
    
    check_text = st.text_area("📱 검사할 문장 붙여넣기", height=200)
    
    if check_text:
        detected = [word for word in FORBIDDEN_WORDS if word.lower() in check_text.lower()]
        
        if detected:
            st.error(f"❌ 금지 의심 단어 발견: {', '.join(detected)}")
            st.write(check_text)
        else:
            st.success("✅ 안전한 문장입니다.")
            
        if "2026." in check_text or "2026.03" in check_text:
            st.error("❌ 서술형 항목에는 날짜를 입력하지 않습니다.")
