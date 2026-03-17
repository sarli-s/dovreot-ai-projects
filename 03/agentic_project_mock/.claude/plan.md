# Development Plan - Claude Code
## Task: Database Migration (Update Feb 2026)
- **Change**: Added `supplier_id` to the `products` table.
- **Removed**: The `legacy_tag` field was removed from all tables.
- **Constraint**: Foreign key constraints added between products and suppliers.
- **Status**: Completed.

## החלטות אסטרטגיות - מרץ 2026
* נבחר להשתמש ב-Groq כספק ה-LLM העיקרי בגלל המהירות.
* הוחלט ששפת הממשק ברירת המחדל תהיה עברית.
* תאריך היעד להשקת גרסת הבטא: 01.05.2026.