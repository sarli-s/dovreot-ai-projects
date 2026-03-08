from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import agent_service

# יצירת מופע של האפליקציה
app = FastAPI(title="AI Todo Agent API")

# הגדרת מבנה הנתונים שהשרת מצפה לקבל
class ChatRequest(BaseModel):
    message: str

@app.get("/")
def read_root():
    return {"status": "The AI Todo Agent is running!"}

@app.post("/chat")
async def chat(request: ChatRequest):
    """
    נקודת קצה שמקבלת טקסט חופשי, מעבירה ל-Agent ומחזירה תשובה אנושית
    """
    try:
        # קריאה לפונקציית ה-agent שבנינו בשלב 3
        response = agent_service.agent(request.message)
        return {"response": response}
    except Exception as e:
        # במקרה של שגיאה (למשל מפתח API לא תקין)
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    # הרצת השרת בפורט 8000
    print("🚀 השרת עולה בכתובת: http://127.0.0.1:8000")
    uvicorn.run(app, host="127.0.0.1", port=8001)