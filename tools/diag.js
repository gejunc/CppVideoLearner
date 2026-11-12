'use strict';

/** 连上应用调试端口，打印编译器探测细节。 */

const BASE = `http://127.0.0.1:${process.env.CDP_PORT || 9225}`;

(async () => {
  const res = await fetch(BASE + '/json');
  const pages = await res.json();
  const page = pages.find((p) => p.type === 'page' && p.webSocketDebuggerUrl);
  const ws = new WebSocket(page.webSocketDebuggerUrl);
  await new Promise((r) => ws.addEventListener('open', r));

  let seq = 0;
  const send = (method, params) => new Promise((resolve) => {
    const id = ++seq;
    const onMsg = (ev) => {
      const m = JSON.parse(ev.data);
      if (m.id === id) { ws.removeEventListener('message', onMsg); resolve(m); }
    };
    ws.addEventListener('message', onMsg);
    ws.send(JSON.stringify({ id, method, params }));
  });

  const ev = async (expr) => {
    const r = await send('Runtime.evaluate', { expression: expr, awaitPromise: true, returnByValue: true });
    if (r.result && r.result.exceptionDetails) return { error: r.result.exceptionDetails.exception };
    return r.result.result.value;
  };

  const st = await ev('window.cpp.compilerStatus(true)');
  console.log('compilerStatus:', JSON.stringify(st, null, 1));

  const envInfo = await ev(`(async () => {
    return await window.cpp.runCode({ code: 'int main(){return 0;}' });
  })()`);
  console.log('runCode 简易结果:', JSON.stringify(envInfo, null, 1));

  process.exit(0);
})().catch((e) => { console.error(e); process.exit(1); });
