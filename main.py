import uvicorn

from fastapi import FastAPI


app = FastAPI(title="Blog API", description="The management of the Blog API")


@app.get("/")
def read_root():
    """
    Healthcheck page definition

    :return: dict: health status
    """

    return {"message": "Welcome to FastAPI project"}


if __name__ == "__main__":
    uvicorn.run(app="main:app", host="127.0.0.1", port=8000, reload=True)
