import streamlit as st
import sqlite3

def login_page():
    st.title("Login")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        conn = sqlite3.connect("database/cms.db")
        cur = conn.cursor()

        cur.execute(
            "SELECT id, name, role FROM users WHERE name=? AND password=?",
            (username, password)
        )

        user = cur.fetchone()
        conn.close()

        if user:
            st.session_state["user_id"] = user[0]
            st.session_state["user_name"] = user[1]
            st.session_state["user_role"] = user[2]
            st.success(f"Welcome {user[1]}")
            st.rerun()
        else:
            st.error("Invalid username or password")
