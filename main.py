import uvicorn
import subprocess

if __name__ == "__main__":
    subprocess.Popen(["streamlit", "run", "frontend.py"])
    uvicorn.run("app.core.app:app", host="127.0.0.1", port=8000, reload=True)
