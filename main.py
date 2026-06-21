from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from database import Base, engine
from routers import auth_routes, farm_routes

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Shamba API", version="1.0")

# Wide open for the hackathon so Vanessa's frontend can hit it from any
# origin while you're both iterating fast. Tighten allow_origins before
# (or right after) judging if you have a spare five minutes.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_routes.router)
app.include_router(farm_routes.router)


@app.get("/")
def root():
    return {"status": "Shamba API is running"}