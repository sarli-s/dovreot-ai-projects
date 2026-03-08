import json
import os

# שם הקובץ שבו יישמרו המשימות
DB_FILE = "tasks_db.json"

def load_tasks():
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def save_tasks(tasks_list):
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(tasks_list, f, ensure_ascii=False, indent=4)

# טעינה ראשונית
tasks = load_tasks()

def add_task(title, description=None, task_type="כללי", start_date=None, end_date=None):
    global tasks
    new_id = max([t['id'] for t in tasks], default=0) + 1
    new_task = {
        "id": new_id,
        "title": title,
        "description": description,
        "type": task_type,
        "start_date": start_date,
        "end_date": end_date,
        "status": "פתוח"
    }
    tasks.append(new_task)
    save_tasks(tasks) # שמירה לקובץ
    return new_task

def get_tasks(status=None, task_type=None):
    global tasks
    tasks = load_tasks() # רענון מהקובץ
    print(f"DEBUG: טענתי מהקובץ: {len(tasks)} משימות")
    
    filtered = tasks
    if status:
        filtered = [t for t in filtered if t['status'] == status]
    if task_type:
        filtered = [t for t in filtered if t['type'] == task_type]
    return filtered

def update_task(task_id, status=None, title=None):
    global tasks
    tasks = load_tasks()
    for task in tasks:
        if task['id'] == int(task_id): # מוודא שזה מספר
            if status: task['status'] = status
            if title: task['title'] = title
            save_tasks(tasks)
            return {"message": "updated", "task": task}
    return {"error": "not found"}

def delete_task(task_id):
    global tasks
    tasks = load_tasks() # רענון מהקובץ
    
    # מחפשים אם המשימה קיימת לפני שמוחקים
    original_length = len(tasks)
    tasks = [t for t in tasks if t['id'] != int(task_id)]
    
    if len(tasks) < original_length:
        save_tasks(tasks) # שמירה של הרשימה החדשה (ללא המשימה שנמחקה)
        print(f"DEBUG: משימה {task_id} נמחקה בהצלחה.")
        return {"message": f"Task {task_id} deleted successfully"}
    else:
        print(f"DEBUG: משימה {task_id} לא נמצאה למחיקה.")
        return {"error": "Task not found"}