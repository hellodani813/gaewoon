import streamlit as st
import pandas as pd

st.set_page_config(
    page_title="Gaeun Assistant",
    page_icon="📝",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.title("🏫 개운중학교 생기부 작성 도우미")
st.write("PC와 스마트폰에서 실시간으로 맞춤법, 띄어쓰기, 기재 금지어를 점검할 수 있습니다.")

# 1. 생기부 기재 금지어 데이터베이스
FORBIDDEN_WORDS = [
    "토익", "TOEIC", "토플", "TOEFL", "텝스", "TEPS", "오픽", "OPIc", "HSK", "JLPT", "인증시험", "한자검정",
    "대회", "경시", "올림피아드", "시상", "수상경력", "교외상", "표창장", "감사장", "공로상",
    "논문", "학회지", "투고", "등재", "도서출판", "출간", "특허", "실용신안", "상표", "디자인출원",
    "어학연수", "해외 봉사", "해외 활동", "해외 여행",
    "아버지", "어머니", "부모", "친인척", "의사", "교수", "변호사", "검사", "대표", "사장",
    "장학생", "장학금", "대학명", "서울대", "연세대", "고려대", "카이스트", "영재교육원", "발명교실", "학원",
    "자격증", "취득", "방과후학교"
]

# 2. 나이스 자주 틀리는 맞춤법 및 띄어쓰기 사전 (오류 단어: (올바른 단어, 이유))
SPELL_CHECK_DICT = {
    "바라며": ("바라며", "정상"), 
    "바램": ("바람", "맞춤법 오류 ('바람'이 올바른 표현)"),
    "기대함": ("기대함", "정상"),
    "할수 ": ("할 수 ", "띄어쓰기 오류 ('할 v 수'로 띄어 써야 함)"),
    "있음": ("있음", "정상"),
    "잇음": ("있음", "맞춤법 오류 ('있음'이 올바른 표현)"),
    "나타남": ("나타남", "정상"),
    "나타남 ": ("나타남", "정상"),
    "가르침": ("가르침", "정상"),
    "가르치며": ("가르치며", "정상"),
    "가르켰": ("가르쳤", "단어 오용 ('손가락으로 가리키다'와 '지식을 가르치다' 구분)") ,
    "가리켰": ("가리켰", "정상"),
    "치루": ("치르", "맞춤법 오류 ('시험을 치르다/치렀다'가 올바른 표현)"),
    "맞추어": ("맞추어", "정상"),
    "마추어": ("맞추어", "맞춤법 오류 ('맞추다'가 올바른 표현)"),
    "돋보임": ("돋보임", "정상"),
    "돗보임": ("돋보임", "맞춤법 오류 ('돋보이다'가 올바른 표현)"),
    "연계하여": ("연계하여", "정상"),
    "연계 하역": ("연계하여", "정상"),
    "연계 하여": ("연계하여", "띄어쓰기 오류 ('연계하여'는 붙여 씀)"),
    "참여 하여": ("참여하여", "띄어쓰기 오류 ('참여하여'는 붙여 씀)"),
    "조사 하여": ("조사하여", "띄어쓰기 오류 ('조사하여'는 붙여 씀)"),
    "분석 하여": ("분석하여", "띄어쓰기 오류 ('분석하여'는 붙여 씀)"),
    "생각 함": ("생각함", "띄어쓰기 오류 ('생각함'은 붙여 씀)"),
    "않음": ("않음", "정상"),
    "안음": ("않음", "맞춤법 오류 ('하지 않음'은 '않음'으로 표기)"),
}

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
            "선택된 학생의 내용 입력창 (입력 시 실시간 검사가 하단에 표시됩니다)", 
            value=current_text, 
            height=180
        )
        
        #
