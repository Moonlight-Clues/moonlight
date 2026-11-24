// Study P12. Phone-width (390 px) pictures of every tab with every box
// opened, from the answers in answers/ (saved fixtures only). The page is
// web/index.html as on main; every other request is refused, so Umami and
// the network are never reached.
//   node fixtures/probe_p12/take_pictures.js
const { chromium } = require("playwright");
const fs = require("fs"), path = require("path");
const ROOT = path.resolve(__dirname, "../..");
const PAGE = fs.readFileSync(path.join(ROOT, "web/index.html"), "utf8");
const OUT = path.join(__dirname, "pictures"), TEXT = path.join(__dirname, "text");
fs.mkdirSync(TEXT, { recursive: true });
const SITE = "http://moonlight.test/";
const PAGES = ["huntington", "type2diabetes", "pah", "myasthenia", "haemophiliaA"];

async function open(browser, answer) {
  const context = await browser.newContext({ viewport: { width: 390, height: 844 }, deviceScaleFactor: 1 });
  await context.route("**/*", route => {
    const url = route.request().url();
    if (url === SITE || url.startsWith(SITE + "?")) return route.fulfill({ contentType: "text/html; charset=utf-8", body: PAGE });
    if (answer && url.startsWith(SITE + "api/clues")) return route.fulfill({ contentType: "application/json", body: JSON.stringify(answer) });
    return route.abort();
  });
  return [context, await context.newPage()];
}
// JPEG stops at 65,535 px tall. A taller page is saved in parts of 60,000 px.
async function shot(page, file) {
  const height = await page.evaluate(() => document.documentElement.scrollHeight);
  if (height <= 65000) return page.screenshot({ path: file + ".jpg", fullPage: true, type: "jpeg", quality: 55 });
  for (let top = 0, n = 1; top < height; top += 60000, n++)
    await page.screenshot({ path: `${file}_part${n}.jpg`, fullPage: true, type: "jpeg", quality: 55,
      clip: { x: 0, y: top, width: 390, height: Math.min(60000, height - top) } });
}
const visibleText = page => page.evaluate(() => document.body.innerText);

(async () => {
  const browser = await chromium.launch();
  // front page
  let [context, page] = await open(browser, null);
  await page.goto(SITE);
  await shot(page, path.join(OUT, "00_front"));
  fs.writeFileSync(path.join(TEXT, "00_front.txt"), await visibleText(page));
  // guide, both folded parts opened
  await page.click("a[data-guide]");
  await page.evaluate(() => document.querySelectorAll("#guide details").forEach(d => d.open = true));
  await page.evaluate(() => window.scrollTo(0, 0));
  await shot(page, path.join(OUT, "01_guide_open"));
  fs.writeFileSync(path.join(TEXT, "01_guide.txt"), await visibleText(page));
  await context.close();

  for (const [n, name] of PAGES.entries()) {
    const answer = JSON.parse(fs.readFileSync(path.join(__dirname, "answers", name + ".json"), "utf8"));
    [context, page] = await open(browser, answer);
    await page.goto(SITE + "?disease=" + answer.disease.id);
    await page.waitForSelector("#found:not([hidden])");
    for (const tab of ["approved", "trials", "clues"]) {
      await page.click("#tab-" + tab);
      const panel = "#panel-" + tab;
      // as it first opens (boxes as the page leaves them)
      await page.evaluate(() => window.scrollTo(0, 0));
      const stem = `${String(n + 2).padStart(2, "0")}_${name}_${tab}`;
      await shot(page, path.join(OUT, stem + "_as_opened"));
      // every box opened
      await page.evaluate(p => document.querySelectorAll(p + " details:not([hidden])").forEach(d => { d.open = true; d.dispatchEvent(new Event("toggle")); }), panel);
      await page.waitForTimeout(50);
      await shot(page, path.join(OUT, stem + "_all_open"));
      fs.writeFileSync(path.join(TEXT, stem + ".txt"), await visibleText(page));
    }
    await context.close();
  }
  await browser.close();
})();
