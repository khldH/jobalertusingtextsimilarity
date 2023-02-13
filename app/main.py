import uvicorn
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

# from app import models
# from app.database import engine
from app.routers import index, user,post, services,organizaiton


def include_router(application):
    application.include_router(index.router)
    application.include_router(user.router)
    application.include_router(post.router)
    application.include_router(services.router)
    application.include_router(organizaiton.router)


# def create_tables():
#     models.Base.metadata.create_all(bind=engine)


def configure_static(app):  # new
    app.mount("/static", StaticFiles(directory="static"), name="static")


def start_application():
    app = FastAPI()
    include_router(app)
    # create_tables()
    configure_static(app)
    return app


app = start_application()

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001)
