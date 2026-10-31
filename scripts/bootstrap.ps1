# Bootstrap IndusScript AI on Windows
Set-Location $PSScriptRoot\..
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python app.py --report
Write-Host "Launch dashboard with: streamlit run dashboard/app.py"
