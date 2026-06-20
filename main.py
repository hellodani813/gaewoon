import streamlit as st
import pandas as pd
import requests

# 1. 페이지 기본 설정 및 디자인
st.set_page_config(
    page_title="개운중학교 생기부 작성 도우미",
    page_icon="🏫",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 커스텀 스타일 (깔끔한 교육기관 톤앤매너)
st.markdown("""
    <style>
    .main-title { font-size: 28px; font-weight: bold; color: #1E3A8A; margin-bottom: 5px; }
    .sub-title { font-size: 15px; color: #4B5563; margin-bottom: 25px; }
    .stTabs [data-baseweb="tab"] { font-size: 16px; font-weight: bold; }
    </style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-title">🏫 2026학년도 개운중학교 생기부 기재 도우미</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">선생님들의 안전하고 정확한 학교생활기록부 작성을 위한 점검 툴입니다.</div>', unsafe_allow_html=True)

# 2026 개운중 기재요령 기준 금지어 데이터베이스 구성
FORBIDDEN_WORDS = [
    # 가. 공인어학시험 및 인증
    "토익", "TOEIC", "토플", "TOEFL", "텝스", "TEPS", "오픽", "OPIc", "HSK", "JLPT", "인증시험", "한자검정",
    # 나. 대회 (수상경력 외 입력 절대 불가)
    "대회", "경시", "올림피아드", "시상", "수상경력",
    # 다. 교외상
    "교외상", "표창장", "감사장", "공로상",
    # 바~아. 연구 및 지식재산
    "논문", "학회지", "투고", "등재", "도서출판", "출간", "특허", "실용신안", "상표", "디자인출원",
    # 자. 해외 활동
    "어학연수", "해외 봉사", "해외 활동", "해외 여행",
    # 차. 부모 사회경제적 지위 암시
    "아버지", "어머니", "부모", "친인척", "의사", "교수", "변호사", "검사", "대표", "사장",
    # 카. 장학금 (행발 칭찬 유의)
    "장학생", "장학금",
    # 타. 특정 대학, 기관, 상호, 강사명
    "대학명", "서울대", "연세대", "고려대", "카이스트", "영재교육원", "발명교실", "학원",
    # 파. 자격증
    "자격증", "취득",
    # 기타 금지 사항 (방과후학교 등)
    "방과후학교"
]

# 2. 탭 구성 (요청사항 반영)
tab1, tab2, tab3 = st.tabs(["👤 학생 명렬 및 행발 작성", "📚 독서 활동(ISBN) 점검", "🚫 기재 금지어 & 규정 검사"])

# -----------------------------------------------------------------------------
# TAB 1: 학생 명렬 및 행발 작성
# -----------------------------------------------------------------------------
with tab1:
    st.subheader("👤 학생 명렬표 업로드 및 행동특성 작성")
    st.write("엑셀(Excel)이나 CSV 명렬표를 업로드하여 학생별로 행발을 관리할 수 있습니다.")
    
    # 2026 양식 다운로드 버튼
    sample_data = pd.DataFrame({"번호": [1, 2, 3], "이름": ["홍길동", "이순신", "강감찬"], "행동특성 및 종합의견": ["", "", ""]})
    sample_csv = sample_data.to_csv(index=False).encode('utf-8-sig')
    st.download_button("📥 명렬표 양식 다운로드", data=sample_csv, file_name="개운중_명렬표_양식.csv", mime="text/csv")
    
    uploaded_file = st.file_uploader("명렬표 파일 업로드 (xlsx, csv 지원)", type=["xlsx", "csv"])
    
    if uploaded_file is not None:
        try:
            if uploaded_file.name.endswith('.csv'):
                df = pd.read_csv(uploaded_file)
            else:
                df = pd.read_excel(uploaded_file)
                
            if "이름" not in df.columns or "번호" not in df.columns:
                st.error("⚠️ 파일에 '번호'와 '이름' 컬럼이 포함되어 있는지 확인해 주세요.")
            else:
                if "행동특성 및 종합의견" not in df.columns:
                    df["행동특성 및 종합의견"] = ""
                
                # 학생 선택
                student_list = [f"{int(row['번호'])}번 {row['이름']}" for _, row in df.iterrows()]
                selected_student = st.selectbox("🎯 작성할 학생 선택:", student_list)
                
                idx = student_list.index(selected_student)
                current_text = df.at[idx, "행동특성 및 종합의견"] if pd.notna(df.at[idx, "행동특성 및 종합의견"]) else ""
                
                # 입력란
                input_text = st.text_area(f"✍️ {selected_student} 입력 (종결어미 '~함.', '~임.' 권장 / 특수문자 지양)", value=current_text, height=180)
                
                # 실시간 글자수 및 규정 점검
                char_count = len(input_text)
                
                # 2026 개정 반영: 행발 300자 제한
                if char_count > 300:
                    st.error(f"🚨 글자 수 초과! 현재 **{char_count}**자 / 최대 300자 (한글 기준)")
                else:
                    st.caption(f"📝 글자 수: **{char_count}**자 / 최대 300자 제한")
                
                # 금지어 실시간 점검
                found_forbidden = [word for word in FORBIDDEN_WORDS if word.lower() in input_text.lower()]
                if found_forbidden:
                    st.error(f"❌ 기재 금지어가 포함되어 있습니다: {', '.join(found_forbidden)}")
                
                if "~다." in input_text:
                    st.warning("⚠️ 서술형 항목은 명사형 어미('~함.', '~임.')로 종결할 것을 권장합니다.")
                    
                # 임시 저장
                if st.button("💾 해당 학생 내용 임시 저장"):
                    df.at[idx, "행동특성 및 종합의견"] = input_text
                    st.success(f"✅ {selected_student} 내용 반영 완료!")
                
                st.write("---")
                st.subheader("📊 전체 학급 작성 현황")
                st.dataframe(df, use_container_width=True)
                
                # 마스터 파일 다운로드
                final_csv = df.to_csv(index=False).encode('utf-8-sig')
                st.download_button(
                    label="📥 최종 작성본 다운로드 (나이스 복붙용)",
                    data=final_csv,
                    file_name="2026학년도_개운중_행발_작성완료.csv",
                    mime="text/csv"
                )
        except Exception as e:
            st.error(f"파일 처리 오류: {e}")

# -----------------------------------------------------------------------------
# TAB 2: 독서 ISBN 검색 및 규정
# -----------------------------------------------------------------------------
with tab2:
    st.subheader("📚 독서활동상황 등록 및 ISBN 검증")
    st.info("💡 **2026 개운중 지침 핵심:** 정기간행물 및 ISSN 도서는 입력 불가하며, **ISBN에 등재된 도서만** 입력할 수 있습니다. 책제목(저자) 형식 준수!")
    
    st.markdown("""
    > **💡 2026학년도 중복 기재 허용 개정 사항**
    > * 학생이 동일한 책을 반복하여 읽고 **동일하지 않은 증빙자료**를 제출하면 학년/학기/과목 상관없이 **중복 입력 가능**합니다.
    > * 단, 2026학년도 3학년이 이전 학년(1, 2학년)에 이미 입력된 내용 간에 중복이 발생해 있다면 그것은 정정대상(오류)입니다.
    """)
    
    query = st.text_input("🔍 검색할 도서명 또는 저자명을 입력하세요:")
    
    if query:
        # 국립중앙도서관 이외에 실제 연동이 필요할 경우 공공 API 인증키를 사용해 활용 가능합니다.
        # 현장 활용성을 위해 Mock 및 가이드 구조로 배치합니다.
        mock_results = [
            {"입력 포맷 예시": f"{query}(홍길동)", "구분": "ISBN 정상 등재 도서", "비고": "기재 가능"},
            {"입력 포맷 예시": f"교실 밖 {query}(강혜원 외)", "구분": "저자 3명 이상 예시", "비고": "기재 가능"}
        ]
        st.write("### 📋 도서 정보 검증 대조표 (예시)")
        st.table(pd.DataFrame(mock_results))
        
        # 언어 제한 필터링
        if any(char in query for char in ["#", "$", "%", "@"]):
            st.warning("⚠️ 특수문자, 문단 기호 및 번호 입력은 지양해 주세요.")

# -----------------------------------------------------------------------------
# TAB 3: 기재 금지어 & 규정 정밀 검사
# -----------------------------------------------------------------------------
with tab3:
    st.subheader("🚫 기재 금지사항 및 2026 신설 규정 딥-체크")
    st.write("작성하신 문장(세특, 창체, 행발 등)을 붙여넣으시면 2026 지침 위반 사항을 추적합니다.")
    
    # 지침 리마인드
    st.warning("""
    **🚨 2026년도 신설 중요 규정:** 
    AI(생성형 AI)를 활용하여 생성한 자료를 학교생활기록부 서술형 항목에 **그대로 입력하는 행위는 절대 금지**됩니다. 
    윤문 보조 수단으로 사용 시 반드시 실제 수행 여부와 유의사항을 철저히 교사가 확인해야 합니다.
    """)
    
    check_text = st.text_area("검사할 문단을 이곳에 붙여넣으세요 (Ctrl + V)", height=250, placeholder="검사 대상 텍스트 입력...")
    
    if check_text:
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 🔍 금지 키워드 검색 결과")
            detected = [word for word in FORBIDDEN_WORDS if word.lower() in check_text.lower()]
            
            if detected:
                st.error(f"발견된 금지 의심 단어: {len(detected)}개")
                highlighted = check_text
                for word in detected:
                    highlighted = highlighted.replace(word, f" 🔴**[{word}]**🔴 ")
                st.markdown(highlighted)
            else:
                st.success("✅ 지침상 금지된 키워드가 발견되지 않았습니다.")
                
        with col2:
            st.markdown("### 📋 2026 글자 수 축소 규정 및 서식 체크")
            
            # 날짜 패턴 간이 체크
            if any(etc in check_text for etc in ["2026.", "2026.03", "2026학년도"]):
                st.error("❌ **서술형 영역 전반에 걸쳐 날짜를 입력하지 않습니다.** (예: '2026.03.04.' 등 기재 금지)")
            else:
                st.success("✅ 날짜 표기 미포함 규칙 준수 중")
                
            # 외국어 표기 체크
            st.info("💡 **문자는 한글, 숫자는 아라비아 숫자** 입력이 원칙입니다. (일반화된 명사 CEO, PD, UCC, IT, AI 등 및 고유명사 도서명/저자명 외 영문/외국어 기재 주의)")

# 사이드바 (연수물 주요 일정 요약)
with st.sidebar:
    st.image("https://img.icons8.com/clouds/100/000000/teacher.png", width=80)
    st.header("📌 개운중 기재요령 가이드")
    st.caption("연수 일시: 2026.05.11. (교무기획부)")
    
    st.markdown("""
    ---
    ### 📝 2026 글자수 가이드
    * **행동특성 및 종합의견**: **300자** (500자에서 축소)
    * **진로활동 특기사항**: **500자** (700자에서 축소)
    * **봉사활동 실적 내용**: **250자** (실적별 50자)
    
    ### 🚨 필수 리마인드
    * **학생 작성 자료 제출물 인용 금지**: 서술형 항목 내용을 학생이 작성해 제출하도록 하는 행위 금지
    * **사전 열람 금지**: 당해 연도 종료 전 학생 및 학부모에게 서술형 항목 열람 절대 불가 (민원으로만 발급 가능)
    * **부정적 내용 기재 시**: 나이스에 반드시 1학기 2회 이상 **누가기록(근거자료)**을 작성해야 교사가 보호받을 수 있습니다.
    """)
