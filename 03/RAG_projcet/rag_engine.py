# import json
# import os
# from llama_index.core.workflow import Event, Workflow, step, StartEvent, StopEvent
# from llama_index.core.retrievers import VectorIndexRetriever
# from llama_index.core import get_response_synthesizer

# # --- הגדרת אירועים (Events) ---
# class RoutingEvent(Event):
#     query: str
#     use_structured: bool

# class RetrievedEvent(Event):
#     nodes: list
#     query: str

# class ValidationEvent(Event):
#     nodes: list
#     query: str

# # --- הגדרת ה-Workflow ---
# class RAGWorkflow(Workflow):
#     def __init__(self, index, extracted_data_path, **kwargs):
#         super().__init__(**kwargs)
#         self.index = index
#         self.data_path = extracted_data_path
#         self.retriever = VectorIndexRetriever(index=index, similarity_top_k=3)
#         self.synthesizer = get_response_synthesizer(response_mode="compact")

#     @step
#     async def route_query(self, ev: StartEvent) -> RoutingEvent | StopEvent:
#         query = ev.get("query")
        
#         # ולידציה בסיסית (ממה שהיה לנו קודם)
#         if not query or len(query.strip()) < 3:
#             return StopEvent(result="השאלה קצרה מדי. אנא נסי שוב.")

#         # לוגיקת ניתוב (שלב ג')
#         structured_keywords = ["רשימה", "כל ההחלטות", "אילו כללים", "אזהרות", "תגיות", "הנחיות"]
#         use_structured = any(word in query.lower() for word in structured_keywords)
        
#         print(f"🛤️ ניתוב: {'Structured (JSON)' if use_structured else 'Semantic (Vector)'}")
#         return RoutingEvent(query=query, use_structured=use_structured)

#     @step
#     async def handle_structured(self, ev: RoutingEvent) -> StopEvent | RetrievedEvent:
#         if not ev.use_structured:
#             # אם לא מובנה, שלח לשלב השליפה הסמנטית הרגיל (השלב הישן שלנו)
#             print(f"🔎 שלב 1: שולף מידע סמנטי עבור: {ev.query}")
#             nodes = self.retriever.retrieve(ev.query)
#             return RetrievedEvent(nodes=nodes, query=ev.query)
            
#         # טיפול במידע מובנה (שלב ג')
#         if not os.path.exists(self.data_path):
#             return StopEvent(result="קובץ הנתונים המובנים לא נמצא. אנא הרץ חילוץ.")
            
#         with open(self.data_path, "r", encoding="utf-8") as f:
#             data = json.load(f)
            
#         print(f"📊 שלב 1: שולף נתונים מה-JSON המובנה")
#         # LLM מנסח תשובה מה-JSON
#         prompt = f"מבוסס על ה-JSON הבא: {json.dumps(data, ensure_ascii=False)}\n ענה על השאלה: {ev.query}"
#         response = self.synthesizer.synthesize(query=ev.query, nodes=[], text_chunks=[prompt])
#         return StopEvent(result=str(response))

#     @step
#     async def validate_results(self, ev: RetrievedEvent) -> ValidationEvent | StopEvent:
#         # כאן נמצאת הוולידציה המקורית שלך!
#         if not ev.nodes:
#             return StopEvent(result="מצטער, לא מצאתי מידע רלוונטי בקבצי הפרויקט.")
        
#         top_score = ev.nodes[0].score if ev.nodes[0].score else 0
#         if top_score < 0.3:
#             print(f"⚠️ אזהרה: ציון דמיון נמוך ({top_score:.2f})")
#             # אפשר להחזיר StopEvent או להמשיך עם הערה - בואי נמשיך כרגע
            
#         print(f"✅ שלב 2: המידע אומת (Score: {top_score:.2f})")
#         return ValidationEvent(nodes=ev.nodes, query=ev.query)

#     @step
#     async def synthesize(self, ev: ValidationEvent) -> StopEvent:
#         # ניסוח התשובה הסמנטית המקורית שלך
#         print("✍️ שלב 3: מנסח תשובה סופית (Semantic)")
#         response = self.synthesizer.synthesize(query=ev.query, nodes=ev.nodes)
#         return StopEvent(result=str(response))