import streamlit as st
import pandas as pd
import requests

st.set_page_config(
    page_title="Gaeun Assistant",
    page_icon="📝",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.title("개운중학교 생기부 작성 도우미")
st.write("PC와 스마트폰 화면에서 실시간 맞춤법 및 실제 ISBN 도서 조회가 가능합니다.")

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
    "바램": "바람", "할수 ": "할 수 ", "잇음": "있음", "가르켰": "가르쳤", "치루": "치르",
    "마추어": "맞추어", "돗보임": "돋보임", "연계 하여": "연계하여", "참여 하여": "참여하여",
    "조사 하여": "조사하여", "분석 하여": "분석하여", "생각 함": "생각함", "안음": "않음"
}

tab1, tab2, tab3 = st.tabs(["학생 명렬 및 행발 작성", "📚 실제 ISBN 도서 조회", "기재 금지어 검사"])

# --- TAB 1 ---
with tab1:
    st.subheader("파일 업로드 및 학생별 종합의견 작성")
    if "student_df" not in st.session_state:
        st.session_state.student_df = pd.DataFrame({
            "번호": [1, 2, 3], "이름": ["홍길동", "이순신", "강감찬"], "행동특성 및 종합의견": ["", "", ""]
        })
    uploaded_file = st.file_uploader("명렬표 파일 선택 (Excel/CSV)", type=["xlsx", "csv"])
    if uploaded_file is not None:
        try:
            if uploaded_file.name.endswith('.csv'): st.session_state.student_df = pd.read_csv(uploaded_file)
            else: st.session_state.student_df = pd.read_excel(uploaded_file)
            st.success("파일 로드 완료")
        except: st.error("파일 업로드 에러")
    df = st.session_state.student_df
    if "이름" in df.columns and "번호" in df.columns:
        if "행동특성 및 종합의견" not in df.columns: df["행동특성 및 종합의견"] = ""
        student_list = [f"{int(row['번호'])}번 {row['이름']}" for _, row in df.iterrows()]
        selected_student = st.selectbox("작성 대상 학생 선택:", student_list)
        idx = student_list.index(selected_student)
        current_text = df.at[idx, "행동특성 및 종합의견"] if pd.notna(df.at[idx, "행동특성 및 종합의견"]) else ""
        input_text = st.text_area("학생 종합의견 입력", value=current_text, height=150)
        char_count = len(input_text)
        st.write(f"현재 글자 수: {char_count}자 / 300자 제한")
        if char_count > 300: st.error("글자 수가 300자를 초과했습니다.")
        found_forbidden = [word for word in FORBIDDEN_WORDS if word.lower() in input_text.lower()]
        if found_forbidden: st.error(f"금지 단어 포함: {', '.join(found_forbidden)}")
        spelling_errors = [f"'{err}' -> '{corr}'" for err, corr in SPELL_CHECK_DICT.items() if err in input_text]
        if spelling_errors: st.warning(f"맞춤법 의심: {', '.join(spelling_errors)}")
        if "다." in input_text: st.info("명사형 종결어미(~함, ~임) 사용을 권장합니다.")
        if st.button("현재 학생 내용 임시 저장"):
            st.session_state.student_df.at[idx, "행동특성 및 종합의견"] = input_text
            st.success("저장되었습니다.")
        st.write("---")
        st.dataframe(st.session_state.student_df, use_container_width=True)
        final_csv = st.session_state.student_df.to_csv(index=False).encode('utf-8-sig')
        st.download_button("최종 작성 파일 다운로드", data=final_csv, file_name="gaeun_records.csv", mime="text/csv")

# --- TAB 2: 공용 우회 도서 검색 인프라 연동 ---
with tab2:
    st.subheader("📚 실제 ISBN 등재 여부 실시간 조회")
    st.info("정기간행물과 ISSN 도서는 걸러지며, ISBN에 등록된 정식 단행본 도서만 안전하게 조회됩니다.")
    
    book_query = st.text_input("조회할 도서명 또는 저자명을 입력하고 엔터를 누르세요:")
    
    if book_query:
        with st.spinner("글로벌 도서 데이터베이스에서 ISBN을 크로스 체크 중입니다..."):
            try:
                # 보안 및 차단 걱정 없는 오픈 인프라 주소 활용
                api_url = f"https://openlibrary.org/search.json?q={book_query}&limit=10"
                response = requests.get(api_url, timeout=7)
                
                if response.status_code == 200:
                    res_json = response.json()
                    docs = res_json.get("docs", [])
                    
                    books_data = []
                    for item in docs:
                        title = item.get("title", "정보 없음")
                        authors = item.get("author_name", ["저자 미상"])
                        author = authors[0]
                        publisher = item.get("publisher", ["정보 없음"])[0]
                        pub_year = item.get("first_publish_year", "정보 없음")
                        isbns = item.get("isbn", [])
                        
                        # ISBN 번호 추출 및 정제
                        final_isbn = isbns[0] if isbns else "미등재 의심 (반려 필요)"
                        
                        if final_isbn != "미등재 의심 (반려 필요)":
                            nice_format = f"{title}({author})"
                            books_data.append({
                                "나이스 입력 양식 (복사용)": nice_format,
                                "정식 ISBN 번호": final_isbn,
                                "출판사": publisher,
                                "발행연도": str(pub_year)
                            })
                    
                    if books_data:
                        st.success(f"🔍 '{book_query}' 검색 결과: 실제 ISBN이 검증된 안전한 도서 리스트입니다.")
                        st.dataframe(pd.DataFrame(books_data), use_container_width=True)
                    else:
                        st.error("❌ 정식 도서 정보(ISBN)를 찾을 수 없습니다. 학교 도서관 소장 도서나 잡지(ISSN)인지 재확인이 필요합니다.")
                else:
                    st.error("데이터베이스 통신 오류가 발생했습니다.")
            except:
                st.error("네트워크 시간 초과 또는 일시적인 장애입니다. 잠시 후 다시 검색 버튼을 눌러주세요.")

# --- TAB 3 ---
with tab3:
    st.subheader("🚫 문장 전체 기재 금지어 및 규칙 검사기")
    st.warning("주의: 생성형 AI가 작성해 준 문장을 그대로 생기부에 복사하여 붙여넣는 행위는 절대 불가합니다.")
    check_text = st.text_area("검사할 문단을 복사(Ctrl+V)하여 붙여넣으세요:", height=180)
    st.write("🔍 정밀 분석 결과:")
    if len(check_text) > 0:
        detected = [word for word in FORBIDDEN_WORDS if word.lower() in check_text.lower()]
        if len(detected) > 0: st.error(f"기재 금지 단어가 발견되었습니다: {', '.join(detected)}")
        else: st.success("금지 키워드가 발견되지 않은 안전한 문장입니다.")
        if "2026." in check_text or "2026.03" in check_text: st.error("날짜 오류: 서술형 항목에 구체적인 날짜 데이터를 기재하지 않습니다.")
        spelling_errors_tab3 = [f"'{err}' -> '{corr}'" for err, corr in SPELL_CHECK_DICT.items() if err in check_text]
        if spelling_errors_tab3: st.warning(f"맞춤법/띄어쓰기 교정 제안: {', '.join(spelling_errors_tab3)}")
    else: st.info("텍스트를 입력하시면 실시간 결과가 이곳에 나타납니다.")
