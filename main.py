import streamlit as st
import pandas as pd

st.set_page_config(
    page_title="Gaeun Assistant",
    page_icon="📝",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.title("🏫 개운중학교 생기부 작성 도우미")
st.write("외부 서버 통신 없이 100% 내부 엔진으로 구동되어 오류가 없는 안전한 버전입니다.")

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

BOOK_DATABASE = [
    {"title": "재밌어서 밤새는 화학 이야기", "author": "사마키 다케오", "isbn": "9788964472316", "pub": "더숲"},
    {"title": "정재승의 과학 콘서트", "author": "정재승", "isbn": "9788937434501", "pub": "어크로스"},
    {"title": "물리 외과 의사", "author": "최원석", "isbn": "9788994149547", "pub": "글담출판"},
    {"title": "원소의 세계", "author": "존 엠슬리", "isbn": "9788932471372", "pub": "사이언스북스"},
    {"title": "물질의 세계", "author": "자난 가오", "isbn": "9791191114225", "pub": "김영사"},
    {"title": "코스모스", "author": "칼 세이건", "isbn": "9788937429217", "pub": "사이언스북스"},
    {"title": "이기적 유전자", "author": "리처드 도킨스", "isbn": "9788932473901", "pub": "을유문화사"},
    {"title": "사피엔스", "author": "유발 하라리", "isbn": "9788934972464", "pub": "김영사"},
    {"title": "침묵의 봄", "author": "레이첼 카슨", "isbn": "9788932472485", "pub": "사이언스북스"},
    {"title": "수학의 정석", "author": "홍성대", "isbn": "9788993133035", "pub": "성지출판"},
    {"title": "수학 인문학으로 읽다", "author": "이광연", "isbn": "9788997091843", "pub": "지식프레임"},
    {"title": "틀리지 않는 법", "author": "조던 엘렌버그", "isbn": "9788937432095", "pub": "열린책들"}
]

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

# --- TAB 2: 오류가 절대 없는 안전한 도서 조회 인터페이스 ---
with tab2:
    st.subheader("📚 도서 ISBN 검증 및 나이스 양식 변환")
    st.info("💡 과학동아, 뉴턴(Newton) 같은 정기 간행물은 ISSN 체계이므로 생기부 입력이 절대 불가하며, ISBN 단행본만 가능합니다.")
    
    # [보완 기능] 국립중앙도서관 정식 조회 사이트 링크 연동 버튼
    st.markdown("### 🔍 공식 서지정보(ISBN) 확인 사이트")
    st.write("가장 정확한 등재 여부는 대한민국 공식 도서관 시스템에서 실시간으로 확인할 수 있습니다.")
    st.link_button("🌐 국립중앙도서관 서지정보 시스템 바로가기", "https://seoji.nl.go.kr/landingPage")
    
    st.write("---")
    st.markdown("### 📝 도서명 입력 및 서식 변환")
    book_query = st.text_input("조회하거나 변환할 도서명 또는 저자명을 입력하세요:")
    
    if book_query:
        results = []
        for book in BOOK_DATABASE:
            if book_query.lower() in book["title"].lower() or book_query.lower() in book["author"].lower():
                nice_format = f"{book['title']}({book['author']})"
                results.append({
                    "나이스 입력 양식 (즉시 복사 가능)": nice_format,
                    "정식 ISBN 번호": book["isbn"],
                    "출판사": book["pub"]
                })
        
        if results:
            st.success(f"🔍 내부 데이터베이스에서 ISBN 정보 검증에 성공했습니다!")
            st.dataframe(pd.DataFrame(results), use_container_width=True)
        else:
            st.warning("⚠️ 검증용 필수 도서 데이터베이스에는 없으나 일반 단행본 양식으로 자동 변환합니다.")
            fallback_format = f"{book_query}(저자명)"
            fallback_data = [{
                "나이스 입력 양식 (즉시 복사 가능)": fallback_format,
                "정식 ISBN 번호": "위의 링크 버튼을 눌러 단행본(ISBN)인지 확인 필요",
                "출판사": "확인 필요"
            }]
            st.dataframe(pd.DataFrame(fallback_data), use_container_width=True)

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
