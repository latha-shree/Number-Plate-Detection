import streamlit as st

st.title("🚘 Number Plate Detection System")

st.write("Choose an option:")

col1, col2 = st.columns(2)

with col1:
    if st.button("1️⃣ Upload Image"):
        st.session_state['page'] = 'upload'

with col2:
    if st.button("2️⃣ Real-Time Capture"):
       st.session_state['page'] = 'realtime'

page = st.session_state.get('page', None)

if page == 'upload':
    import drag
    drag.app()

elif page == 'realtime':
  import num2
  num2.app()
