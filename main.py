import io
import json
import re
from dataclasses import dataclass
from typing import Any

import pandas as pd
import streamlit as st


REQUIRED_COLUMNS = ["번호", "성명", "학년", "세부능력 및 특기사항"]

COLUMN_ALIASES = {
    "번호": ["번호", "학번", "순번", "No", "NO"],
    "성명": ["성명", "이름", "학생명", "학생 성명"],
    "학년": ["학년", "학년명"],
    "세부능력 및 특기사항": [
        "세부능력 및 특기사항",
        "세부능력및특기사항",
        "세특",
        "과목별 세부능력 및 특기사항",
        "과목별세부능력및특기사항",
    ],
}

DEFAULT_RULES: dict[str, dict[str, Any]] = {
    "2024": {
        "max_chars": 1500,
        "max_bytes": 4500,
        "caution_words": [
            "최고", "완벽", "천재", "영재", "전교", "등수", "1등", "꼴찌",
            "부모", "아버지", "어머니", "엄마", "아빠", "가정형편", "경제적",
            "종교", "정치", "장애", "질병", "우울",
        ],
        "replace_map": {"최고": "뛰어난", "완벽": "충실", "천재": "높은 이해도를 보이는 학생", "꼴찌": "학습 보완이 필요한"},
    },
    "2025": {
        "max_chars": 1500,
        "max_bytes": 4500,
        "caution_words": [
            "최고", "완벽", "천재", "영재", "전교", "등수", "1등", "꼴찌",
            "부모", "아버지", "어머니", "엄마", "아빠", "가정형편", "경제적",
            "종교", "정치", "장애", "질병", "우울", "진단", "상담",
        ],
        "replace_map": {"최고": "우수한", "완벽": "안정적인", "천재": "빠른 이해를 보이는 학생", "진단": "관찰"},
    },
    "2026": {
        "max_chars": 1500,
        "max_bytes": 4500,
        "caution_words": [
            "최고", "완벽", "천재", "영재", "전교", "등수", "1등", "꼴찌",
            "부모", "아버지", "어머니", "엄마", "아빠", "가정형편", "경제적",
            "종교", "정치", "장애", "질병", "우울", "진단", "상담", "치료",
        ],
        "replace_map": {"최고": "돋보이는", "완벽": "완성도 높은", "천재": "깊이 있게 이해하는 학생", "치료": "지원"},
    },
}


@dataclass
class CheckResult:
    status: str
    severity: str
    messages: list[str]
    suggestion: str
    char_count: int
    byte_count: int


def normalize_column_name(value: Any) -> str:
    return re.sub(r"\s+", "", str(value).strip()).lower()


def build_column_mapping(columns: list[str]) -> dict[str, str]:
    normalized_columns = {normalize_column_name(col): col for col in columns}
    mapping = {}
    for required, aliases in COLUMN_ALIASES.items():
        for alias in aliases:
            found = normalized_columns.get(normalize_column_name(alias))
            if found:
                mapping[required] = found
                break
    return mapping


def load_rule_profile(year: str, uploaded_rules: Any) -> dict[str, Any]:
    rules = DEFAULT_RULES.get(year, DEFAULT_RULES["2026"]).copy()
    if uploaded_rules is None:
        return rules
    try:
        custom_rules = json.load(uploaded_rules)
    except json.JSONDecodeError as exc:
        st.warning(f"규칙 파일을 읽지 못했습니다. 기본 규칙을 사용합니다. ({exc})")
        return rules
    rules.update(custom_rules)
    return rules


def clean_text(text: Any) -> str:
    if pd.isna(text):
        return ""
    text = str(text)
    text = re.sub(r"\s+", " ", text)
    text = re.sub(r"\s+([,.!?])", r"\1", text)
    return text.strip()


def apply_replacements(text: str, replace_map: dict[str, str]) -> str:
    suggestion = text
    for source, target in replace_map.items():
        suggestion = suggestion.replace(source, target)
    return suggestion


def check_record(row: pd.Series, rules: dict[str, Any], text_column: str, name_column: str) -> CheckResult:
    original_text = "" if pd.isna(row[text_column]) else str(row[text_column])
    text = clean_text(original_text)
    student_name = "" if pd.isna(row[name_column]) else str(row[name_column]).strip()
    messages: list[str] = []
    severity = "정상"

    char_count = len(text)
    byte_count = len(text.encode("utf-8"))
    max_chars = int(rules.get("max_chars", 1500))
    max_bytes = int(rules.get("max_bytes", 4500))
    caution_words = [str(word).strip() for word in rules.get("caution_words", []) if str(word).strip()]
    replace_map = {str(k): str(v) for k, v in rules.get("replace_map", {}).items()}

    if not text:
        messages.append("세부능력 및 특기사항이 비어 있습니다.")
        severity = "높음"
    if char_count > max_chars:
        messages.append(f"글자 수가 기준({max_chars}자)을 초과했습니다.")
        severity = "높음"
    if byte_count > max_bytes:
        messages.append(f"UTF-8 바이트 수가 기준({max_bytes}byte)을 초과했습니다.")
        severity = "높음"

    found_words = [word for word in caution_words if word in text]
    if found_words:
        messages.append("주의 표현 확인 필요: " + ", ".join(found_words))
        if severity != "높음":
            severity = "중간"

    if student_name and student_name in text:
        messages.append("본문에 학생 성명이 포함되어 있습니다. 필요 여부를 확인하세요.")
        if severity == "정상":
            severity = "낮음"

    if re.search(r"\d{2,3}-\d{3,4}-\d{4}", text):
        messages.append("전화번호로 보이는 개인정보가 포함되어 있습니다.")
        severity = "높음"
    if re.search(r"\d{6}-\d{7}", text):
        messages.append("주민등록번호 형태의 개인정보가 포함되어 있습니다.")
        severity = "높음"
    if "\n" in original_text or "\r" in original_text:
        messages.append("줄바꿈이 포함되어 있습니다. 입력 형식에 맞게 한 문단으로 정리하세요.")
        if severity == "정상":
            severity = "낮음"

    suggestion = apply_replacements(text, replace_map)
    status = "통과" if not messages else "검토 필요"
    return CheckResult(status, severity, messages, suggestion, char_count, byte_count)


def make_result_workbook(df: pd.DataFrame) -> bytes:
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="점검결과")
        worksheet = writer.sheets["점검결과"]
        for column_cells in worksheet.columns:
            max_length = max(len(str(cell.value or "")) for cell in column_cells)
            worksheet.column_dimensions[column_cells[0].column_letter].width = min(max(max_length + 2, 10), 60)
    return output.getvalue()


def main() -> None:
    st.set_page_config(page_title="생기부 세특 점검", page_icon="✓", layout="wide")
    st.title("생기부 세특 점검")
    st.caption("엑셀 파일의 번호, 성명, 학년, 세부능력 및 특기사항을 읽어 연도별 규칙으로 점검하고 수정 제안을 만듭니다.")

    with st.sidebar:
        st.header("점검 기준")
        year = st.selectbox("적용 연도", sorted(DEFAULT_RULES.keys(), reverse=True))
        uploaded_rules = st.file_uploader("사용자 규칙 JSON", type=["json"])
        rules = load_rule_profile(year, uploaded_rules)
        max_chars = st.number_input("최대 글자 수", min_value=100, max_value=3000, value=int(rules["max_chars"]))
        max_bytes = st.number_input("최대 바이트 수", min_value=300, max_value=9000, value=int(rules["max_bytes"]))
        caution_text = st.text_area("주의 표현", value=", ".join(rules.get("caution_words", [])), height=140)
        rules["max_chars"] = max_chars
        rules["max_bytes"] = max_bytes
        rules["caution_words"] = [word.strip() for word in caution_text.split(",") if word.strip()]

    uploaded_file = st.file_uploader("점검할 엑셀 파일 업로드", type=["xlsx", "xls"])
    if uploaded_file is None:
        st.info("엑셀 파일을 올리면 점검 결과가 이곳에 표시됩니다.")
        with st.expander("사용자 규칙 JSON 예시"):
            st.code(json.dumps({"max_chars": 1500, "max_bytes": 4500, "caution_words": ["최고", "등수", "개인정보"], "replace_map": {"최고": "우수한"}}, ensure_ascii=False, indent=2), language="json")
        return

    try:
        df = pd.read_excel(uploaded_file)
    except Exception as exc:
        st.error(f"엑셀 파일을 읽지 못했습니다. 파일 형식을 확인해 주세요. ({exc})")
        return

    if df.empty:
        st.warning("업로드한 엑셀 파일에 데이터가 없습니다.")
        return

    column_mapping = build_column_mapping(list(df.columns))
    missing_columns = [col for col in REQUIRED_COLUMNS if col not in column_mapping]
    if missing_columns:
        st.error("필수 열을 찾지 못했습니다: " + ", ".join(missing_columns))
        st.write("현재 파일의 열:", ", ".join(map(str, df.columns)))
        return

    text_column = column_mapping["세부능력 및 특기사항"]
    name_column = column_mapping["성명"]
    checked_rows = []
    for _, row in df.iterrows():
        result = check_record(row, rules, text_column, name_column)
        checked_rows.append({
            "점검상태": result.status,
            "위험도": result.severity,
            "점검결과": "\n".join(result.messages) if result.messages else "특이사항 없음",
            "수정제안": result.suggestion,
            "글자수": result.char_count,
            "바이트수": result.byte_count,
        })

    result_df = pd.concat([df.reset_index(drop=True), pd.DataFrame(checked_rows)], axis=1)
    total_count = len(result_df)
    needs_review = int((result_df["점검상태"] == "검토 필요").sum())
    high_risk = int((result_df["위험도"] == "높음").sum())

    metric_cols = st.columns(3)
    metric_cols[0].metric("전체", f"{total_count:,}건")
    metric_cols[1].metric("검토 필요", f"{needs_review:,}건")
    metric_cols[2].metric("높은 위험도", f"{high_risk:,}건")

    filter_value = st.radio("보기", ["전체", "검토 필요", "통과"], horizontal=True)
    visible_df = result_df if filter_value == "전체" else result_df[result_df["점검상태"] == filter_value]
    st.dataframe(visible_df, use_container_width=True, hide_index=True)

    excel_bytes = make_result_workbook(result_df)
    st.download_button(
        "점검 결과 엑셀 다운로드",
        data=excel_bytes,
        file_name=f"생기부_세특_점검결과_{year}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        type="primary",
    )


if __name__ == "__main__":
    main()
