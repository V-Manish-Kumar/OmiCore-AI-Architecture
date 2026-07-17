import sys
import os
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

# Ensure root package directory is in python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from omnicore.parser.intent_parser import IntentParser, CompileError
from omnicore.ir.models import TaskIR, ExecutionDAG

app = FastAPI(
    title="OmniCore Task Compiler API",
    description="Compiler frontend API translating Natural Language requests to Task IR & Execution DAG structures.",
    version="0.1.0"
)

parser = IntentParser()

@app.get("/", response_class=HTMLResponse)
def serve_frontend():
    """Serves the compiler frontend HTML page."""
    html_path = os.path.join(os.path.dirname(__file__), "index.html")
    with open(html_path, "r", encoding="utf-8") as f:
        return f.read()

class ParseRequest(BaseModel):
    prompt: str

class ParseResponse(BaseModel):
    task_ir: TaskIR
    execution_dag: ExecutionDAG

@app.post("/parse", response_model=ParseResponse)
def parse_prompt(request: ParseRequest):
    """
    Compiles a natural language request into TaskIR and ExecutionDAG.
    """
    if not request.prompt.strip():
        raise HTTPException(status_code=400, detail="Prompt cannot be empty.")
    try:
        task_ir, execution_dag = parser.compile(request.prompt)
        return ParseResponse(task_ir=task_ir, execution_dag=execution_dag)
    except CompileError as ce:
        raise HTTPException(
            status_code=400,
            detail={
                "message": "Compilation failed",
                "errors": ce.errors
            }
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
