'use strict';

/**
 * 用 Chrome DevTools Protocol 对界面做一次交互自测。
 * 需要先以 --remote-debugging-port=9222 启动 Chrome。
 */

const BASE = `http://127.0.0.1:${process.env.CDP_PORT || 9222}`;
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

// 读取持久化状态：Electron 下走 IPC 写文件，浏览器下走 localStorage
const READ_STATE = `(async () => {
  if (window.cpp) { try { return await window.cpp.loadState(); } catch (e) { return {}; } }
  try { return JSON.parse(localStorage.getItem('cpp-learn-state') || '{}'); } catch (e) { return {}; }
})()`;

let ws;
let seq = 0;

function send(method, params) {
  return new Promise((resolve, reject) => {
    const id = ++seq;
    const timer = setTimeout(() => reject(new Error(`timeout: ${method}`)), 15000);
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
        await new Promise((resolve, reject) => {
          ws.addEventListener('open', resolve);
          ws.addEventListener('error', reject);
        });
        await send('Runtime.enable');
        return page.url;
      }
    } catch { /* 还没起来 */ }
    await sleep(500);
  }
  throw new Error('无法连接 Chrome 调试端口');
}

const results = [];
function check(name, ok, detail) {
  results.push({ name, ok, detail });
  console.log(`${ok ? 'PASS' : 'FAIL'}  ${name}${detail ? '  -> ' + detail : ''}`);
}

async function main() {
  const url = await connect();
  console.log('页面:', url);

  // 清掉上次残留的状态，保证从干净环境开始
  await evalJs('localStorage.clear(); true').catch(() => {});
  await evalJs('location.reload(); true').catch(() => {});
  await sleep(2200);

  // 等待课程数据与首屏渲染完成
  for (let i = 0; i < 40; i++) {
    const ready = await evalJs('!!(window.COURSE_DATA && document.querySelector(".ls"))');
    if (ready) break;
    await sleep(300);
  }

  const lessonCount = await evalJs('document.querySelectorAll(".ls").length');
  check('课时渲染数量 = 50', lessonCount === 50, String(lessonCount));

  const chapCount = await evalJs('document.querySelectorAll(".ch").length');
  check('章节渲染数量 = 14', chapCount === 14, String(chapCount));

  // 首个课时自动打开
  const firstActive = await evalJs('document.querySelector(".ls.active .ls-name").textContent');
  check('默认打开第一课', /C\+\+ 是什么/.test(firstActive || ''), firstActive);

  // 视频源指向正确文件
  const src = await evalJs('decodeURIComponent(document.querySelector("#video").src).split("/").pop()');
  check('视频源 = l01.mp4', src === 'l01.mp4', src);

  // 点击第 10 个课时
  await evalJs('document.querySelectorAll(".ls")[9].click()');
  await sleep(600);
  const title10 = await evalJs('document.querySelector("#lesson-title").textContent');
  const crumb10 = await evalJs('document.querySelector("#crumb").textContent');
  const id10 = await evalJs('document.querySelector(".ls.active").dataset.id');
  check('切换到第 10 个课时', /函数定义/.test(title10 || ''), `${crumb10} ${title10}`);

  // 视频源随之切换
  const src10 = await evalJs('decodeURIComponent(document.querySelector("#video").src).split("/").pop()');
  check(`视频源 = ${id10}.mp4`, src10 === `${id10}.mp4`, src10);

  // 代码示例存在且高亮生效
  const codeN = await evalJs('document.querySelectorAll(".code-item").length');
  const kwN = await evalJs('document.querySelectorAll(".code-item pre .k, .code-item pre .ty").length');
  check('代码示例已渲染', codeN > 0, `片段 ${codeN}`);
  check('代码高亮生效', kwN > 0, `着色标记 ${kwN}`);

  // 练习题：每课 2 道，默认折叠，点击展开答案
  const exN = await evalJs('document.querySelectorAll("#pane-ex .ex-item").length');
  check('练习题已渲染（每课 2 道）', exN === 2, `${exN} 题`);

  const collapsed = await evalJs('document.querySelectorAll("#pane-ex .ex-body.hidden").length');
  check('答案默认折叠', collapsed === exN, `${collapsed}/${exN} 折叠`);

  await evalJs('document.querySelector("#pane-ex .ex-head").click()');
  await sleep(400);
  const openedBody = await evalJs('!document.querySelector("#pane-ex .ex-body").classList.contains("hidden")');
  const answerText = await evalJs('document.querySelector("#pane-ex .ex-body pre")?.textContent || ""');
  check('点击后展开参考答案', openedBody && answerText.length > 20, `${answerText.length} 字符`);

  const tryInEx = await evalJs('!!document.querySelector("#pane-ex .ex-body .try")');
  check('答案里带「去代码台」', tryInEx);

  // 笔记：输入后自动保存
  await evalJs(`(() => {
    const ta = document.querySelector('#note');
    ta.value = '自测笔记：指针与引用';
    ta.dispatchEvent(new Event('input', { bubbles: true }));
    return true;
  })()`);
  await sleep(1400);
  const saved = await evalJs(
    `(async () => { const s = await ${READ_STATE}; return ((s.notes || {})[${JSON.stringify(id10)}]) || ""; })()`);
  check('笔记自动保存', saved === '自测笔记：指针与引用', saved);

  // 标记已学：切换 active 课时上的完成状态
  const doneBefore = await evalJs(
    'document.querySelector(".ls.active").classList.contains("done")');
  await evalJs('document.querySelector("#btn-done").click()');
  await sleep(700);
  const doneAfter = await evalJs(
    'document.querySelector(".ls.active").classList.contains("done")');
  check('标记已学切换', doneBefore !== doneAfter, `${doneBefore} -> ${doneAfter}`);

  // 再点一次应恢复
  await evalJs('document.querySelector("#btn-done").click()');
  await sleep(500);
  const doneBack = await evalJs(
    'document.querySelector(".ls.active").classList.contains("done")');
  check('再次点击取消标记', doneBack === doneBefore, `${doneAfter} -> ${doneBack}`);

  // 顶部统计应随进度变化
  await evalJs('document.querySelector("#btn-done").click()');
  await sleep(600);
  const tb1 = await evalJs('document.querySelector("#tb-progress").textContent');
  check('统计显示已学课时', /已学 1/.test(tb1 || ''), tb1);
  await evalJs('document.querySelector("#btn-done").click()');
  await sleep(400);

  // 搜索过滤
  await evalJs(`(() => {
    const q = document.querySelector('#q');
    q.value = '指针';
    q.dispatchEvent(new Event('input', { bubbles: true }));
    return true;
  })()`);
  await sleep(400);
  const visible = await evalJs(
    'Array.from(document.querySelectorAll(".ls")).filter(e => e.style.display !== "none").length');
  check('搜索"指针"能过滤', visible > 0 && visible < 26, `命中 ${visible}`);

  // 清空搜索
  await evalJs(`(() => {
    const q = document.querySelector('#q');
    q.value = '';
    q.dispatchEvent(new Event('input', { bubbles: true }));
    return true;
  })()`);
  await sleep(300);

  // 键盘快捷键：S 切换字幕
  const subBefore = await evalJs(
    `(async () => { const s = await ${READ_STATE}; return (s.settings || {}).subtitles; })()`);
  await evalJs(`document.body.focus(); document.dispatchEvent(
    new KeyboardEvent('keydown', { key: 's', bubbles: true }))`);
  await sleep(700);
  const subAfter = await evalJs(
    `(async () => { const s = await ${READ_STATE}; return (s.settings || {}).subtitles; })()`);
  check('S 键切换字幕', subBefore !== subAfter, `${subBefore} -> ${subAfter}`);

  // 上一课 / 下一课按钮
  await evalJs('document.querySelector("#btn-next").click()');
  await sleep(500);
  const t2 = await evalJs('document.querySelector("#lesson-title").textContent');
  check('下一课按钮', t2 !== title10, t2);

  // 进度环与统计
  const tb = await evalJs('document.querySelector("#tb-progress").textContent');
  check('顶部统计有内容', /共|已学/.test(tb || ''), tb);

  const fail = results.filter((r) => !r.ok).length;
  console.log(`\n通过 ${results.length - fail} / ${results.length}`);
  process.exit(fail ? 1 : 0);
}

main().catch((e) => {
  console.error('自测失败:', e.message);
  process.exit(2);
});
