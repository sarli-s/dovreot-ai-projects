import streamlit as st
from agent_service import agent

# הגדרות דף הממשק
st.set_page_config(page_title="עוזר המשימות האישי שלי", page_icon="📝", layout="centered")

# עיצוב כותרת
st.title("🤖 ה-AI שיסדר לך את היום")
st.subheader("מה המשימה הבאה שלך?")

# יצירת היסטוריית שיחה (כדי שהצ'אט ייראה יפה)
if "messages" not in st.session_state:
    st.session_state.messages = []

# הצגת הודעות קודמות מההיסטוריה
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# תיבת קלט למשתמש (איפה שכותבים)
if prompt := st.chat_input("למשל: תוסיף לי משימה לקנות פרחים..."):
    # הוספת הודעת המשתמש למסך
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # שליחה ל-Agent וקבלת תשובה
    with st.chat_message("assistant"):
        with st.spinner("חושב..."):
            response = agent(prompt)
            st.markdown(response)
    
    # שמירת תשובת ה-AI בהיסטוריה
    st.session_state.messages.append({"role": "assistant", "content": response})

# פס צד (Sidebar) להסבר קצר
with st.sidebar:
    st.header("עזרה מהירה 💡")
    st.write("""
    אתה יכול להגיד לי:
    * 'תוסיף משימה לסיים את הפרויקט'
    * 'אילו משימות יש לי?'
    * 'תעדכן את משימה 1 לבוצע'
    * 'תמחק את משימה 2'
    """)
    if st.button("נקה היסטוריית שיחה"):
        st.session_state.messages = []
        st.rerun()