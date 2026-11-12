'use strict';

/** 检查平台标记与字体是否按平台切换。用法：node tools/check-platform.js [端口] */

const PORT = process.env.CDP_PORT || process.argv[2] || 9230;

(async () => {
  const res = await fetch(`http://127.0.0.1:${PORT}/json`);
  const pages = await res.json();
  const page = pages.find((p) => p.type === 'page');
  const ws = new WebSocket(page.webSocketDebuggerUrl);
  await new Promise((r) => ws.addEventListener('open', r));

  let seq = 0;
  const ev = (expr) => new Promise((resolve) => {
    const id = ++seq;
    const h = (e) => {
      const m = JSON.parse(e.data);
      if (m.id === id) {
        ws.removeEventListener('message', h);
        resolve(m.result && m.result.result ? m.result.result.value : undefined);
      }
    };
    ws.addEventListener('message', h);
    ws.send(JSON.stringify({
      id, method: 'Runtime.evaluate',
      params: { expression: expr, returnByValue: true, awaitPromise: true },
    }));
  });

  console.log('body class          :', await ev('document.body.className'));
  console.log('html data-platform  :', await ev('document.documentElement.dataset.platform'));
  console.log('标题栏 padding-left :', await ev('getComputedStyle(document.querySelector(".titlebar")).paddingLeft'));
  console.log('正文字体            :', await ev('getComputedStyle(document.body).fontFamily'));
  console.log('等宽字体变量        :', await ev('getComputedStyle(document.documentElement).getPropertyValue("--mono").trim()'));
  process.exit(0);
})().catch((e) => { console.error(e.message); process.exit(1); });
