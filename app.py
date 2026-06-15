"""Prototype UI bằng Streamlit (DEMO NHANH, không phải Frontend chính thức).

Frontend chính thức = React ở frontend/. File này import trực tiếp core để chạy
offline khi chưa dựng API. Chạy: pip install streamlit && streamlit run app.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "backend"))

import streamlit as st  # noqa: E402

from app.core.faq.faq import answer  # noqa: E402
from app.core.rules.engine import allocation_50_30_20, evaluate_allocation  # noqa: E402
from app.core.rules.models import UserProfile  # noqa: E402

st.title("💰 BudgetBOT — Trợ lý ngân sách cá nhân (prototype)")
st.caption("Prototype nội bộ — Frontend chính thức là React. Chỉ tham khảo, không phải lời khuyên đầu tư.")

tab_faq, tab_plan = st.tabs(["Hỏi đáp", "Lập kế hoạch"])

with tab_faq:
    q = st.text_input("Hỏi về tài chính cá nhân:")
    if q:
        st.write(answer(q))

with tab_plan:
    income = st.number_input("Thu nhập/tháng", min_value=0.0, step=1_000_000.0)
    needs = st.number_input("Chi thiết yếu", min_value=0.0, step=1_000_000.0)
    wants = st.number_input("Chi mong muốn", min_value=0.0, step=1_000_000.0)
    savings = st.number_input("Tiết kiệm", min_value=0.0, step=1_000_000.0)
    if income > 0:
        st.subheader("Gợi ý 50/30/20")
        st.json(allocation_50_30_20(income))
        st.subheader("Đánh giá phân bổ hiện tại")
        st.json(evaluate_allocation(UserProfile(income, needs, wants, savings)))
