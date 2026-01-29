from fastapi import FastAPI, HTTPException

app = FastAPI()

skills_db = [
    {"id": 1, "name": "Python"},
    {"id": 2, "name": "FastAPI"},
    {"id": 3, "name": "Docker"},
]
next_skill_id = 4


@app.get("/")
def read_root():
    return {"message": "Hello, TWJobs!"}


@app.get("/api/skills")
def get_skills():
    return skills_db


@app.post("/api/skills", status_code=201)
def create_skill(skill: dict):
    global next_skill_id
    new_skill = {"id": next_skill_id, "name": skill["name"]}
    skills_db.append(new_skill)
    next_skill_id += 1
    return new_skill


@app.get("/api/skills/{skill_id}")
def get_skill(skill_id: int):
    for skill in skills_db:
        if skill["id"] == skill_id:
            return skill
    raise HTTPException(status_code=404, detail="Skill not found")


@app.put("/api/skills/{skill_id}")
def update_skill(skill_id: int, skill: dict):
    for existing_skill in skills_db:
        if existing_skill["id"] == skill_id:
            existing_skill["name"] = skill["name"]
            return existing_skill
    raise HTTPException(status_code=404, detail="Skill not found")


@app.delete("/api/skills/{skill_id}", status_code=204)
def delete_skill(skill_id: int):
    for index, skill in enumerate(skills_db):
        if skill["id"] == skill_id:
            del skills_db[index]
            return
    raise HTTPException(status_code=404, detail="Skill not found")
