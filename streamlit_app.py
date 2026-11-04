"""
Streamlit Web Entrypoint (streamlit_app.py).
Supports both standard Streamlit execution and direct Python invocation:
    streamlit run streamlit_app.py
    python streamlit_app.py
"""
import os
import sys
import subprocess

# Ensure project root is in sys.path
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

def is_running_in_streamlit() -> bool:
    """Checks whether this script is currently active inside the Streamlit runtime."""
    try:
        from streamlit.runtime.scriptrunner import get_script_run_ctx
        return get_script_run_ctx() is not None
    except Exception:
        return False

if __name__ == "__main__":
    if not is_running_in_streamlit():
        # User ran 'python streamlit_app.py' -> automatically launch Streamlit runner!
        frontend_app_path = os.path.join(ROOT_DIR, "frontend", "streamlit_app.py")
        print("[e-GP Chatbot] Starting Streamlit application in your default browser...")
        cmd = [sys.executable, "-m", "streamlit", "run", frontend_app_path] + sys.argv[1:]
        sys.exit(subprocess.call(cmd))
    else:
        # Running under Streamlit runner -> execute frontend UI
        frontend_app_path = os.path.join(ROOT_DIR, "frontend", "streamlit_app.py")
        with open(frontend_app_path, "r", encoding="utf-8") as f:
            exec(compile(f.read(), frontend_app_path, "exec"), globals())
