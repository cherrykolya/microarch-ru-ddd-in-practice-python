import uvicorn


def start_uvicorn():
    uvicorn.run("api.main:app", host="127.0.0.1", port=8082, reload=True)


if __name__ == "__main__":
    start_uvicorn()
