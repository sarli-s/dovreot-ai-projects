import json
from datetime import datetime
from pathlib import Path
from llama_index.core import SimpleDirectoryReader
from llama_index.core.program import LLMTextCompletionProgram
from src.core.schema import ExtractedProjectData
from src.core.settings import init_settings

class DataExtractor:
    def __init__(self):
        init_settings() # מוודא שה-LLM מוגדר
        self.prompt_template = (
            "אתה מומחה לניתוח מסמכי פרויקט. סרוק את הטקסט הבא וחלץ החלטות, כללים ואזהרות.\n"
            "השתמש במבנה הנתונים המדויק שהוגדר.\n"
            "טקסט:\n{text}\n"
        )
        self.program = LLMTextCompletionProgram.from_defaults(
            output_cls=ExtractedProjectData,
            prompt_template_str=self.prompt_template,
            verbose=True
        )

    def run_extraction(self, input_path: str, output_file: str):
        print(f"🔍 מתחיל סריקה בנתיב: {input_path}")
        reader = SimpleDirectoryReader(input_dir=input_path, recursive=True, required_exts=[".md"])
        documents = reader.load_data()
        
        final_data = ExtractedProjectData(generated_at=datetime.now().isoformat())

        for doc in documents:
            print(f"📄 מעבד קובץ: {doc.metadata.get('file_name')}")
            try:
                result = self.program(text=doc.text)
                final_data.decisions.extend(result.decisions)
                final_data.rules.extend(result.rules)
                final_data.warnings.extend(result.warnings)
            except Exception as e:
                print(f"⚠️ שגיאה בעיבוד קובץ: {e}")

        # שמירה ל-JSON
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(final_data.dict(), f, ensure_ascii=False, indent=4)
        print(f"✅ החילוץ הושלם! הנתונים נשמרו ב-{output_file}")