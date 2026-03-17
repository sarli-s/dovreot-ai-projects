import gradio as gr
import asyncio

def create_ui(workflow_runner):
    """
    יוצר את ממשק ה-Gradio.
    """
    
    async def chat_wrapper(user_question, history):
        # הפעלת ה-Workflow
        result = await workflow_runner(user_question)
        return str(result)

    # הסרנו את theme="soft" כדי למנוע את ה-TypeError
    demo = gr.ChatInterface(
        fn=chat_wrapper,
        title="🤖 Agentic RAG - Multi-Layer Architecture",
        description=(
            "מערכת RAG מתקדמת מבוססת אירועים (Event-Driven).\n"
            "המערכת יודעת לנתב בין חיפוש סמנטי לחילוץ נתונים מובנים (JSON)."
        ),
        examples=["מה הצבע הכללי של המערכת?", "תן לי רשימה של כל ההחלטות הטכניות", "אילו אזהרות קיימות?"]
    )
    
    return demo