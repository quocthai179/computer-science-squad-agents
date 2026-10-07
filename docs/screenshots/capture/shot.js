// usage: node shot.js in.html out.png
const { chromium } = require('playwright');
(async () => {
  const [inp, out] = process.argv.slice(2);
  const browser = await chromium.launch();
  const page = await browser.newPage({ deviceScaleFactor: 2, viewport: { width: 1400, height: 900 } });
  await page.goto('file://' + require('path').resolve(inp));
  await page.waitForTimeout(300);
  const body = await page.$('body');
  await body.screenshot({ path: out });
  await browser.close();
})();
