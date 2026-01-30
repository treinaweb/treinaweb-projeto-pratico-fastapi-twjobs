from fastapi import FastAPI

from twjobs.api.auth.router import router as auth_router
from twjobs.api.companies.router import router as companies_router
from twjobs.api.skills.router import router as skills_router

app = FastAPI()

app.include_router(skills_router, prefix="/api/skills")
app.include_router(auth_router, prefix="/api/auth")
app.include_router(companies_router, prefix="/api/companies")
