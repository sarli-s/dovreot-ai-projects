tools = [
    {
        "type": "function",
        "function": {
            "name": "add_task",
            "description": "הוספת משימה חדשה לרשימה",
            "parameters": {
                "type": "object",
                "properties": {
                    "title": {"type": "string", "description": "כותרת המשימה"},
                    "description": {"type": "string", "description": "תיאור נוסף"},
                    "task_type": {"type": "string", "description": "סוג המשימה (עבודה, אישי, וכו')"}
                },
                "required": ["title"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_tasks",
            "description": "שליפת רשימת משימות עם אפשרות לסינון",
            "parameters": {
                "type": "object",
                "properties": {
                    "status": {"type": "string", "description": "סינון לפי סטטוס (פתוח/בוצע)"},
                    "task_type": {"type": "string", "description": "סינון לפי סוג"}
                }
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "update_task",
            "description": "עדכון משימה קיימת",
            "parameters": {
                "type": "object",
                "properties": {
                    "task_id": {"type": "integer", "description": "מזהה המשימה"},
                    "status": {"type": "string", "description": "סטטוס חדש"},
                    "title": {"type": "string", "description": "כותרת חדשה"}
                },
                "required": ["task_id"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "delete_task",
            "description": "מחיקת משימה מהרשימה",
            "parameters": {
                "type": "object",
                "properties": {
                    "task_id": {"type": "integer", "description": "מזהה המשימה למחיקה"}
                },
                "required": ["task_id"]
            }
        }
    }
]