import streamlit as st
import pandas as pd

st.set_page_config(
    page_title="Gaeun Assistant",
    page_icon="QL",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.title("개운중학교 생기부 작성 도우미")
st.write("모든 기능이 항상 활성화되어 있는 2026학년도 안정화 버전입니다.")

FORBIDDEN_WORDS = [
    "토익", "TOEIC", "토플", "TOEFL", "텝스", "TEPS", "오픽", "OPIc", "HSK", "JLPT", "인증시험", "한자검정",
    "대회", "경시", "올림피아드", "시상", "수상경력", "교외상", "표창장", "감사장", "공로상",
    "논문", "학회지", "투고", "등재", "도서출판", "출간", "특허", "실용신안", "상표", "디자인출원",
    "어학연수", "해외 봉사", "해외 활동", "해외 여행",
    "아버지", "어머니", "부모", "친인척", "의사", "교수", "변호사", "검사", "대표", "사장",
    "장학생", "장학금", "대학명", "서울대", "연세대", "고려대", "카이스트", "영재교육원", "발명교실", "학원",
    "자격증", "취득", "방과후학교"
]

SPELL_CHECK_DICT = {
    "바램": "바람",
    "할수 ": "할 수 ",
    "잇음": "있음",
    "가르켰": "가르쳤",
    "치루": "치르",
    "마추어": "맞추어",
    "돗보임": "돋보임",
    "연계 하여": "연계하여",
    "참여 하여": "참여하여",
    "조사 하여": "조사하여",
    "분석 하여": "분석하여",
    "생각 함": "생각함",
    "안음": "않음"
}

tab1, tab2, tab3 = st.tabs(["학생 명렬 및 행발 작성", "독서 활동 점검", "기재 금지어 검사"])

# --- TAB 1 ---
with tab1:
    st.subheader("파일 업로드 및 학생별 종합의견 작성")
    
    if "student_df" not in st.session_state:
        st.session_state.student_df = pd.DataFrame({
            "번호": [1, 2, 3], 
            "이름": ["홍길동", "이순신", "강감찬"], 
            "행동특성 및 종합의견": ["", "", ""]
        })

    uploaded_file = st.file_uploader("명렬표 파일 선택 (Excel/CSV)", type=["xlsx", "csv"])
    
    if uploaded_file is not None:
        try:
            if uploaded_file.name.endswith('.csv'):
                st.session_state.student_df = pd.read_csv(uploaded_file)
            else:
                st.session_state.student_df = pd.read_excel(uploaded_file)
            st.success("파일 로드 완료")
        except:
            st.error("파일 업로드 에러")
            
    df = st.session_state.student_df

    if "이름" in df.columns and "번호" in df.columns:
        if "행동특성 및 종합의견" not in df.columns:
            df["행동특성 및 종합의견"] = ""
            
        student_list = [f"{int(row['번호'])}번 {row['이름']}" for _, row in df.iterrows()]
        selected_student = st.selectbox("작성 대상 학생 선택:", student_list)
        
        idx = student_list.index(selected_student)
        current_text = df.at[idx, "행동특성 및 종합의견"] if pd.notna(df.at[idx, "행동특성 및 종합의견"]) else ""
        
        input_text = st.text_area("학생 종합의견 입력", value=current_text, height=150)
        
        char_count = len(input_text)
        st.write(f"현재 글자 수: {char_count}자 / 300자 제한")
        
        if char_count > 300: 
            st.error("글자 수가 300자를 초과했습니다.")
            
        found_forbidden = [word for word in FORBIDDEN_WORDS if word.lower() in input_text.lower()]
        if found_forbidden:
            st.error(f"금지 단어 포함: {', '.join(found_forbidden)}")
            
        spelling_errors = [f"'{err}' -> '{corr}' 제안" for err, corr in SPELL_CHECK_DICT.items() if err in input_text]
        if spelling_errors:
            st.warning(f"맞춤법/띄어쓰기 의심: {', '.join(spelling_errors)}")
            
        if "다." in input_text:
            st.info("팁: 명사형 종결어미(~함, ~임) 사용을 권장합니다.")
            
        if st.button("현재 학생 내용 임시 저장"):
            st.session_state.student_df.at[idx, "행동특성 및 종합의견"] = input_text
            st.success("저장되었습니다.")
            
        st.write("---")
        st.dataframe(st.session_state.student_df, use_container_width=True)
        
        final_csv = st.session_state.student_df.to_csv(index=False).encode('utf-8-sig')
        st.download_button("최종 작성 파일 다운로드", data=final_csv, file_name="gaeun_records.csv", mime="text/csv")

# --- TAB 2 ---
with tab2:
    st.subheader("📚 독서활동상황 형식 확인 규칙")
    st.info("ISBN 단행본 도서만 입력 가능합니다. (잡지, 정기 간행물, ISSN 도서 입력 불가)")
    
    query = st.text_input("검색하거나 검증할 도서명 또는 저자명을 입력하세요:")
    
    st.write("📝 **나이스 입력 포맷 예시:**")
    if len(query) > 0:
        st.success(f"{query}(저자명)")
    else:
        st.success("도서명(저자명)")
        
    st.markdown("- 2026 개정: 동일 도서 반복 독서 시 증빙자료가 다르면 중복 입력 가능(이전 학년 간 중복은 정정 대상)")

# --- TAB 3 ---
with tab3:
    st.subheader("🚫 문장 전체 기재 금지어 및 규칙 검사기")
    st.warning("주의: 생성형 AI가 작성해 준 문장을 그대로 생기부에 복사하여 붙여넣는 행위는 절대 불가합니다.")
    
    check_text = st.text_area("검사할 문단을 복사(Ctrl+V)하여 붙여넣으세요:", height=180)
    
    st.write("🔍 **정밀 분석 결과:**")
    
    if len(check_text) > 0:
        detected = [word for word in FORBIDDEN_WORDS if word.lower() in check_text.lower()]
        if len(detected) > 0:
            st.error(f"기재 금지 단어가 발견되었습니다: {', '.join(detected)}")
        else:
            st.success("금지 키워드가 발견되지 않은 안전한 문장입니다.")
            
        if "2026." in check_text or "2026.03" in check_text:
            st.error("날짜 오류: 서술형 항목 전반에 걸쳐 구체적인 날짜 데이터를 기재하지 않습니다.")
            
        spelling_errors_tab3 = [f"'{err}' -> '{corr}'" for err, corr in SPELL_CHECK_DICT.items() if err in check_text]
        if spelling_errors_tab3:
            st.warning(f"맞춤법/띄어쓰기 교정 제안: {', '.join(spelling_errors_tab3)}")
    else:
        st.info("텍스트를 입력하시면 실시간 결과가 이곳에 나타납니다.")
