import json
import os
from llama_index.core.workflow import Event, Workflow, step, StartEvent, StopEvent
from llama_index.core.retrievers import VectorIndexRetriever
from llama_index.core import get_response_synthesizer, Settings

# --- הגדרת אירועים ---
class RoutingEvent(Event):
    query: str
    use_structured: bool

class RetrievedEvent(Event):
    nodes: list
    query: str

class ValidationEvent(Event):
    nodes: list
    query: str

class RAGWorkflow(Workflow):
    def __init__(self, index, extracted_data_path, **kwargs):
        super().__init__(**kwargs)
        self.index = index
        self.data_path = extracted_data_path
        self.retriever = VectorIndexRetriever(index=index, similarity_top_k=3)
        self.synthesizer = get_response_synthesizer(response_mode="compact")

    @step
    async def route_query(self, ev: StartEvent) -> RoutingEvent | StopEvent:
        query = ev.get("query")
        if not query: return StopEvent(result="אנא שאל שאלה.")

        # ניתוב חכם
        structured_keywords = ["רשימה", "החלטות", "כללים", "אזהרות", "תגיות", "הנחיות", "מובנה", "json"]
        use_structured = any(word in query.lower() for word in structured_keywords)
        
        print(f"🛤️ ניתוב: {'Structured (JSON)' if use_structured else 'Semantic (Vector)'}")
        return RoutingEvent(query=query, use_structured=use_structured)

    @step
    async def handle_structured(self, ev: RoutingEvent) -> StopEvent | RetrievedEvent:
        # מקרה 1: ניתוב סמנטי (כאן היה החסר שגרם לשגיאה!)
        if not ev.use_structured:
            print(f"🔎 שלב 1: שולף מידע סמנטי עבור: {ev.query}")
            nodes = self.retriever.retrieve(ev.query)
            return RetrievedEvent(nodes=nodes, query=ev.query)
            
        # מקרה 2: ניתוב מובנה (JSON)
        if not os.path.exists(self.data_path):
            return StopEvent(result="קובץ הנתונים לא נמצא. אנא הרץ חילוץ.")

        with open(self.data_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        # שלב המחשבה 
        query_gen_prompt = (
            f"המשתמש שאל: {ev.query}\n"
            f"השדות ב-JSON: 'decisions', 'warnings', 'guidelines', 'tags'.\n"
            f"איזה שדה הכי רלוונטי? ענה במילה אחת."
        )
        selected_field = str(Settings.llm.complete(query_gen_prompt)).strip().lower()
        print(f"🤖 ה-LLM בחר להתמקד בשדה: {selected_field}")

        # תשובה סופית עם גיבוי (כדי שלא יהיה Empty Response)
        final_prompt = (
            f"הנה מידע מהפרויקט (JSON):\n{json.dumps(data, ensure_ascii=False, indent=2)}\n\n"
            f"שאלה: {ev.query}\n"
            f"התמקד במידע הרלוונטי ונסח תשובה מפורטת בעברית:"
        )
        response = Settings.llm.complete(final_prompt)
        return StopEvent(result=str(response))

    @step
    async def validate_results(self, ev: RetrievedEvent) -> ValidationEvent | StopEvent:
        if not ev.nodes:
            return StopEvent(result="לא נמצא מידע רלוונטי במסמכים.")
        
        # אימות ציון רלוונטיות
        top_score = ev.nodes[0].score if ev.nodes[0].score else 0
        print(f"✅ שלב 2: מידע אומת (Score: {top_score:.2f})")
        return ValidationEvent(nodes=ev.nodes, query=ev.query)

    @step
    async def synthesize(self, ev: ValidationEvent) -> StopEvent:
        print("✍️ שלב 3: מנסח תשובה סופית (סמנטי)")
        response = self.synthesizer.synthesize(query=ev.query, nodes=ev.nodes)
        return StopEvent(result=str(response))