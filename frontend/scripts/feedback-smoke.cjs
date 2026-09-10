// Run against the local Vite server. All API calls are intercepted, never sent to a backend.
const { chromium } = require('../node_modules/.browser-check/node_modules/playwright');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const matchResult = require('../../contracts/fixtures/match-result.json');
const resumeResult = require('../../contracts/fixtures/resume-analysis-result.json');
const output = path.resolve(__dirname, '../node_modules/.browser-check/artifacts');
const baseURL = process.env.FEEDBACK_URL || 'http://127.0.0.1:5173';
if (!['localhost', '127.0.0.1'].includes(new URL(baseURL).hostname)) throw new Error('Use a local test server.');
fs.mkdirSync(output, { recursive: true });
const pdf = { name: 'candidate.pdf', mimeType: 'application/pdf', buffer: Buffer.from('%PDF-1.4 test fixture') };
const jd = { ...pdf, name: 'job-description.pdf' };
const emptyPage = { items: [], page: 0, size: 10, totalItems: 0, totalPages: 0 };

(async () => {
  const browser = await chromium.launch({ channel: 'chrome', headless: true });
  const context = await browser.newContext({ viewport: { width: 1440, height: 1000 } });
  const page = await context.newPage();
  page.setDefaultTimeout(15000);
  const errors = [];
  const consoleErrors = [];
  const failedRequests = [];
  page.on('requestfailed', (request) => failedRequests.push({ url: request.url(), error: request.failure()?.errorText }));
  page.on('pageerror', (error) => errors.push(error.message));
  page.on('console', (message) => { if (['error', 'warning'].includes(message.type())) consoleErrors.push(message.text()); });
  let pendingMatch;
  let pendingResume;
  let matchCalls = 0;
  let loginRole = 'USER';
  let historyFails = true;
  let adminFails = true;
  const matchPayloads = [];
  await page.clock.install();
  await page.route('**/api/**', async (route) => {
    const url = new URL(route.request().url());
    if (!url.pathname.startsWith('/api/')) return route.continue();
    if (url.pathname === '/api/auth/login') return route.fulfill({ json: {
      accessToken: 'browser-test-token', tokenType: 'Bearer', expiresIn: 7200,
      user: { id: 1, email: 'preview@example.test', fullName: 'Preview User', role: loginRole },
    } });
    if (url.pathname === '/api/analyses/match') {
      matchCalls += 1;
      matchPayloads.push(route.request().postData());
      return new Promise((resolve) => { pendingMatch = async (status = 200) => {
        await route.fulfill({ status, json: status === 200 ? { id: 1, result: matchResult } : { message: 'Test service unavailable' } });
        resolve();
      }; });
    }
    if (url.pathname === '/api/analyses/resume') return new Promise((resolve) => { pendingResume = async () => {
      await route.fulfill({ json: { id: 2, result: resumeResult } }); resolve();
    }; });
    if (url.pathname === '/api/analyses') {
      const status = historyFails ? 503 : 200;
      historyFails = false;
      return route.fulfill({ status, json: status === 200 ? emptyPage : { message: 'Unavailable' } });
    }
    if (url.pathname === '/api/admin/metrics') {
      const status = adminFails ? 503 : 200;
      return route.fulfill({ status, json: { totalAnalyses: 0, resumeAnalysesCount: 0, matchAnalysesCount: 0, fallbackRate: 0, avgLatencyMs: 0, p95LatencyMs: 0 } });
    }
    if (url.pathname.startsWith('/api/admin/')) return route.fulfill({ json: emptyPage });
    throw new Error(`Unexpected API request: ${url.pathname}`);
  });

  const signIn = async () => {
    await page.goto(`${baseURL}/login`);
    await page.getByLabel('Email', { exact: true }).fill('preview@example.test');
    await page.getByLabel('Password', { exact: true }).fill('test-password');
    await page.getByRole('button', { name: 'Sign in', exact: true }).click();
    await page.waitForURL(`**/${loginRole === 'ADMIN' ? 'admin' : 'dashboard'}`);
  };
  const prepareMatch = async (textMode = false) => {
    await page.getByRole('button', { name: 'Job Match & ATS', exact: true }).click();
    await page.getByLabel('Upload Candidate CV (PDF)').setInputFiles(pdf);
    if (textMode) {
      await page.getByRole('button', { name: 'Paste JD Text', exact: true }).click();
      await page.getByLabel('Job Description Text (min 50 chars)', { exact: true }).fill('Looking for a frontend developer with React, TypeScript and accessible CSS experience.');
    } else await page.getByLabel('Upload Target Job Description (PDF)').setInputFiles(jd);
  };
  const startMatch = async () => {
    const requested = page.waitForRequest('**/api/analyses/match');
    await page.getByRole('button', { name: 'Run Job Match & ATS Analysis', exact: true }).click();
    await requested;
    await page.getByRole('dialog').waitFor();
  };
  const noOverflow = async (label) => assert(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth), `${label} overflows`);

  try {
    await signIn();
    for (const width of [320, 768, 1024, 1440]) {
      await page.setViewportSize({ width, height: 1000 });
      if (width !== 320) await page.goto(`${baseURL}/dashboard`);
      await prepareMatch();
      await noOverflow(`Dashboard ${width}`);
      await startMatch();
      assert(await page.getByRole('dialog').evaluate((dialog) => dialog.matches(':modal')));
      assert.equal(await page.evaluate(() => document.body.style.overflow), 'hidden');
      await page.keyboard.press('Escape');
      assert(await page.getByRole('dialog').isVisible());
      await page.keyboard.press('Tab');
      assert(await page.evaluate(() => document.activeElement === document.body || !!document.activeElement.closest('dialog')));
      await page.clock.fastForward(10000);
      const value = Number(await page.getByRole('progressbar').getAttribute('value'));
      assert(value >= 65 && value < 100);
      const box = await page.getByRole('dialog').boundingBox();
      assert(box.x >= 0 && box.x + box.width <= width);
      // Let the compositor finish the progress transition after the clock jump.
      await page.waitForTimeout(350);
      await page.screenshot({ path: path.join(output, `match-${width}.png`) });
      if (width === 1440) {
        await page.emulateMedia({ reducedMotion: 'reduce' });
        await page.waitForTimeout(50);
        assert(await page.getByRole('dialog').evaluate((dialog) => dialog.getAnimations({ subtree: true }).every((animation) => animation.playState !== 'running')));
        await page.emulateMedia({ reducedMotion: 'no-preference' });
      }
      await pendingMatch(503);
      await page.getByRole('button', { name: 'Close', exact: true }).waitFor();
      await page.getByRole('button', { name: 'Close', exact: true }).click();
      assert.equal(await page.evaluate(() => document.body.style.overflow), '');
      assert(await page.getByText('candidate.pdf', { exact: true }).isVisible());
      console.log(`PASS: overlay, keyboard, file preservation, layout at ${width}px`);
    }

    await startMatch();
    const before = matchCalls;
    await page.clock.fastForward(61000);
    assert.equal(await page.getByRole('progressbar').getAttribute('value'), '95');
    await page.getByRole('button', { name: 'Minimize', exact: true }).click();
    assert.equal(await page.getByRole('dialog').count(), 0);
    assert(await page.getByRole('button', { name: 'Resume Scoring', exact: true }).isDisabled());
    assert(await page.getByRole('button', { name: 'Remove candidate.pdf', exact: true }).isDisabled());
    await page.getByRole('button', { name: 'Show progress', exact: true }).click();
    assert.equal(matchCalls, before);
    await pendingMatch(503);
    await page.getByRole('button', { name: 'Try again', exact: true }).click();
    await page.waitForFunction(() => document.querySelector('progress')?.value < 10);
    await pendingMatch();
    await page.waitForURL('**/match/result');
    await page.getByRole('heading', { name: 'Job Match Result', exact: true }).waitFor();
    assert(matchPayloads[0].includes('name="jdFile"'));
    console.log('PASS: slow request, minimize/expand, retry, real completion and PDF result');

    await page.getByRole('link', { name: 'Return to dashboard', exact: true }).click();
    await prepareMatch(true);
    await startMatch();
    await pendingMatch();
    await page.waitForURL('**/match/result');
    assert(matchPayloads.at(-1).includes('name="jobDescription"'));
    assert(!matchPayloads.at(-1).includes('name="jdFile"'));

    await page.getByRole('link', { name: 'Return to dashboard', exact: true }).click();
    await page.getByLabel('Upload Resume (PDF)').setInputFiles(pdf);
    await page.getByRole('button', { name: 'Upload Resume', exact: true }).click();
    await page.getByText('Analyzing your resume.', { exact: false }).waitFor();
    assert(await page.getByRole('button', { name: 'Remove candidate.pdf', exact: true }).isDisabled());
    await pendingResume();
    await page.waitForURL('**/resume/result');
    await page.getByRole('link', { name: 'Return to dashboard', exact: true }).click();
    await page.getByRole('button', { name: 'Analysis History', exact: true }).click();
    await page.getByRole('button', { name: 'Try again', exact: true }).click();
    await page.getByText('No previous analyses found.', { exact: true }).waitFor();
    console.log('PASS: JD text, resume scoring and history retry');

    await page.getByRole('button', { name: 'Resume Scoring', exact: true }).click();
    await prepareMatch();
    await startMatch();
    await pendingMatch(401);
    await page.waitForURL('**/login');
    assert.equal(await page.evaluate(() => document.body.style.overflow), '');
    loginRole = 'ADMIN';
    await signIn();
    await page.getByRole('button', { name: 'Try again', exact: true }).waitFor();
    adminFails = false;
    await page.getByRole('button', { name: 'Try again', exact: true }).click();
    await page.getByText('No registered users.', { exact: true }).waitFor();
    await page.getByText('No analyses yet.', { exact: true }).waitFor();
    for (const width of [320, 768, 1024, 1440]) {
      await page.setViewportSize({ width, height: 1000 });
      await noOverflow(`Admin ${width}`);
    }
    await page.screenshot({ path: path.join(output, 'admin.png'), fullPage: true });
    await page.getByRole('button', { name: 'Log out', exact: true }).click();
    await page.waitForURL('**/login');
    assert.deepEqual(errors, []);
    const unexpectedConsole = consoleErrors.filter((message) => !/Failed to load resource: the server responded with a status of (503|401)/.test(message));
    assert.deepEqual(unexpectedConsole, []);
    console.log('PASS: 401 redirect, Admin retry/empty states, logout and no unexpected console errors');
  } catch (error) {
    await page.screenshot({ path: path.join(output, 'failure.png'), fullPage: true }).catch(() => {});
    console.error('Observed page errors:', errors);
    console.error('Failed browser requests:', failedRequests);
    throw error;
  } finally {
    await browser.close();
  }
})().catch((error) => { console.error(error); process.exitCode = 1; });
