/**
 * Create/publish IndusScript AI white paper on GitBook.
 * Requires env GITBOOK_TOKEN — never commit secrets.
 */
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const GB = path.join(ROOT, 'gitbook');
const TOKEN = process.env.GITBOOK_TOKEN;
const ORG = process.env.GITBOOK_ORG || 'j7SVn4ixz3OLy2MIcSrV';
const API = 'https://api.gitbook.com/v1';

if (!TOKEN) {
  console.error('Set GITBOOK_TOKEN');
  process.exit(1);
}

const headers = {
  Authorization: `Bearer ${TOKEN}`,
  Accept: 'application/json',
  'Content-Type': 'application/json',
};

async function api(method, urlPath, body) {
  const res = await fetch(`${API}${urlPath}`, {
    method,
    headers,
    body: body === undefined ? undefined : JSON.stringify(body),
  });
  const text = await res.text();
  let json = null;
  try {
    json = text ? JSON.parse(text) : null;
  } catch {
    json = { raw: text };
  }
  if (!res.ok) {
    throw new Error(`${method} ${urlPath} -> ${res.status}: ${text.slice(0, 900)}`);
  }
  return json;
}

function stripYamlFrontMatter(md) {
  return md.replace(/^---\r?\n[\s\S]*?\r?\n---\r?\n/, '');
}

function rewriteAssets(md) {
  // GitBook hosted uploads later; keep relative .gitbook paths for Git Sync.
  return md.replaceAll('](.gitbook/assets/', '](https://raw.githubusercontent.com/AmmarJamshed/indusscript-ai/main/gitbook/.gitbook/assets/');
}

function readOrder() {
  const summary = fs.readFileSync(path.join(GB, 'SUMMARY.md'), 'utf8');
  const items = [];
  for (const line of summary.split(/\r?\n/)) {
    const link = line.match(/^\s*\*\s*\[([^\]]+)\]\(([^)]+\.md)\)/);
    if (link) items.push({ title: link[1], file: link[2] });
  }
  return items;
}

async function ensureSpace() {
  if (process.env.GITBOOK_SPACE) return process.env.GITBOOK_SPACE;
  const spaces = await api('GET', `/orgs/${ORG}/spaces`);
  const found = (spaces.items || []).find(
    (s) => /indusscript/i.test(s.title || '') || /indus script ai/i.test(s.title || '')
  );
  if (found) {
    console.log(`› reuse space ${found.id} (${found.title})`);
    return found.id;
  }
  console.log('› creating space');
  const space = await api('POST', `/orgs/${ORG}/spaces`, {
    title: 'IndusScript AI White Paper',
    emoji: '1f4dc',
    editMode: 'live',
    empty: true,
  });
  console.log(`› SPACE=${space.id}`);
  return space.id;
}

async function ensureSite(spaceId) {
  if (process.env.GITBOOK_SITE) return process.env.GITBOOK_SITE;
  const sites = await api('GET', `/orgs/${ORG}/sites`);
  const found = (sites.items || []).find((s) =>
    /indusscript/i.test(s.title || '') || (s.spaces || []).includes?.(spaceId)
  );
  if (found) {
    console.log(`› reuse site ${found.id}`);
    return found.id;
  }
  // Create site if API supports it; otherwise attach later.
  try {
    const site = await api('POST', `/orgs/${ORG}/sites`, {
      title: 'IndusScript AI',
      spaces: [spaceId],
    });
    console.log(`› SITE=${site.id}`);
    return site.id;
  } catch (e) {
    console.warn(`› site create skipped: ${e.message}`);
    const sites2 = await api('GET', `/orgs/${ORG}/sites`);
    const any = (sites2.items || [])[0];
    if (!any) throw e;
    console.log(`› fallback site ${any.id} (${any.title})`);
    return any.id;
  }
}

async function ensureChangeRequest(spaceId) {
  const list = await api('GET', `/spaces/${spaceId}/change-requests`);
  const items = list.items || [];
  const open = items.find((c) => c.status === 'open' || c.status === 'draft');
  if (open) return String(open.number);
  const cr = await api('POST', `/spaces/${spaceId}/change-requests`, {
    subject: 'Import IndusScript AI White Paper v1.0',
  });
  return String(cr.number);
}

async function main() {
  const SPACE = await ensureSpace();
  const SITE = await ensureSite(SPACE);
  const items = readOrder();
  console.log(`› ${items.length} pages from SUMMARY.md`);

  // Prefer git import so assets sync
  try {
    console.log('› attempting git import from GitHub');
    await api('POST', `/spaces/${SPACE}/git/import`, {
      url: 'https://github.com/AmmarJamshed/indusscript-ai.git',
      ref: 'refs/heads/main',
      // Some API variants accept projectDirectory / path
      projectDirectory: 'gitbook',
    });
    console.log('› git import accepted');
  } catch (e) {
    console.warn(`› git import unavailable (${e.message.slice(0, 200)}) — using change-request markdown import`);
    const CR = await ensureChangeRequest(SPACE);
    const content = await api('GET', `/spaces/${SPACE}/change-requests/${CR}/content`);
    const existing = new Map();
    const walk = (pages) => {
      for (const p of pages || []) {
        existing.set(p.title, p.id);
        walk(p.pages);
      }
    };
    walk(content.pages);

    const apply = async (changes, label) => {
      if (!changes.length) return;
      console.log(`  ${label}: ${changes.length}`);
      await api('POST', `/spaces/${SPACE}/change-requests/${CR}/content`, { changes });
    };

    const cover = items[0];
    const first = content.pages?.[0];
    if (cover && first) {
      const raw = rewriteAssets(
        stripYamlFrontMatter(fs.readFileSync(path.join(GB, cover.file), 'utf8'))
      );
      await apply(
        [{ operation: 'update_page', page: first.id, title: cover.title, document: { markdown: raw } }],
        'cover'
      );
    }

    for (const item of items.slice(1)) {
      if (existing.has(item.title)) {
        console.log(`  skip ${item.title}`);
        continue;
      }
      const md = rewriteAssets(
        stripYamlFrontMatter(fs.readFileSync(path.join(GB, item.file), 'utf8'))
      );
      try {
        await apply(
          [{ operation: 'insert_page', title: item.title, document: { markdown: md } }],
          item.title
        );
      } catch (err) {
        console.error(`  FAIL ${item.title}: ${err.message.slice(0, 200)}`);
      }
    }

    try {
      await api('POST', `/spaces/${SPACE}/change-requests/${CR}/merge`, {});
      console.log('› merged');
    } catch (e) {
      console.warn(`› merge: ${e.message.slice(0, 300)}`);
    }
  }

  try {
    await api('POST', `/orgs/${ORG}/sites/${SITE}/publish`, {});
    console.log('› site publish requested');
  } catch (e) {
    console.warn(`› publish: ${e.message.slice(0, 300)}`);
  }

  const site = await api('GET', `/orgs/${ORG}/sites/${SITE}`);
  console.log(`SPACE=${SPACE}`);
  console.log(`SITE=${SITE}`);
  console.log(`PUBLIC_URL=${site.urls?.published || '(configure slug in GitBook UI)'}`);
  console.log(`APP=https://app.gitbook.com/o/${ORG}/s/${SPACE}/`);
  console.log(`SITE_APP=${site.urls?.app || ''}`);
}

main().catch((e) => {
  console.error(e);
  process.exit(1);
});
