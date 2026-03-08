import requests

URL = "http://127.0.0.1:8001/chat"

def ask_ai(message):
    print(f"\n>> המשתמש: {message}")
    try:
        response = requests.post(URL, json={"message": message})
        if response.status_code == 200:
            print(f">> ה-AI ענה: {response.json()['response']}")
        else:
            print(f"!! שגיאה מהשרת ({response.status_code}): {response.text}")
    except Exception as e:
        print(f"!! תקלה בתקשורת: {e}")

# --- כאן את שולטת בטסטים (תורידי את ה-# מהשורה שאת רוצה להריץ) ---

# טסט 1: הוספת משימה
# ask_ai("תוסיף לי משימה לקנות פרחים לשבת")

# טסט 2: הצגת משימות (לוודא שהתווסף)
# ask_ai("אילו משימות יש לי?")

# טסט 3: עדכון משימה (בהנחה שה-ID הוא 1)
# ask_ai("תעדכן את משימה 1 לסטטוס 'בוצע'")

#טסט 4: בדיקה אם המשימה באמת עודכנה
# ask_ai("תציג לי את כל המשימות, כולל אלו שבוצעו")

# טסט 5: מחיקה
ask_ai("תמחק את משימה 1")