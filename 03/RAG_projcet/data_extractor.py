from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

# 1. הגדרת פריט: החלטה טכנית
class Decision(BaseModel):
    id: str
    title: str = Field(description="عنوان ההחלטה")
    summary: str = Field(description="תקציר ההחלטה שנבחרה")
    tags: List[str]
    observed_at: str = Field(description="תאריך זיהוי או קבלת ההחלטה")

# 2. הגדרת פריט: כלל/הנחיה
class Rule(BaseModel):
    id: str
    rule: str = Field(description="תוכן הכלל או ההנחיה")
    scope: str = Field(description="באילו רכיבים הכלל תקף (למשל UI, Backend)")
    observed_at: str = Field(description="תאריך הופעת הכלל")

# 3. הגדרת פריט: אזהרה
class WarningItem(BaseModel):
    id: str
    area: str = Field(description="אזור המערכת עליו יש אזהרה")
    message: str = Field(description="תוכן האזהרה")
    severity: str = Field(description="רמת חומרה: low, medium, high")

# 4. המבנה הכולל של ה-JSON (הסכימה הסופית)
class ExtractedProjectData(BaseModel):
    decisions: List[Decision]
    rules: List[Rule]
    warnings: List[WarningItem]