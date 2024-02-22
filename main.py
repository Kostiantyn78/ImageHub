from pathlib import Path

from fastapi import FastAPI, Depends, HTTPException
from fastapi.staticfiles import StaticFiles
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

from src.database.db import get_db
from src.routes import auth, users, photo, comments

app = FastAPI(title="ImageHUB", description="Welcome to ImageHUB API",
              swagger_ui_parameters={"syntaxHighlight.theme": "obsidian"})

BASE_DIR = Path(__file__).parent
directory = BASE_DIR.joinpath("src").joinpath("static")
app.mount("/static", StaticFiles(directory=directory), name="static")

app.include_router(auth.router, prefix='/api', tags=['Authentication'])
app.include_router(users.router, prefix='/api', tags=['Users'])
app.include_router(photo.router, prefix='/api', tags=['Photos'])
app.include_router(comments.router, prefix="/api", tags=['Comments'])


@app.get("/api/healthchecker", tags=['Health checker'])
async def healthchecker(db: AsyncSession = Depends(get_db)):
    try:
        result = await db.execute(text("SELECT 1"))
        result = result.fetchone()
        if result is None:
            raise HTTPException(status_code=500, detail="Database is not configured correctly")
        return {"message": "Welcome to FastAPI!"}
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail="Error connecting to the database")
