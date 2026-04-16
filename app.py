import streamlit as st

from ui_pages import (
    init_user_state,
    inject_global_styles,
    login_view,
    sidebar_panel,
    home_page,
    planner_page,
    history_page,
    profile_page,
    downloads_page,
)

st.set_page_config(
    page_title="Smart Revision Planner",
    page_icon="📚",
    layout="wide"
)

init_user_state()
inject_global_styles()

if not st.session_state.logged_in:
    login_view()
else:
    sidebar_panel()

    if st.session_state.current_page == "Home":
        home_page()
    elif st.session_state.current_page == "Planner":
        planner_page()
    elif st.session_state.current_page == "History":
        history_page()
    elif st.session_state.current_page == "Profile":
        profile_page()
    elif st.session_state.current_page == "Downloads":
        downloads_page()
