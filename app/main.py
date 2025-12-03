import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.db import Base, engine
from app.api import employees, departments, leave_requests, leave_quotas, auth,salary_routes

# ----- Logging config -----
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s - %(message)s",
)
logger = logging.getLogger("hr_portal")
# ---------------------------

# ----- Logging config -----
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s - %(message)s",
)
logger = logging.getLogger("hr_portal")
# ---------------------------

# Create DB tables if they do not exist yet.
# In a real project you'd usually manage this via Alembic migrations instead.
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="HR Portal API",
    version="1.0.0",
)

# Configure CORS for your React frontend (adjust origins in real deployment).
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # e.g. ["http://localhost:3000"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount routers (paths match the earlier OpenAPI contract).
app.include_router(employees.router)
app.include_router(departments.router)
app.include_router(leave_requests.router)
app.include_router(leave_quotas.router)
app.include_router(auth.router)
app.include_router(salary_routes.router)


@app.get("/")
def read_root():
    return {"message": "HR Portal backend is running"}
