from pydantic import BaseModel, Field
from typing import List, Optional

# --- פריטי המידע לחילוץ (שלב ג') ---

class Decision(BaseModel):
    """מייצג החלטה טכנית או ארכיטקטונית שהתקבלה בפרויקט"""
    id: str = Field(description="מזהה ייחודי (למשל dec-001)")
    title: str = Field(description="כותרת קצרה של ההחלטה")
    summary: str = Field(description="תמצית ההחלטה והסיבה לה")
    tags: List[str] = Field(default_factory=list, description="תגיות נושא (db, ui, auth)")
    observed_at: str = Field(description="תאריך/זמן כפי שמופיע במסמך")

class Rule(BaseModel):
    """מייצג כלל עבודה, הנחיית פיתוח או קוד התנהגות"""
    id: str = Field(description="מזהה ייחודי (למשל rule-001)")
    rule: str = Field(description="תוכן ההנחיה או הכלל")
    scope: str = Field(description="היקף היישום (למשל 'כל המערכת', 'Frontend בלבד')")
    observed_at: str = Field(description="תאריך זיהוי הכלל")

class WarningItem(BaseModel):
    """מייצג אזהרה, סיכון או אזור רגיש בקוד שצריך לשים לב אליו"""
    id: str = Field(description="מזהה ייחודי (למשל warn-001)")
    area: str = Field(description="הרכיב המושפע מהאזהרה")
    message: str = Field(description="פירוט האזהרה")
    severity: str = Field(description="רמת חומרה (low, medium, high)")

# --- המבנה הכולל של ה-JSON הסופי ---

class ExtractedProjectData(BaseModel):
    """האובייקט המרכז את כל המידע המובנה שחולץ מהפרויקט"""
    decisions: List[Decision] = Field(default_factory=list)
    rules: List[Rule] = Field(default_factory=list)
    warnings: List[WarningItem] = Field(default_factory=list)
    generated_at: str = Field(description="זמן יצירת הקובץ")