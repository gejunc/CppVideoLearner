'use strict';

/**
 * 用 CDP 操作界面并截图，产出文档用图。
 * 用法：node tools/demo-shot.js [端口]
 */

const fs = require('node:fs');
const path = require('node:path');

const PORT = process.env.CDP_PORT || process.argv[2] || 9226;
const OUT = path.join(__dirname, '..', 'docs');
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

let ws;
let seq = 0;

function send(method, params) {
  return new Promise((resolve, reject) => {
    const id = ++seq;
    const timer = setTimeout(() => reject(new Error('timeout ' + method)), 30000);
    const onMsg = (ev) => {
      const m = JSON.parse(ev.data);
      if (m.id === id) {
        clearTimeout(timer);
        ws.removeEventListener('message', onMsg);
        resolve(m);
      }
    };
    ws.addEventListener('message', onMsg);
    ws.send(JSON.stringify({ id, method, params }));
  });
}

async function ev(expr) {
  const r = await send('Runtime.evaluate', { expression: expr, awaitPromise: true, returnByValue: true });
  if (r.result && r.result.exceptionDetails) {
    throw new Error('JS: ' + JSON.stringify(r.result.exceptionDetails.exception));
  }
  return r.result.result.value;
}

async function shot(name) {
  const r = await send('Page.captureScreenshot', { format: 'png', captureBeyondViewport: false });
  const buf = Buffer.from(r.result.data, 'base64');
  fs.writeFileSync(path.join(OUT, name), buf);
  console.log('saved', name, Math.round(buf.length / 1024) + ' KB');
}

(async () => {
  const res = await fetch(`http://127.0.0.1:${PORT}/json`);
  const pages = await res.json();
  const page = pages.find((p) => p.type === 'page' && p.webSocketDebuggerUrl);
  ws = new WebSocket(page.webSocketDebuggerUrl);
  await new Promise((r) => ws.addEventListener('open', r));
  await send('Page.enable');
  await send('Runtime.enable');

  // 等到首页就绪
  for (let i = 0; i < 40; i++) {
    if (await ev('!!(window.COURSE_DATA && document.querySelector(".ls"))')) break;
    await sleep(300);
  }

  // ---- 图 1：练习题展开
  await ev('document.querySelector(\'.tab[data-tab="ex"]\').click()');
  await sleep(500);
  await ev('document.querySelector("#pane-ex .ex-head").click()');
  await sleep(900);
  await shot('shot-exercise.png');

  // ---- 图 2：代码台跑一段代码
  const demoCode = [
    '#include <iostream>',
    '#include <vector>',
    '',
    'int main() {',
    '    std::vector<int> v{3, 1, 4, 1, 5, 9, 2, 6};',
    '    long long sum = 0;',
    '    for (int x : v) sum += x;',
    '    std::cout << "sum = " << sum << std::endl;',
    '    return 0;',
    '}',
  ].join('\n');
  await ev(`openDrawer(${JSON.stringify(demoCode)})`);
  await sleep(700);
  await ev('document.querySelector("#btn-run").click()');
  for (let i = 0; i < 40; i++) {
    const st = await ev('document.querySelector("#run-status").textContent');
    if (st.includes('✓') || st.includes('失败') || st.includes('崩溃')) break;
    await sleep(400);
  }
  await sleep(600);
  await shot('shot-playground.png');

  // ---- 图 3：关掉抽屉，回到主界面（第 27 课并发那节）
  await ev('closeDrawer()');
  await ev('document.querySelectorAll(".ls")[26].click()');
  await sleep(2500);
  await shot('screenshot.png');

  process.exit(0);
})().catch((e) => { console.error('失败:', e.message); process.exit(1); });
