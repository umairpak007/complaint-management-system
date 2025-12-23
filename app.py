# import sqlite3
# sqlite3.connect("database/cms.db")
# conn = sqlite3.connect("database/cms.db")
# print("database connection established")
# conn.close()
#
# import streamlit as st
# st.set_page_config(page_title="Complaint Management System")
# st.subheader("python final project")
# st.success("system started successfully")

#crate table
from services.models import create_tables
create_tables()

#add password column
from services.models import add_password_column
add_password_column()

#login user
import streamlit as st
from pages.login import login_page

st.set_page_config(page_title="Complaint Management System")

if "user_role" not in st.session_state:
    login_page()
else:
    st.sidebar.success(f"Logged in as {st.session_state['user_name']}")
    st.write("Dashboard coming next...")


