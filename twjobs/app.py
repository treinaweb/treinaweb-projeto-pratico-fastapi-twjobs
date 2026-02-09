from fastapi import FastAPI

from twjobs.api.applications.router import router as applications_router
from twjobs.api.auth.router import router as auth_router
from twjobs.api.candidates.router import router as candidates_router
from twjobs.api.companies.router import router as companies_router
from twjobs.api.jobs.router import router as jobs_router
from twjobs.api.skills.router import router as skills_router

app = FastAPI()

app.include_router(skills_router, prefix="/api/skills")
app.include_router(auth_router, prefix="/api/auth")
app.include_router(companies_router, prefix="/api/companies")
app.include_router(candidates_router, prefix="/api/candidates")
app.include_router(jobs_router, prefix="/api/jobs")
app.include_router(applications_router, prefix="/api/applications")
