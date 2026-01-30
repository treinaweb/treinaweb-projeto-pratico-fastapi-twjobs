import typer
from rich import print
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from twjobs.core.db import engine
from twjobs.core.models import Skill, User
from twjobs.core.security import hash_password

app = typer.Typer()


@app.command()
def hello(name: str = "World"):
    print(f"Hello, {name}!")


@app.command()
def goodbye(name: str = "World"):
    print(f"Goodbye, {name}!")


@app.command()
def populate_skills():
    skills = [
        "PYTHON",
        "JAVA",
        "JAVASCRIPT",
        "TYPESCRIPT",
        "C",
        "C++",
        "C#",
        "GO",
        "RUST",
        "PHP",
        "RUBY",
        "SWIFT",
        "KOTLIN",
        "SCALA",
        "DART",
        "SQL",
        "POSTGRESQL",
        "MYSQL",
        "SQLITE",
        "ORACLE DATABASE",
        "MONGODB",
        "REDIS",
        "ELASTICSEARCH",
        "HTML",
        "CSS",
        "SASS",
        "BOOTSTRAP",
        "TAILWIND CSS",
        "REACT",
        "ANGULAR",
        "VUE.JS",
        "NEXT.JS",
        "NODE.JS",
        "EXPRESS.JS",
        "FASTAPI",
        "DJANGO",
        "FLASK",
        "SPRING BOOT",
        "NESTJS",
        "ASP.NET CORE",
        "GRAPHQL",
        "REST API",
        "GIT",
        "GITHUB",
        "GITLAB",
        "BITBUCKET",
        "DOCKER",
        "DOCKER COMPOSE",
        "KUBERNETES",
        "CI/CD",
        "GITHUB ACTIONS",
        "GITLAB CI",
        "JENKINS",
        "AWS",
        "AZURE",
        "GOOGLE CLOUD",
        "TERRAFORM",
        "LINUX",
        "SHELL SCRIPT",
        "POWERSHELL",
        "MICROSERVICES",
        "CLEAN CODE",
        "SOLID",
        "DESIGN PATTERNS",
        "DOMAIN DRIVEN DESIGN",
        "TESTES UNITÁRIOS",
        "TESTES DE INTEGRAÇÃO",
        "JEST",
        "PYTEST",
        "JUNIT",
        "CYPRESS",
        "SELENIUM",
        "PERFORMANCE TESTING",
        "SEGURANÇA DA INFORMAÇÃO",
        "OAUTH 2.0",
        "JWT",
        "WEB SOCKETS",
        "MESSAGE QUEUES",
        "RABBITMQ",
        "APACHE KAFKA",
        "EVENT DRIVEN ARCHITECTURE",
        "DATA STRUCTURES",
        "ALGORITHMS",
        "OBJECT ORIENTED PROGRAMMING",
        "FUNCTIONAL PROGRAMMING",
        "CONCURRENCY",
        "ASYNCHRONOUS PROGRAMMING",
        "API VERSIONING",
        "CODE REVIEW",
        "STATIC CODE ANALYSIS",
        "SONARQUBE",
        "ORM",
        "SQLALCHEMY",
        "HIBERNATE",
        "ENTITY FRAMEWORK",
        "UML",
        "SYSTEM DESIGN",
        "SCRUM",
        "KANBAN",
        "AGILE METHODOLOGIES",
    ]

    with Session(engine) as session:
        for skill_name in skills:
            skill = Skill(name=skill_name)
            session.add(skill)
        session.commit()

    print("[bold green]Skills populated successfully.[/bold green]")


@app.command()
def create_superuser():
    username = typer.prompt("What is the superuser username?", default="admin")
    password = typer.prompt("What is the superuser password?", hide_input=True)

    password_hash = hash_password(password)

    with Session(engine) as session:
        superuser = User(
            username=username, password_hash=password_hash, role="admin"
        )
        session.add(superuser)
        try:
            session.commit()
            print(
                f"[bold green]Superuser '{username}' "
                "created successfully.[/bold green]"
            )
        except IntegrityError:
            session.rollback()
            print(
                f"[bold red]Error: A user with username '{username}' "
                "already exists.[/bold red]"
            )


if __name__ == "__main__":
    app()
