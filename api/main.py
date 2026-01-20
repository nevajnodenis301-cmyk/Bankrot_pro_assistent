from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import cases, creditors, documents, ai

app = FastAPI(
    title="Банкрот ПРО API",
    description="API для системы управления делами по банкротству физических лиц (127-ФЗ)",
    version="1.0.0",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(cases.router)
app.include_router(creditors.router)
app.include_router(documents.router)
app.include_router(ai.router)


@app.get("/")
async def root():
    return {
        "message": "Банкрот ПРО API",
        "version": "1.0.0",
        "docs": "/docs",
    }


@app.get("/health")
async def health():
    return {"status": "ok"}
