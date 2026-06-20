import streamlit as st
import pandas as pd

st.set_page_config(
    page_title="Gaeun Assistant",
    page_icon="📝",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.title("개운중학교 생기부 작성 도우미")
st.write("PC와 스마트폰 화면에 모두 맞춤형으로 작동하는 2026학년도 기재 시스템입니다.")

FORBIDDEN_WORDS = [
    "토익", "TOEIC", "토플", "TOEFL", "텝스", "TEPS", "오픽", "OPIc", "HSK", "JLPT", "인증시험", "한자검정",
    "대회", "경시", "올림피아드", "시상", "수상경력", "교외상", "표창장", "감사장", "공로상",
    "논문", "학회지", "투고", "등재", "도서출판", "출간", "특허", "실용신안", "상표", "디자인출원",
    "어학연수", "해외 봉사", "해외 활동", "해외 여행",
    "아버지", "어머니", "부모", "친인척", "의사", "교수", "변호사", "검사", "대표", "사장",
    "장학생", "장학금", "대학명", "서울대", "연세대", "고려대", "카이스트", "영재교육원", "발명교실", "학원",
    "자격증", "취득", "방과후학교"
]

tab1, tab2, tab3 = st.tabs(["학생 명렬 및 행발 작성", "독서 활동 점검", "기재 금지어 검사"])

with tab1:
    st.subheader("파일 업로드 및 학생별 종합의견 작성")
    st.write("Excel 또는 CSV 명렬표 파일을 업로드하여 수정본을 관리하세요.")
    
    if "student_df" not in st.session_state:
        st.session_state.student_df = pd.DataFrame({
            "번호": [1, 2, 3], 
            "이름": ["홍길동", "이순신", "강감찬"], 
            "행동특성 및 종합의견": ["", "", ""]
        })

    uploaded_file = st.file_uploader("명렬표 파일 선택", type=["xlsx", "csv"])
    
    if uploaded_file is not None:
        try:
            if uploaded_file.name.endswith('.csv'):
                st.session_state.student_df = pd.read_csv(uploaded_file)
            else:
                st.session_state.student_df = pd.read_excel(uploaded_file)
            st.success("파일 업로드에 성공했습니다.")
        except Exception as e:
            st.error("파일 로딩 중 에러가 발생했습니다.")
            
    df = st.session_state.student_df

    if "이름" in df.columns and "번호" in df.columns:
        if "행동특성 및 종합의견" not in df.columns:
            df["행동특성 및 종합의견"] = ""
            
        student_list = [f"{int(row['번호'])}번 {row['이름']}" for _, row in df.iterrows()]
        selected_student = st.selectbox("작성 대상 학생 선택:", student_list)
        
        idx = student_list.index(selected_student)
        current_text = df.at[idx, "행동특성 및 종합의견"] if pd.notna(df.at[idx, "행동특성 및 종합의견"]) else ""
        
        input_text = st.text_area(
            "선택된 학생의 내용 입력창", 
            value=current_text, 
            height=180
        )
        
        char_count = len(input_text)
        if char_count > 300: 
            st.error(f"글자 수 초과 위험이 있습니다. 현재 {char_count}자 (최대 300자 제한)")
        else:
            st.caption(f"현재 글자 수: {char_count}자 / 300자 제한")
            
        found_forbidden = [word for word in FORBIDDEN_WORDS if word.lower() in input_text.lower()]
        if found_forbidden:
            st.error(f"지침 금지 단어 감지: {', '.join(found_forbidden)}")
            
        if st.button("현재 학생 내용 데이터에 반영하기"):
            st.session_state.student_df.at[idx, "행동특성 및 종합의견"] = input_text
            st.success("해당 학생의 초안 데이터 저장이 임시 완료되었습니다.")
            
        st.write("---")
        st.subheader("전체 명렬표 실시간 누적 현황")
        st.dataframe(st.session_state.student_df, use_container_width=True)
        
        final_csv = st.session_state.student_df.to_csv(index=False).encode('utf-8-sig')
        st.download_button(
            label="최종 작성 완료 파일 다운로드",
            data=final_csv,
            file_name="gaeun_middle_school_records.csv",
            mime="text/csv"
        )

with tab2:
    st.subheader("독서활동상황 지침")
    st.info("정기간행물과 ISSN 도서는 기재가 절대 불가하며, ISBN에 정상 등재된 단행본 도서만 입력할 수 있습니다.")
    
    query = st.text_input("도서명 또는 저자명 검색창:")
    if query:
        st.success(f"입력 포맷 적용 형태: {query}(저자)")

with tab3:
    st.subheader("문장 정밀 점검 및 2026 지침 필터")
    st.warning("생성형 AI가 도출한 문장 그대로 복사해서 생기부에 붙여넣는 실무 행위는 금지됩니다.")
    
    check_text = st.text_area("점검할 텍스트 문단을 통째로 붙여넣으세요", height=200)
    
    if check_text:
        detected = [word for word in FORBIDDEN_WORDS if word.lower() in check_text.lower()]
        
        if detected:
            st.error(f"주의 필요 단어 감지: {', '.join(detected)}")
            st.write(check_text)
        else:
            st.success("안전한 문장 구성으로 확인됩니다.")
            
        if "2026." in check_text or "2026.03" in check_text:
            st.error("서술형 항목 안에는 날짜 데이터를 기재하지 않습니다.")
