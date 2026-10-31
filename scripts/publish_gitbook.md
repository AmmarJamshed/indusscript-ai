# Publish this white paper on GitBook

The repository already contains a GitBook-ready tree at `gitbook/` (see `.gitbook.yaml`).

## Recommended: GitHub → GitBook Sync (no token in CI)

1. Open [https://app.gitbook.com](https://app.gitbook.com) and create a space named **IndusScript AI White Paper**.
2. Space menu → **Synchronize with Git** → **GitHub**.
3. Authorize the GitBook GitHub App on `AmmarJamshed/indusscript-ai` if prompted.
4. Select branch `main`.
5. Set the content / project directory to `gitbook` (root config: `.gitbook.yaml`).
6. Initial sync: **GitHub → GitBook**.
7. **Publish** the docs site (public or unlisted).

Expected public URL pattern: `https://<org>.gitbook.io/indusscript-ai/` (exact slug chosen at publish time).

## Optional: API import (requires personal access token)

```powershell
$env:GITBOOK_API_TOKEN = "<token from https://app.gitbook.com/account/developer>"
$env:GITBOOK_SPACE_ID = "<space id>"
# Then:
# POST https://api.gitbook.com/v1/spaces/{spaceId}/git/import
```

Do not commit tokens to the repository.
