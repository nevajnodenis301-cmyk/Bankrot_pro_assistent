from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from config import settings
from routers import cases, creditors, debts, documents, ai, children, income, properties, transactions

# Initialize rate limiter
limiter = Limiter(key_func=get_remote_address, default_limits=["100/minute"])

app = FastAPI(
    title="Банкрот ПРО API",
    description="API для системы управления делами по банкротству физических лиц (127-ФЗ)",
    version="1.0.0",
)

# Add rate limiter to app state
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(cases.router)
app.include_router(creditors.router)
app.include_router(debts.router)
app.include_router(documents.router)
app.include_router(ai.router)
# GROUP 1: Family & Employment
app.include_router(children.router)
app.include_router(income.router)
# GROUP 2: Property & Transactions
app.include_router(properties.router)
app.include_router(transactions.router)


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
