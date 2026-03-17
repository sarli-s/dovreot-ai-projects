# Database Schema - Cursor
- **Table**: `users`
- **Fields**: `id`, `email`, `created_at`
- **Note**: Encryption needed for the email field.

## Security & Guidelines
* **אזהרת אבטחה:** חובה להשתמש ב-MFA לכל גישת אדמין למערכת.
* **הנחיית פיתוח:** יש להשתמש ב-Conventional Commits בכל דחיפת קוד.
* **מגבלת שרת:** השרת יבצע ריסטארט אוטומטי בכל יום ב-03:00 לפנות בוקר.