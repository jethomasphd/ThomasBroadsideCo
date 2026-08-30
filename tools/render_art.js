// Renders art_src/*.svg to exact-size PNGs via Playwright (the chromium
// CLI screenshot clips tall pages; Playwright's viewport doesn't).
// Called by tools/render_art.py — not directly.
//   node tools/render_art.js <svgPath> <pngPath> <w> <h> <scale>
const { chromium } = require('playwright');

(async () => {
  const [svgPath, pngPath, w, h, scale] = process.argv.slice(2);
  const exe = process.env.CHROMIUM || '/opt/pw-browsers/chromium';
  const browser = await chromium.launch({ executablePath: exe });
  const page = await browser.newPage({
    viewport: { width: parseInt(w), height: parseInt(h) },
    deviceScaleFactor: parseFloat(scale),
  });
  await page.goto('file://' + svgPath, { waitUntil: 'networkidle' });
  await page.waitForTimeout(250); // font settle
  await page.screenshot({ path: pngPath });
  await browser.close();
})();
