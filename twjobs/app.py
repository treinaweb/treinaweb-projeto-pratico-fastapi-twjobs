from fastapi import FastAPI

from twjobs.api.skills.router import router as skills_router

app = FastAPI()

app.include_router(skills_router, prefix="/api/skills")
