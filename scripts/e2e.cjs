#!/usr/bin/env node
/* E2E sanity for Predict/Dashboard: analysis, sentiment, 4 unique checkpoints, 2dp rounding, locked badge */

const puppeteer = require('puppeteer');
const http = require('http');

function httpGet(url) {
  return new Promise((resolve, reject) => {
    const req = http.get(url, (res) => {
      let data = '';
      res.on('data', (c) => (data += c));
      res.on('end', () => resolve({ status: res.statusCode, body: data }));
    });
    req.on('error', reject);
  });
}

function httpPost(url) {
  return new Promise((resolve, reject) => {
    const req = http.request(url, { method: 'POST' }, (res) => {
      let data = '';
      res.on('data', (c) => (data += c));
      res.on('end', () => resolve({ status: res.statusCode, body: data }));
    });
    req.on('error', reject);
    req.end();
  });
}

(async () => {
  const failures = [];
  // Resolve FE base
  let feBase = 'http://localhost:3000';
  try {
    const r = await httpGet(`${feBase}`);
    if ((r.status || 0) >= 400) throw new Error('bad');
  } catch {
    feBase = 'http://localhost:3015';
  }

  // Seed AI for today
  const today = new Date().toLocaleDateString('en-CA', { timeZone: 'America/Chicago' });
  try {
    const r = await httpPost(`http://localhost:8000/ai/predict/${today}?lookbackDays=5`);
    if (![200, 201, 409].includes(r.status)) failures.push(`ai/predict status ${r.status}`);
  } catch (e) {
    failures.push(`ai/predict exception ${e}`);
  }

  const browser = await puppeteer.launch({ headless: 'new' });
  const page = await browser.newPage();
  page.setDefaultTimeout(15000);

  try {
    await page.goto(feBase);
    // Navigate to Predict
    await page.waitForSelector('nav');
    await page.click('text/Predict');
    // Wait for AI preview to load (sentiment or table rows)
    await page.waitForFunction(() => {
      const hasSentiment = !!Array.from(document.querySelectorAll('*')).find(n => (n.textContent||'').includes('Sentiment:'));
      const rows = document.querySelectorAll('table tbody tr');
      return hasSentiment || rows.length >= 4;
    }, { timeout: 20000 });

    // Analysis present
    await page.waitForSelector('h3.font-medium');
    const analysisExists = await page.evaluate(() => {
      const headers = Array.from(document.querySelectorAll('h3.font-medium'));
      const h = headers.find(el => el.textContent && el.textContent.includes('Analysis'));
      if (!h) return false;
      const card = h.closest('div');
      if (!card) return false;
      const p = card.querySelector('p');
      return Boolean(p && p.textContent && p.textContent.trim().length > 0);
    });
    if (!analysisExists) failures.push('No Analysis paragraph');

    // Sentiment present
    const sentimentExists = await page.evaluate(() => !!Array.from(document.querySelectorAll('*')).find(n => (n.textContent||'').includes('Sentiment:')));
    if (!sentimentExists) failures.push('No Sentiment block');

    // Table with 4 rows and unique checkpoints
    await page.waitForSelector('table', { timeout: 20000 });
    const rows = await page.$$eval('table tbody tr', (trs) => trs.map(tr => tr.innerText));
    if (rows.length !== 4) failures.push(`Expected 4 prediction rows, got ${rows.length}`);
    const labels = await page.$$eval('table tbody tr td:first-child', (tds) => tds.map(td => td.textContent?.trim().toLowerCase()));
    const uniq = new Set(labels);
    if (uniq.size !== 4) failures.push(`Duplicate checkpoints: ${labels.join(', ')}`);

    // Rounding check for price columns (predicted & actual)
    const priceCells = await page.$$eval('table tbody tr td:nth-child(2)', (tds) => tds.map(td => td.textContent?.trim()));
    const priceRegex = /^\$\d+(?:\.\d{2})$/;
    priceCells.forEach((txt, i) => {
      if (!priceRegex.test(txt || '')) failures.push(`Bad rounding in row ${i + 1}: ${txt}`);
    });

    // Dashboard checks
    await page.click('text/Dashboard');
    await page.waitForSelector('h2');
    const lockedChip = await page.$x("//*[contains(text(),'Locked')] ");
    if (!lockedChip.length) failures.push('Dashboard missing Locked badge');

    // Low/High rounding
    const moneyTexts = await page.$$eval('p.font-mono.font-bold', (els) => els.map(e => e.textContent || ''));
    const moneyRegex = /^\$\d+(?:\.\d{2})$/;
    if (!moneyTexts.some(t => moneyRegex.test(t))) failures.push('Dashboard money rounding missing');
  } catch (e) {
    failures.push(`Navigation error: ${e.message}`);
  } finally {
    await browser.close();
  }

  if (failures.length) {
    console.error('E2E FAILURES:');
    failures.forEach(f => console.error(' -', f));
    process.exit(1);
  } else {
    console.log('E2E PASS: Predict and Dashboard validated');
  }
})();
