import os
import sys
import asyncio
from pathlib import Path

# הוספת נתיב הפרויקט
current_dir = Path(__file__).resolve().parent
sys.path.append(str(current_dir))

from src.core.settings import init_settings
from src.engine.index_manager import get_index
from src.engine.extractor import DataExtractor
from src.engine.workflow import RAGWorkflow
from src.ui.interface import create_ui

# ניסיונות ייבוא לכלי הציור
try:
    from llama_index.utils.workflow import draw_all_possible_flows
except ImportError:
    try:
        from llama_index.core.workflow.utils import draw_all_possible_flows
    except ImportError:
        draw_all_possible_flows = None

def main():
    print("🌟 Starting Agentic RAG System...")
    
    # 1. אתחול הגדרות ומודלים
    init_settings()
    
    # 2. טעינת אינדקס וקטורי (Semantic)
    index = get_index()
    
    # 3. טיפול בנתונים מובנים (JSON Extraction)
    os.makedirs("data", exist_ok=True)
    extracted_data_path = "data/extracted_data.json"
    
    if not os.path.exists(extracted_data_path):
        print("💡 JSON נתונים לא נמצא. מחלץ נתונים מהקבצים...")
        extractor = DataExtractor()
        mock_path = "../agentic_project_mock" 
        if os.path.exists(mock_path):
            extractor.run_extraction(input_path=mock_path, output_file=extracted_data_path)
        else:
            print(f"⚠️ נתיב ה-Mock לא נמצא ב-{mock_path}")

    # 4. הקמת ה-Workflow
    workflow = RAGWorkflow(index=index, extracted_data_path=extracted_data_path)
    
    # --- יצירת תרשים זרימה אמיתי לפי דרישת המורה ---
    if draw_all_possible_flows:
        try:
            print("📊 מייצר תרשים זרימה של ה-Workflow...")
            # שולחים את workflow (האובייקט) כדי למנוע שגיאת positional argument
            draw_all_possible_flows(workflow, filename="workflow_graph.html")
            print("✅ התרשים נוצר בהצלחה: workflow_graph.html")
        except Exception as e:
            print(f"⚠️ הערה: לא ניתן היה לייצר תרשים אוטומטי: {e}")
    else:
        print("ℹ️ פונקציית הציור לא זמינה בסביבה זו.")

    # 5. פונקציית הרצת הלוגיקה עבור הממשק
    async def run_logic(query):
        try:
            return await workflow.run(query=query)
        except Exception as e:
            return f"שגיאה בהרצת השאילתה: {str(e)}"

    # 6. הרצת הממשק (Gradio)
    print("🚀 מפעיל את ממשק המשתמש בכתובת http://127.0.0.1:7861")
    ui = create_ui(run_logic)
    
    ui.launch(server_name="127.0.0.1", server_port=7861, share=False)

if __name__ == "__main__":
    main()