/* Ticket 8.3. Opens Moonlight in a real browser (Chromium) and catches
   everything the page tries to send outside. Nothing ever reaches Umami:
   every outside request is stopped here, inside the browser.

   Run by tests/test_umami.py:  node browser_check.js <local address> <saved umami script>
   Prints one JSON object. It never prints request headers. */
"use strict";
const fs = require("fs");
const { chromium } = require("playwright");

const LOCAL = process.argv[2];                    // like http://127.0.0.1:8123
const SAVED_SCRIPT = fs.readFileSync(process.argv[3], "utf-8");
const REAL_SITE = "https://moonlightclues.com";   // on Kashish's list, so the tracker is allowed to run
const TYPED = "pulmonary arterial hypertension";
const SECRET_WORDS = ["disease", "mondo", "tab=", "guide=", "pulmonary", "hypertension", "secretword"];

/* One fresh browser window with a trap on every request. */
async function trap(browser, { blockScript = false, doNotTrack = false, breakBeforeSend = false } = {}) {
  const context = await browser.newContext({ viewport: { width: 390, height: 844 } });
  const caught = { umami: [], scriptLoads: 0, otherOutside: [], headersClean: true, pageErrors: [] };
  if (doNotTrack) await context.addInitScript(() => {
    Object.defineProperty(Navigator.prototype, "doNotTrack", { get: () => "1" });
  });
  if (breakBeforeSend) await context.addInitScript(() => {
    Object.defineProperty(window, "moonlightVisit", { get: () => undefined, set() {} });
  });
  await context.route("**/*", async route => {
    const request = route.request(), url = request.url();
    if (url.startsWith(REAL_SITE + "/") || url.startsWith(LOCAL + "/")) {
      /* Moonlight itself: answered by the test's own local server. */
      const answer = await route.fetch({ url: LOCAL + url.slice(new URL(url).origin.length) });
      return route.fulfill({ response: answer });
    }
    /* Everything below is outside Moonlight. Check the headers the browser
       would attach (the Referer is one of them) without printing them. */
    const all = await request.allHeaders();
    const headers = Object.values(all).join("\n").toLowerCase();
    const referer = all["referer"] || "";   // the address the browser says it came from
    if (SECRET_WORDS.some(word => headers.includes(word))) caught.headersClean = false;
    if (referer && referer !== new URL(referer).origin + "/") caught.headersClean = false;
    if (url === "https://cloud.umami.is/script.js") {
      caught.scriptLoads += 1;
      if (blockScript) return route.abort("blockedbyclient");
      /* The saved copy. It also tries to set a cookie, to show the browser refuses it. */
      return route.fulfill({ status: 200, contentType: "application/javascript", body: SAVED_SCRIPT,
        headers: { "access-control-allow-origin": "*", "set-cookie": "trap_script=1; Path=/; Secure; SameSite=None" } });
    }
    if (new URL(url).hostname.endsWith("umami.is")) {
      caught.umami.push({ method: request.method(), to: url, body: JSON.parse(request.postData() || "null") });
      return route.fulfill({ status: 200, contentType: "application/json", body: "{}",
        headers: { "access-control-allow-origin": "*", "set-cookie": "trap_send=1; Path=/; Secure; SameSite=None" } });
    }
    caught.otherOutside.push(request.method() + " " + url);
    return route.abort();
  });
  const page = await context.newPage();
  page.on("pageerror", error => caught.pageErrors.push(String(error)));
  return { context, page, caught };
}

const settle = page => page.waitForTimeout(1500);  // the tracker waits 300 ms before a send

async function storage(context, page) {
  return {
    cookies: (await context.cookies()).map(cookie => cookie.name),
    documentCookie: await page.evaluate(() => document.cookie),
    localStorageKeys: await page.evaluate(() => Object.keys(localStorage)),
    sessionStorageKeys: await page.evaluate(() => Object.keys(sessionStorage)),
  };
}

/* Search, open every tab, open the guide. Returns what the person can see. */
async function useThePage(page) {
  await page.fill("#disease-search", TYPED);
  await page.click("#search-form button[type=submit]");
  await page.click("#disease-matches button");
  await page.waitForSelector("#found:not([hidden])");
  const seen = { diseaseTitle: await page.textContent("#disease-title") };
  for (const tab of ["trials", "clues", "approved"]) {
    await page.click("#tab-" + tab);
    await page.waitForTimeout(300);
  }
  await page.click("#tab-clues");
  await page.waitForSelector("#panel-clues [data-slot=card]");
  seen.clueCards = await page.locator("#panel-clues [data-slot=card]").count();
  seen.titleAfterSearch = await page.title();
  await page.click(".card-help a");          // opens the guide
  await page.waitForSelector("#guide:not([hidden])");
  seen.guideOpen = await page.isVisible("#guide-facts-title");
  await page.click("[data-guide-close]");
  seen.safetyLine = (await page.textContent("[data-slot=safety-line]")).trim();
  await settle(page);
  return seen;
}

(async () => {
  const browser = await chromium.launch();
  const out = {};

  /* 1. The ticket's example: a link that opens a disease and a tab, reached
        from another site whose address holds private words. */
  {
    const { context, page, caught } = await trap(browser);
    await page.goto(REAL_SITE + "/?disease=MONDO_0015924&tab=clues#secretword",
      { referer: "https://example.org/some/page?q=secretword" });
    await page.waitForSelector("#found:not([hidden])");
    await settle(page);
    out.link = { caught, title: await page.title(), storage: await storage(context, page) };
    await context.close();
  }

  /* 2. Search for a disease, open each tab, open the guide. Then the guide link. */
  {
    const { context, page, caught } = await trap(browser);
    await page.goto(REAL_SITE + "/");
    await settle(page);
    const seen = await useThePage(page);
    await page.goto(REAL_SITE + "/?guide=1");
    await page.waitForSelector("#guide:not([hidden])");
    await settle(page);
    out.use = { caught, seen, storage: await storage(context, page) };
    await context.close();
  }

  /* 3. Umami's script is blocked. The page must work exactly as before. */
  {
    const { context, page, caught } = await trap(browser, { blockScript: true });
    await page.goto(REAL_SITE + "/");
    await settle(page);
    const seen = await useThePage(page);
    out.blocked = { caught, seen, umamiExists: await page.evaluate(() => typeof window.umami) };
    await context.close();
  }

  /* 4. The browser says Do Not Track. Nothing is sent. */
  {
    const { context, page, caught } = await trap(browser, { doNotTrack: true });
    await page.goto(REAL_SITE + "/?disease=MONDO_0015924");
    await page.waitForSelector("#found:not([hidden])");
    await settle(page);
    out.doNotTrack = { caught };
    await context.close();
  }

  /* 5. A laptop or a test run (not the real site). Nothing is sent. */
  {
    const { context, page, caught } = await trap(browser);
    await page.goto(LOCAL + "/?disease=MONDO_0015924");
    await page.waitForSelector("#found:not([hidden])");
    await settle(page);
    out.laptop = { caught };
    await context.close();
  }

  /* 6. One of the two guards fails: the before-send function is missing.
        data-exclude-search and data-exclude-hash must still keep the disease out. */
  {
    const { context, page, caught } = await trap(browser, { breakBeforeSend: true });
    await page.goto(REAL_SITE + "/?disease=MONDO_0015924&tab=clues#secretword",
      { referer: "https://example.org/some/page?q=secretword" });
    await page.waitForSelector("#found:not([hidden])");
    await settle(page);
    out.oneGuardOnly = { caught, guardMissing: await page.evaluate(() => typeof window.moonlightVisit) };
    await context.close();
  }

  await browser.close();
  console.log(JSON.stringify(out));
})().catch(error => { console.error(String(error && error.stack || error)); process.exit(1); });
