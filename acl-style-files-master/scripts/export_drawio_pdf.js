#!/usr/bin/env node

// Export hand-drawn .drawio sources to vector PDF through the diagrams.net
// embed.
//
//   node scripts/export_drawio_pdf.js IN.drawio OUT.pdf [WIDTH_IN]
//   node scripts/export_drawio_pdf.js --all
//
// Two things this has to get right:
//
// 1. Each figure is exported at the width it actually occupies on the page. A
//    figure exported at \textwidth but placed in a 0.545\textwidth minipage is
//    rescaled by LaTeX, and every font size inside it shrinks with the scale
//    factor. Keeping export width equal to placed width is what makes a
//    draw.io fontSize predict a printed point size.
// 2. Booting the embedded editor costs well over a minute on a cold cache, so
//    all figures are exported from one browser session rather than one each.

const fs = require("fs");
const http = require("http");
const path = require("path");
const { chromium } = require("playwright");

const FIGURES = path.join(__dirname, "..", "figures");
const TEXT_WIDTH_IN = 6.323; // \textwidth = 455.24 pt

// Placed width must match the \includegraphics width in paper.tex.
//
// paper.tex now ships the hand-authored PDFs from figures/final2/, so running
// this script overwrites Figures 1(a) and 2 with the generated artwork instead.
const ALL = [
  ["fig1a_concept", 0.545 * TEXT_WIDTH_IN], // minipage in the Fig. 1 figure*
  ["fig2_pipeline", TEXT_WIDTH_IN],
];

function parseArgs() {
  const argv = process.argv.slice(2);
  if (argv[0] === "--all") {
    return ALL.map(([stem, width]) => ({
      input: path.join(FIGURES, `${stem}.drawio`),
      output: path.join(FIGURES, `${stem}.pdf`),
      width,
    }));
  }
  const [input, output, widthArg] = argv;
  if (!input || !output) {
    throw new Error(
      "usage: export_drawio_pdf.js INPUT.drawio OUTPUT.pdf [WIDTH_IN] | --all"
    );
  }
  const width = widthArg ? Number(widthArg) : TEXT_WIDTH_IN;
  if (!Number.isFinite(width) || width <= 0) {
    throw new Error(`bad width: ${widthArg}`);
  }
  return [{ input, output, width }];
}

const HOST_PAGE = `<!doctype html>
<html><body style="margin:0">
<iframe id="drawio" style="border:0;width:100vw;height:100vh"
  src="https://embed.diagrams.net/?embed=1&proto=json&spin=1&ui=min&libraries=0&grid=0"></iframe>
<script>
const iframe = document.getElementById("drawio");
const origin = "https://embed.diagrams.net";
let pending = null;
function send(message) {
  iframe.contentWindow.postMessage(JSON.stringify(message), origin);
}
window.exportXml = (xml) => new Promise((resolve) => {
  pending = resolve;
  send({ action: "load", xml });
});
window.addEventListener("message", (event) => {
  if (event.source !== iframe.contentWindow || event.origin !== origin) return;
  let message = event.data;
  if (typeof message === "string") {
    try { message = JSON.parse(message); } catch { return; }
  }
  if (message.event === "init") {
    window.ready();
  } else if (message.event === "load") {
    send({ action: "export", format: "pdf", crop: true, border: 0, scale: 1 });
  } else if (message.event === "export" && message.data && pending) {
    const resolve = pending;
    pending = null;
    resolve(message.data);
  }
});
</script></body></html>`;

async function main() {
  const jobs = parseArgs();

  const server = http.createServer((request, response) => {
    response.writeHead(200, { "Content-Type": "text/html; charset=utf-8" });
    response.end(HOST_PAGE);
  });
  await new Promise((resolve) => server.listen(0, "127.0.0.1", resolve));
  const { port } = server.address();

  const browser = await chromium.launch({
    executablePath:
      "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    headless: true,
  });
  const page = await browser.newPage({ viewport: { width: 2100, height: 900 } });
  const booted = new Promise((resolve) => page.exposeFunction("ready", resolve));
  await page.goto(`http://127.0.0.1:${port}`, { waitUntil: "domcontentloaded" });
  await Promise.race([
    booted,
    new Promise((_, reject) =>
      setTimeout(() => reject(new Error("editor never initialised")), 150000)
    ),
  ]);

  const printPage = await browser.newPage({ viewport: { width: 900, height: 300 } });

  for (const { input, output, width } of jobs) {
    const xml = fs.readFileSync(input, "utf8");
    const dataUrl = await Promise.race([
      page.evaluate((source) => window.exportXml(source), xml),
      new Promise((_, reject) =>
        setTimeout(() => reject(new Error(`export timed out: ${input}`)), 120000)
      ),
    ]);

    const payload = dataUrl.substring(dataUrl.indexOf(",") + 1);
    const svg = dataUrl.includes(";base64,")
      ? Buffer.from(payload, "base64")
      : Buffer.from(decodeURIComponent(payload), "utf8");
    fs.writeFileSync(`${output}.svg`, svg);

    // Size the page to the placed width and to the drawing's own aspect ratio.
    // A fixed page height letterboxes the figure, and LaTeX then scales that
    // dead space onto the page along with the artwork.
    const svgText = svg.toString("utf8");
    const dimensions = /<svg[^>]*?width="([\d.]+)px"[^>]*?height="([\d.]+)px"/.exec(
      svgText
    );
    if (!dimensions) {
      throw new Error(`could not read intrinsic SVG dimensions: ${input}`);
    }
    const [pxW, pxH] = [Number(dimensions[1]), Number(dimensions[2])];
    if (pxW < 50) {
      throw new Error(
        `${input}: exported ${pxW}x${pxH} px, so the editor rejected the XML`
      );
    }
    const heightIn = ((width * pxH) / pxW).toFixed(4);
    const ptPerPx = (width * 72) / pxW;
    console.log(
      `${path.basename(input)}: ${pxW}x${pxH} px -> ` +
        `${width.toFixed(3)}x${heightIn} in; 1 px = ${ptPerPx.toFixed(4)} pt ` +
        `(8 pt needs ${(8 / ptPerPx).toFixed(1)} px)`
    );

    await printPage.setContent(
      `<!doctype html><html><head><style>
        @page { size: ${width}in ${heightIn}in; margin: 0; }
        html, body { width: ${width}in; height: ${heightIn}in; margin: 0; padding: 0; }
        svg { display: block; width: ${width}in !important; height: ${heightIn}in !important; }
      </style></head><body>${svgText}</body></html>`,
      { waitUntil: "load" }
    );
    await printPage.pdf({
      path: output,
      width: `${width}in`,
      height: `${heightIn}in`,
      printBackground: true,
      margin: { top: "0", right: "0", bottom: "0", left: "0" },
    });
  }

  await browser.close();
  server.close();
}

main().catch((error) => {
  console.error(error);
  process.exit(1);
});
