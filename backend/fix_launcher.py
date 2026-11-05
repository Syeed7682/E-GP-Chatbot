import os

for path in ['streamlit_app.py', 'frontend/streamlit_app.py']:
    with open(path, 'r', encoding='utf-8') as f:
        text = f.read()

    old_target = "import requests\nimport streamlit as st"
    new_target = """from streamlit.runtime import exists as _st_exists
if not _st_exists():
    import sys
    from streamlit.web import cli as stcli
    sys.argv = ["streamlit", "run", os.path.abspath(__file__)]
    sys.exit(stcli.main())

import requests
import streamlit as st"""

    if old_target in text:
        text = text.replace(old_target, new_target, 1)
        text = text.replace("if hasattr(st, \"secrets\"):", "if _st_exists() and hasattr(st, \"secrets\"):")
        with open(path, 'w', encoding='utf-8') as f:
            f.write(text)
        print("Updated:", path)
    else:
        print("Old target not found in:", path)

