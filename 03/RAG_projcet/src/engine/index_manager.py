import os
from pathlib import Path
from llama_index.core import (
    SimpleDirectoryReader, VectorStoreIndex, 
    StorageContext, load_index_from_storage
)

def get_index():
    # החזרת פונקציית ה-Metadata המקורית שלך
    def file_metadata(file_path):
        if ".cursor" in file_path: return {"tool": "Cursor"}
        elif ".claude" in file_path: return {"tool": "Claude Code"}
        return {"tool": "General"}

    # נתיבים (מעודכנים למבנה החדש - עולים תיקייה אחת למעלה ל-Root)
    BASE_DIR = Path(__file__).resolve().parent.parent.parent
    mock_path = BASE_DIR.parent / "agentic_project_mock"
    PERSIST_DIR = BASE_DIR / "data" / "storage"

    if not os.path.exists(PERSIST_DIR):
        print("Creating new index...")
        input_dirs = [
            str(mock_path / ".cursor"),
            str(mock_path / ".claude"),
            str(mock_path / "docs")
        ]
        
        documents = []
        for folder in input_dirs:
            if os.path.exists(folder):
                reader = SimpleDirectoryReader(
                    input_dir=folder, 
                    file_metadata=file_metadata,
                    exclude_hidden=False
                )
                documents.extend(reader.load_data())
        
        # כאן הוא משתמש אוטומטית ב-SentenceSplitter מה-Settings
        index = VectorStoreIndex.from_documents(documents)
        index.storage_context.persist(persist_dir=str(PERSIST_DIR))
        return index
    else:
        storage_context = StorageContext.from_defaults(persist_dir=str(PERSIST_DIR))
        return load_index_from_storage(storage_context)