from fastapi import FastAPI

from app.api.endpoints import chat, embedd_database
import uvicorn
import subprocess
import threading

app = FastAPI()
app.include_router(embedd_database.router, prefix="/database", tags=["database"])

app.include_router(chat.router, prefix="/chat", tags=["items"])


def run_fastapi():
    print("Starting FastAPI...")
    uvicorn.run(app, host="0.0.0.0", port=8000)


def run_streamlit():
    try:
        print("Starting Streamlit...")
        subprocess.run(["streamlit", "run", "frontend/frontend.py", "--server.port", "8080"], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Streamlit failed with error: {e}")


if __name__ == "__main__":
    fastapi_thread = threading.Thread(target=run_fastapi)
    fastapi_thread.start()

    run_streamlit()
