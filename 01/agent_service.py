import os
import json
from groq import Groq
from dotenv import load_dotenv
import todo_service
from tools_module import tools

# טעינת משתני הסביבה
load_dotenv()

api_key = os.getenv("GROQ_API_KEY")

if not api_key:
    raise ValueError("לא נמצא GROQ_API_KEY בקובץ .env!")

client = Groq(api_key=api_key)

def agent(query):
    # System Message מעודכן וקשוח כדי למנוע את טעויות ה-JSON והקישורים
    messages = [
        {
            "role": "system", 
            "content":"""אתה עוזר אישי אדיב לניהול משימות בעברית.
            1. כשאתה משתמש בכלים (tools), הקפד לשלוח ארגומנטים בפורמט JSON תקין בלבד (למשל task_id כמספר).
            2. לאחר שקיבלת את התוצאה מהכלי, נסח תשובה אנושית, ברורה ומנומסת בעברית למשתמש.
            3. אל תציג למשתמש סוגריים מסולסלים {} או פורמט JSON בתשובה הסופית שלך.
            דוגמה: במקום להראות JSON, אמור: 'הוספתי לך את המשימה: קניית פרחים'."""ךם
        },
        {"role": "user", "content": query}
    ]

    # שימוש במודל יציב שתומך ב-Tools (versatile)
    chat_completion = client.chat.completions.create(
        model="llama-3.3-70b-versatile", 
        messages=messages,
        tools=tools,
        tool_choice="auto"
    )
    
    message = chat_completion.choices[0].message
    tool_calls = message.tool_calls

    if tool_calls:
        messages.append(message)
        
        for tool_call in tool_calls:
            function_name = tool_call.function.name
            
            try:
                # טעינת הארגומנטים
                args = json.loads(tool_call.function.arguments) if tool_call.function.arguments else {}
                if args is None:
                    args = {}
            except Exception:
                args = {}

            # ניקוי ערכים ריקים
            clean_args = {k: v for k, v in args.items() if v is not None and v != ""}

            # הפעלת הפונקציות
            if function_name == "add_task":
                result = todo_service.add_task(**clean_args)
            elif function_name == "get_tasks":
                result = todo_service.get_tasks(**clean_args)
            elif function_name == "update_task":
                if "task_id" in clean_args: 
                    clean_args["task_id"] = int(str(clean_args["task_id"]).strip())
                result = todo_service.update_task(**clean_args)
            elif function_name == "delete_task":
                if "task_id" in clean_args: 
                    clean_args["task_id"] = int(str(clean_args["task_id"]).strip())
                result = todo_service.delete_task(**clean_args)
            else:
                result = {"error": "Unknown function"}

            # תיקון שגיאת הכתיב כאן (הוספת פסיק לפני ensure_ascii)
            messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "name": function_name,
                "content": json.dumps(result, ensure_ascii=False)
            })

        # פנייה שנייה לקבלת התשובה הסופית
        final_response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=messages
        )
        return final_response.choices[0].message.content

    return message.content