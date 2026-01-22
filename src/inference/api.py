"""
FastAPI Server - REST API for Code Generation
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.model.deepseek import CodeGenius

app = FastAPI(
    title="AI Code Genius API",
    description="DeepSeek Coder V2 tabanlı kod üretim API'si",
    version="1.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global model
genius = None


class CodeRequest(BaseModel):
    prompt: str
    max_tokens: int = 2048
    temperature: float = 0.7
    model_size: str = "6.7b"


class ProjectRequest(BaseModel):
    description: str
    tech_stack: List[str]
    features: List[str]
    architecture: str = "modular"
    model_size: str = "6.7b"


class RefactorRequest(BaseModel):
    code: str
    requirements: List[str]
    language: Optional[str] = None
    model_size: str = "6.7b"


class TestRequest(BaseModel):
    code: str
    framework: str = "pytest"
    coverage_target: int = 90
    model_size: str = "6.7b"


@app.on_event("startup")
async def startup_event():
    """Model yükle"""
    global genius
    genius = CodeGenius(model_size="6.7b", quantization="4bit")


@app.get("/")
async def root():
    return {
        "message": "AI Code Genius API",
        "version": "1.0.0",
        "endpoints": ["/generate", "/project", "/refactor", "/test"]
    }


@app.post("/generate")
async def generate_code(request: CodeRequest):
    """Kod üret"""
    try:
        code = genius.generate(
            prompt=request.prompt,
            max_tokens=request.max_tokens,
            temperature=request.temperature
        )
        
        return {
            "success": True,
            "code": code,
            "tokens": len(code.split())
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/project")
async def generate_project(request: ProjectRequest):
    """Proje üret"""
    try:
        files = genius.generate_project(
            description=request.description,
            tech_stack=request.tech_stack,
            features=request.features,
            architecture=request.architecture
        )
        
        return {
            "success": True,
            "files": files,
            "file_count": len(files)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/refactor")
async def refactor_code(request: RefactorRequest):
    """Kod iyileştir"""
    try:
        improved = genius.refactor(
            code=request.code,
            requirements=request.requirements,
            language=request.language
        )
        
        return {
            "success": True,
            "code": improved
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/test")
async def generate_tests(request: TestRequest):
    """Test üret"""
    try:
        tests = genius.generate_tests(
            code=request.code,
            framework=request.framework,
            coverage_target=request.coverage_target
        )
        
        return {
            "success": True,
            "tests": tests,
            "framework": request.framework
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
async def health_check():
    return {"status": "healthy", "model_loaded": genius is not None}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)