// Fetch the World Athletics record lists used by data/atletik-rekor (R-11, F-037).
//
// worldathletics.org fills its record tables with scripts, so a plain HTTP request gets an empty page. This script
// opens each record page in Chromium (Playwright), clicks every sex tab (Women, Men, Mixed) and saves the table
// element exactly as the page shows it, one file per page and tab:
//
//   <out>/<slug>--<tab>.html      the <table> element (outerHTML), unchanged
//   <out>/SOURCE.txt              page URL, tab, fetch time (UTC), size and SHA-256 of every file
//
// The saved tables are the raw source of tools/converters/atletik-rekor.py, which treats them as untrusted input
// (parsed, never executed). One page at a time with a pause of at least 2 s between pages.
//
// Usage: node tools/converters/atletik-rekor-fetch.mjs <out_dir> [slug ...]
//   default slugs: world-records world-u20-records world-u18-best-performances asian-records
import { createHash } from 'node:crypto';
import { mkdir, writeFile, appendFile } from 'node:fs/promises';
import { join } from 'node:path';
import { createRequire } from 'node:module';

const require = createRequire(import.meta.url);
const { chromium } = require('playwright');

const [out, ...rest] = process.argv.slice(2);
if (!out) {
    console.error('Usage: node tools/converters/atletik-rekor-fetch.mjs <out_dir> [slug ...]');
    process.exit(1);
}
const slugs = rest.length ? rest : ['world-records', 'world-u20-records', 'world-u18-best-performances', 'asian-records'];
const TABS = ['Women', 'Men', 'Mixed'];
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

await mkdir(out, { recursive: true });
const source = join(out, 'SOURCE.txt');
await writeFile(source, 'World Athletics record lists, rendered in Chromium; <table> element saved per tab, unchanged.\n\n');

const browser = await chromium.launch({ args: ['--disable-dev-shm-usage'] });
const page = await browser.newPage();
for (const slug of slugs) {
    const url = `https://worldathletics.org/records/by-category/${slug}`;
    await page.goto(url, { timeout: 90000 });
    await page.waitForSelector('table tbody tr', { timeout: 60000 });
    for (const tab of TABS) {
        // The tabs are <li><button>women</button></li> (lower case in the markup, capitalised by CSS).
        const button = page.locator('li[class*="navItem"] > button').filter({ hasText: new RegExp(`^\\s*${tab}\\s*$`, 'i') }).first();
        if (!(await button.count())) continue;
        const before = await page.locator('table').first().innerHTML();
        await button.click();
        // Wait until the table changes (or stays the same for the tab that was already active).
        for (let i = 0; i < 40; i++) {
            await sleep(250);
            if ((await page.locator('table').first().innerHTML()) !== before) break;
        }
        await sleep(1500);
        const html = await page.locator('table').first().evaluate((t) => t.outerHTML);
        const name = `${slug}--${tab.toLowerCase()}.html`;
        await writeFile(join(out, name), html);
        const sha = createHash('sha256').update(html).digest('hex');
        const rows = (html.match(/<tr role="row" class="defaultRow/g) || []).length;
        await appendFile(source, `${name}\n  page URL : ${url} (tab "${tab}")\n  fetched  : ${new Date().toISOString()}\n` +
            `  size     : ${Buffer.byteLength(html)} bytes, ${rows} rows\n  SHA-256  : ${sha}\n\n`);
        console.log(`${name}: ${rows} rows`);
    }
    // The legend under the table explains the marks (* pending ratification, Mx, Wo, (i) indoor).
    const body = await page.innerText('body');
    const legend = (body.match(/Legend\s*\n([^\n]+)/) || [])[1] || '(no legend found)';
    await appendFile(source, `${slug} legend: ${legend.trim()}\n\n`);
    await sleep(2000);
}
await browser.close();
