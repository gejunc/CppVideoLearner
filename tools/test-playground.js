'use strict';

/**
 * 代码台的端到端自测：通过 CDP 模拟真实的点击流程。
 * 需要应用以 --remote-debugging-port 启动。
 */

const BASE = `http://127.0.0.1:${process.env.CDP_PORT || 9225}`;
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

let ws;
let seq = 0;

function send(method, params) {
  return new Promise((resolve, reject) => {
    const id = ++seq;
    const timer = setTimeout(() => reject(new Error('timeout ' + method)), 40000);
    const onMsg = (ev) => {
      let msg;
      try { msg = JSON.parse(ev.data); } catch { return; }
      if (msg.id === id) {
        clearTimeout(timer);
        ws.removeEventListener('message', onMsg);
        resolve(msg);
      }
    };
    ws.addEventListener('message', onMsg);
    ws.send(JSON.stringify({ id, method, params }));
  });
}

async function evalJs(expr) {
  const r = await send('Runtime.evaluate', {
    expression: expr, awaitPromise: true, returnByValue: true,
  });
  if (r.result && r.result.exceptionDetails) {
    throw new Error('JS 异常: ' + JSON.stringify(r.result.exceptionDetails.exception));
  }
  return r.result && r.result.result ? r.result.result.value : undefined;
}

async function connect() {
  for (let i = 0; i < 40; i++) {
    try {
      const res = await fetch(BASE + '/json');
      const pages = await res.json();
      const page = pages.find((p) => p.type === 'page' && p.webSocketDebuggerUrl);
      if (page) {
        ws = new WebSocket(page.webSocketDebuggerUrl);
        await new Promise((res2, rej) => {
          ws.addEventListener('open', res2);
          ws.addEventListener('error', rej);
        });
        await send('Runtime.enable');
        return page.url;
      }
    } catch { /* 等等 */ }
    await sleep(500);
  }
  throw new Error('连不上调试端口');
}

const results = [];
function check(name, ok, detail) {
  results.push({ name, ok });
  console.log(`${ok ? 'PASS' : 'FAIL'}  ${name}${detail ? '  -> ' + detail : ''}`);
}

async function waitFor(expr, timeout = 20000, interval = 300) {
  const t0 = Date.now();
  while (Date.now() - t0 < timeout) {
    if (await evalJs(expr)) return true;
    await sleep(interval);
  }
  return false;
}

async function main() {
  const url = await connect();
  console.log('页面:', url);

  await waitFor('!!(window.COURSE_DATA && document.querySelector(".ls"))');

  // 1. 从「代码示例」点「去代码台」
  const hasTry = await evalJs('!!document.querySelector("#pane-code .try")');
  check('代码示例里出现「去代码台」按钮', hasTry);
  if (!hasTry) throw new Error('没有去代码台按钮，后续无法测试');

  await evalJs('document.querySelector("#pane-code .try").click()');
  await sleep(600);

  const opened = await evalJs('document.querySelector("#drawer").classList.contains("open")');
  check('抽屉打开', opened);

  const editorLen = await evalJs('document.querySelector("#editor").value.length');
  check('编辑器已填入代码', editorLen > 20, `${editorLen} 字符`);

  // 2. 编译器徽章
  const badgeOk = await waitFor(
    'document.querySelector("#compiler-badge").classList.contains("ok") || document.querySelector("#compiler-badge").classList.contains("bad")',
    25000);
  const badge = await evalJs('document.querySelector("#compiler-badge").textContent');
  check('编译器状态已显示', badgeOk, badge);
  const hasGpp = await evalJs('document.querySelector("#compiler-badge").classList.contains("ok")');
  check('检测到 g++', hasGpp, badge);

  // 3. 运行一段确定性的代码
  await evalJs(`(() => {
    const ed = document.querySelector('#editor');
    ed.value = '#include <iostream>\\nint main() { std::cout << 6 * 7 << std::endl; return 0; }';
    ed.dispatchEvent(new Event('input', { bubbles: true }));
    return true;
  })()`);
  await evalJs('document.querySelector("#btn-run").click()');

  const done = await waitFor('document.querySelector("#run-status").textContent.includes("✓") || document.querySelector("#run-status").textContent.includes("失败") || document.querySelector("#run-status").textContent.includes("崩溃")', 40000);
  const out1 = await evalJs('document.querySelector("#run-output").textContent');
  const st1 = await evalJs('document.querySelector("#run-status").textContent');
  check('运行成功并输出 42', done && (out1 || '').trim() === '42', `${st1} | 输出: ${JSON.stringify(out1)}`);

  // 4. 编译错误要显示 g++ 的报错
  await evalJs(`(() => {
    const ed = document.querySelector('#editor');
    ed.value = 'int main() { return unknown_thing; }';
    ed.dispatchEvent(new Event('input', { bubbles: true }));
    return true;
  })()`);
  await evalJs('document.querySelector("#btn-run").click()');
  await waitFor('document.querySelector("#run-status").textContent.includes("编译失败") || document.querySelector("#run-status").textContent.includes("✓")', 40000);
  const out2 = await evalJs('document.querySelector("#run-output").textContent');
  check('编译错误有 g++ 报错信息', /error:/.test(out2 || ''), (out2 || '').split('\n')[0]);

  // 5. 语法高亮层
  const hlLen = await evalJs('document.querySelector("#hl").innerHTML.length');
  check('编辑器高亮层有内容', hlLen > 10, `${hlLen} 字符`);

  // 6. 行号
  const gutter = await evalJs('document.querySelector("#gutter").textContent.trim()');
  check('行号已渲染', gutter.startsWith('1'), gutter.replace(/\n/g, ','));

  // 7. 标准输入
  await evalJs(`(() => {
    const ed = document.querySelector('#editor');
    ed.value = '#include <iostream>\\nint main(){ std::string n; std::cin >> n; std::cout << "hi " << n; }';
    ed.dispatchEvent(new Event('input', { bubbles: true }));
    document.querySelector('#run-stdin').value = 'World';
    return true;
  })()`);
  await evalJs('document.querySelector("#btn-run").click()');
  await waitFor('document.querySelector("#run-status").textContent.includes("✓") || document.querySelector("#run-status").textContent.includes("失败")', 40000);
  const out3 = await evalJs('document.querySelector("#run-output").textContent');
  check('标准输入可用', (out3 || '').includes('hi World'), (out3 || '').trim());

  // 8. 关闭抽屉
  await evalJs('document.querySelector("#btn-close-drawer").click()');
  await sleep(500);
  const closed = await evalJs('!document.querySelector("#drawer").classList.contains("open")');
  check('抽屉可关闭', closed);

  // 9. 练习题 tab 切换
  const exTab = await evalJs('!!document.querySelector(\'.tab[data-tab="ex"]\')');
  check('存在练习题 tab', exTab);
  if (exTab) {
    await evalJs('document.querySelector(\'.tab[data-tab="ex"]\').click()');
    await sleep(400);
    const exVisible = await evalJs('!document.querySelector("#pane-ex").classList.contains("hidden")');
    check('练习题面板可切换', exVisible);
    const exCount = await evalJs('document.querySelectorAll("#pane-ex .ex-item").length');
    check('练习题已渲染', exCount > 0, `${exCount} 题`);
  }

  const fail = results.filter((r) => !r.ok).length;
  console.log(`\n通过 ${results.length - fail} / ${results.length}`);
  process.exit(fail ? 1 : 0);
}

main().catch((e) => {
  console.error('自测失败:', e.message);
  process.exit(2);
});
