$ErrorActionPreference = "Stop"
Set-Location -LiteralPath $PSScriptRoot
& "C:\Users\quynh\anaconda3\python.exe" -m streamlit run "dashboard\app.py" --server.headless true --server.port 8501
