import os
import httpx
import gradio as gr
from groq import Groq
import pandas as pd
from dotenv import load_dotenv

# טעינת משתני סביבה מה-.env
load_dotenv()

# הגדרת הלקוח עם ביטול אימות SSL (הפתרון שעבד לחברה שלך)
http_client = httpx.Client(verify=False)

client = Groq(
    api_key=os.environ.get("GROQ_API_KEY"),
    http_client=http_client
)

def load_system_prompt(filepath):
    """טוען את הפרומפט מתוך קובץ Markdown"""
    try:
        with open(filepath, 'r', encoding='utf-8') as file:
            return file.read()
    except FileNotFoundError:
        return "You are a PowerShell expert. Convert input to commands."

# טעינת התוכן מהקובץ שלך
SYSTEM_PROMPT_CONTENT = load_system_prompt("prompts/three.md")

def translate_to_cli(user_input):
    if not user_input.strip():
        return ""
        
    try:
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT_CONTENT},
                {"role": "user", "content": user_input}
            ],
            temperature=0
        )
        return completion.choices[0].message.content
    except Exception as e:
        return f"שגיאה: {str(e)}"

# ממשק המשתמש (Gradio)
with gr.Blocks(theme=gr.themes.Soft(), title="CLI Agent") as demo:
    gr.Markdown("# 🤖 PowerShell AI Agent (Groq Edition)")
    gr.Markdown("הסוכן משתמש במודל Llama 3 כדי לייצר פקודות בטוחות.")
    
    with gr.Row():
        txt_in = gr.Textbox(
            label="מה תרצה לבצע? (עברית/אנגלית)", 
            placeholder="למשל: תציג את כל התיקיות בכונן C",
            lines=2
        )
    
    btn = gr.Button("צור פקודה", variant="primary")
    
    # שימוש ברכיב Code לתצוגה יפה
    txt_out = gr.Code(label="פקודת PowerShell", language="shell")
    
    btn.click(fn=translate_to_cli, inputs=txt_in, outputs=txt_out)


def process_excel_file(file):
    """פונקציה חדשה שקוראת אקסל ומריצה את המודל על כל שורה"""
    try:
        # טעינת הקובץ (Gradio מעביר אובייקט קובץ)
        df = pd.read_excel(file.name)
        
        if 'Input' not in df.columns:
            return None, "שגיאה: הקובץ חייב להכיל עמודה בשם 'Input'"

        # הרצת המודל על כל שורה בעמודת ה-Input
        # אנחנו משתמשים בפונקציה הקיימת שלך translate_to_cli
        df['Output'] = df['Input'].apply(translate_to_cli)
        
        # יצירת נתיב לקובץ התוצאות
        output_path = "test_results_filled.xlsx"
        df.to_excel(output_path, index=False)
        
        return output_path, "הקובץ עובד בהצלחה!"
    except Exception as e:
        return None, f"שגיאה בעיבוד הקובץ: {str(e)}"
    
# --- ממשק המשתמש (Gradio) המעודכן ---
with gr.Blocks(theme=gr.themes.Soft(), title="CLI Agent") as demo:
    gr.Markdown("# 🤖 PowerShell AI Agent (Groq Edition)")
    
    with gr.Tab("פקודה בודדת"): # לשונית לממשק הקיים
        txt_in = gr.Textbox(label="מה תרצה לבצע?", lines=2)
        btn = gr.Button("צור פקודה", variant="primary")
        txt_out = gr.Code(label="פקודת PowerShell", language="shell")
        btn.click(fn=translate_to_cli, inputs=txt_in, outputs=txt_out)

    with gr.Tab("בדיקת קובץ (Bulk)"): # לשונית חדשה לבדיקת ה-15 תרחישים
        gr.Markdown("העלי קובץ Excel עם עמודת 'Input' כדי להריץ בדיקה המונית.")
        file_input = gr.File(label="העלי קובץ אקסל")
        run_bulk_btn = gr.Button("הריצי בדיקות על כל הקובץ")
        file_output = gr.File(label="הורידי תוצאות")
        status_text = gr.Textbox(label="סטטוס")
        
        run_bulk_btn.click(
            fn=process_excel_file, 
            inputs=file_input, 
            outputs=[file_output, status_text]
        )

if __name__ == "__main__":
    print("Starting server on http://127.0.0.1:7860")
    demo.launch()