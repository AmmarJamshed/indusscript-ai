# Reproduce & Cite

## Local research stack

```bash
git clone https://github.com/AmmarJamshed/indusscript-ai.git
cd indusscript-ai
python -m venv .venv
# Windows: .\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python app.py --report
streamlit run dashboard/app.py
pytest -q
```

## Public demo

Open [https://ammarjamshed.github.io/indusscript-ai/](https://ammarjamshed.github.io/indusscript-ai/)

## Suggested citation

> Ammar Jamshed. *IndusScript AI: A Computational Platform for Comparative Hypothesis Testing on the Undeciphered Indus Writing System* (White Paper v1.0). 2026. GitHub: https://github.com/AmmarJamshed/indusscript-ai

## GitBook publishing (this space)

This `gitbook/` directory is structured for GitBook Git Sync:

1. Create or open a space at [app.gitbook.com](https://app.gitbook.com)
2. Enable **GitHub Sync** → repository `AmmarJamshed/indusscript-ai`
3. Branch `main`, content root `/gitbook` (see `.gitbook.yaml`)
4. Initial sync direction: **GitHub → GitBook**
5. Publish the docs site as public / unlisted per university preference
