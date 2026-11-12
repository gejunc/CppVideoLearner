'use strict';

/** 直接从应用页面截图（不受窗口遮挡影响）。用法：node tools/shot-app.js <端口> <输出文件> */

const fs = require('node:fs');
const path = require('node:path');

const PORT = process.env.CDP_PORT || process.argv[2] || 9231;
const OUT = process.argv[3] || path.join(__dirname, '..', '.tmp', 'app-shot.png');

(async () => {
  const res = await fetch(`http://127.0.0.1:${PORT}/json`);
  const pages = await res.json();
  const page = pages.find((p) => p.type === 'page');
  const ws = new WebSocket(page.webSocketDebuggerUrl);
  await new Promise((r) => ws.addEventListener('open', r));

  let seq = 0;
  const send = (method, params) => new Promise((resolve) => {
    const id = ++seq;
    const h = (e) => {
      const m = JSON.parse(e.data);
      if (m.id === id) { ws.removeEventListener('message', h); resolve(m); }
    };
    ws.addEventListener('message', h);
    ws.send(JSON.stringify({ id, method, params }));
  });

  await send('Page.enable');
  const r = await send('Page.captureScreenshot', { format: 'png' });
  const buf = Buffer.from(r.result.data, 'base64');
  fs.writeFileSync(OUT, buf);
  console.log('已保存', OUT, Math.round(buf.length / 1024) + ' KB');
  process.exit(0);
})().catch((e) => { console.error(e.message); process.exit(1); });
