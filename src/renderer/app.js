'use strict';

/* ============================================================
   C++ 视频学习 — 渲染进程逻辑
   ============================================================ */

const $ = (s) => document.querySelector(s);

const els = {
  tbProgress: $('#tb-progress'),
  courseMeta: $('#course-meta'),
  footInfo: $('#foot-info'),
  chapters: $('#chapters'),
  q: $('#q'),
  video: $('#video'),
  subtitle: $('#subtitle'),
  empty: $('#empty'),
  resumeTip: $('#resume-tip'),
  crumb: $('#crumb'),
  lessonTitle: $('#lesson-title'),
  lessonDur: $('#lesson-dur'),
  tags: $('#tags'),
  btnPrev: $('#btn-prev'),
  btnDone: $('#btn-done'),
  btnNext: $('#btn-next'),
  paneCode: $('#pane-code'),
  paneEx: $('#pane-ex'),
  exCount: $('#ex-count'),
  codeHint: $('#code-hint'),
  note: $('#note'),
  noteState: $('#note-state'),
  ringFg: $('#ring-fg'),
  ringPct: $('#ring-pct'),
  barFill: $('#bar-fill'),
  toast: $('#toast'),
  // 代码台
  drawer: $('#drawer'),
  drawerMask: $('#drawer-mask'),
  editor: $('#editor'),
  hl: $('#hl'),
  gutter: $('#gutter'),
  runOutput: $('#run-output'),
  runStatus: $('#run-status'),
  runStdin: $('#run-stdin'),
  btnRun: $('#btn-run'),
  btnResetCode: $('#btn-reset-code'),
  btnCloseDrawer: $('#btn-close-drawer'),
  stdSelect: $('#std-select'),
  compilerBadge: $('#compiler-badge'),
};

const RING_LEN = 113;

// 平台标记：macOS 的红绿灯按钮占左上角，标题栏要给它让位
(function tagPlatform() {
  let p = '';
  if (window.cpp && window.cpp.platform) {
    p = window.cpp.platform;
  } else if (typeof navigator !== 'undefined') {
    const s = (navigator.platform || '') + ' ' + (navigator.userAgent || '');
    if (/mac/i.test(s)) p = 'darwin';
    else if (/linux/i.test(s)) p = 'linux';
    else p = 'win32';
  }
  document.documentElement.dataset.platform = p;
  document.addEventListener('DOMContentLoaded', () => {
    document.body.classList.add('platform-' + p);
  });
})();

// 环境适配：Electron 内用 preload 暴露的接口，直接用浏览器打开则走 localStorage
const IS_ELECTRON = !!window.cpp;
const store = IS_ELECTRON ? {
  load: () => window.cpp.loadState(),
  save: (s) => window.cpp.saveState(s),
  videoUrl: (rel) => window.cpp.videoUrl(rel),
} : {
  load: async () => {
    try { return JSON.parse(localStorage.getItem('cpp-learn-state') || '{}'); }
    catch { return {}; }
  },
  save: async (s) => {
    try { localStorage.setItem('cpp-learn-state', JSON.stringify(s)); return true; }
    catch { return false; }
  },
  videoUrl: (rel) => `../../assets/${rel}`,
};

let course = null;
let flat = [];                  // 扁平课时列表
let byId = new Map();
let chapterEls = new Map();
let current = null;             // 当前课时对象
let state = { progress: {}, notes: {}, settings: {}, lastLesson: null };
let subs = [];                  // 当前字幕 [{s, e, text}]
let saveTimer = null;
let noteTimer = null;
let lastSaveAt = 0;
let resumePending = 0;

// ------------------------------------------------------------ 工具
function fmtTime(sec) {
  sec = Math.max(0, Math.round(sec || 0));
  const m = Math.floor(sec / 60);
  const s = sec % 60;
  return `${m}:${String(s).padStart(2, '0')}`;
}

function fmtDuration(sec) {
  if (!sec) return '—';
  const m = Math.round(sec / 60);
  return m >= 1 ? `${m} 分钟` : `${Math.round(sec)} 秒`;
}

function toast(msg) {
  els.toast.textContent = msg;
  els.toast.classList.add('show');
  clearTimeout(toast._t);
  toast._t = setTimeout(() => els.toast.classList.remove('show'), 1800);
}

function esc(s) {
  return s.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
}

// ------------------------------------------------------------ C++ 高亮
const KW = new Set(('if else for while do switch case default break continue return goto ' +
  'try catch throw new delete using namespace public private protected class struct enum ' +
  'union template typename virtual override final static const constexpr inline explicit ' +
  'friend operator this nullptr true false sizeof decltype noexcept mutable volatile extern ' +
  'auto co_await co_return co_yield static_cast dynamic_cast const_cast reinterpret_cast ' +
  'typedef alignas alignof static_assert and or not').split(' '));

const TY = new Set(('int double float char bool void long short unsigned signed wchar_t ' +
  'size_t ptrdiff_t string vector map set array pair unique_ptr shared_ptr weak_ptr ' +
  'make_unique make_shared ifstream ofstream fstream istringstream ostringstream exception ' +
  'runtime_error invalid_argument out_of_range cout cin cerr endl std string_view greater ' +
  'int8_t int16_t int32_t int64_t uint8_t uint32_t thread mutex lock_guard').split(' '));

const TOK_RE = /(\/\/[^\n]*)|("(?:\\.|[^"\\])*"|'(?:\\.|[^'\\])*')|(^[ \t]*#[^\n]*)|(\b(?:0[xX][0-9a-fA-F]+|\d+\.?\d*(?:[eE][+-]?\d+)?)[uUlLfF]*\b)|([A-Za-z_]\w*)|([{}()\[\];,.<>+\-*/%=!&|^~?:])|(\s+)/gm;

function highlightCpp(code) {
  let out = '';
  let last = 0;
  TOK_RE.lastIndex = 0;
  let m;
  while ((m = TOK_RE.exec(code)) !== null) {
    if (m.index > last) out += esc(code.slice(last, m.index));
    const t = m[0];
    let cls = '';
    if (m[1]) cls = 'cm';
    else if (m[2]) cls = 's';
    else if (m[3]) cls = 'pp';
    else if (m[4]) cls = 'n';
    else if (m[5]) {
      if (KW.has(t)) cls = 'k';
      else if (TY.has(t)) cls = 'ty';
      else if (code[m.index + t.length] === '(') cls = '';
      else cls = '';
    } else if (m[6]) cls = '';
    out += cls ? `<span class="${cls}">${esc(t)}</span>` : esc(t);
    last = m.index + t.length;
  }
  out += esc(code.slice(last));
  return out;
}

// ------------------------------------------------------------ 状态
function saveState(immediate = false) {
  const doIt = () => {
    lastSaveAt = Date.now();
    store.save({
      progress: state.progress,
      notes: state.notes,
      settings: state.settings,
      lastLesson: current ? current.id : state.lastLesson,
    }).catch(() => {});
  };
  if (immediate) {
    clearTimeout(saveTimer);
    saveTimer = null;
    doIt();
    return;
  }
  if (Date.now() - lastSaveAt > 4000) {
    doIt();
    return;
  }
  if (saveTimer) return;
  saveTimer = setTimeout(() => { saveTimer = null; doIt(); }, 1500);
}

function lessonProg(id) {
  return state.progress[id] || { t: 0, d: 0, done: false };
}

function ratioOf(id) {
  const p = lessonProg(id);
  if (p.done) return 1;
  if (!p.d || !p.t) return 0;
  return Math.min(0.99, p.t / p.d);
}

function updateStats() {
  const total = flat.length;
  const doneCount = flat.filter((l) => lessonProg(l.id).done).length;
  const watched = flat.reduce((a, l) => a + Math.min(lessonProg(l.id).t || 0, l.duration || 0), 0);
  const pct = total ? doneCount / total : 0;

  els.ringFg.style.strokeDashoffset = String(RING_LEN * (1 - pct));
  els.ringPct.textContent = `${Math.round(pct * 100)}%`;
  els.barFill.style.width = `${pct * 100}%`;
  els.tbProgress.textContent = doneCount
    ? `已学 ${doneCount} / ${total} 课 · 累计 ${Math.round(watched / 60)} 分钟`
    : `共 ${total} 课 · 累计 ${Math.round(watched / 60)} 分钟`;
  els.courseMeta.textContent = `${total} 节课 · ${course.chapters.length} 章 · ${course.total_duration
    ? Math.round(course.total_duration / 60) : 0} 分钟`;
}

// ------------------------------------------------------------ 侧栏
function buildSidebar() {
  els.chapters.innerHTML = '';
  chapterEls.clear();

  course.chapters.forEach((ch) => {
    const wrap = document.createElement('div');
    wrap.className = 'ch';
    wrap.dataset.ch = ch.id;

    const head = document.createElement('div');
    head.className = 'ch-head';
    head.innerHTML = `
      <svg class="ch-arrow" viewBox="0 0 24 24"><path d="M7 10l5 5 5-5z"/></svg>
      <span class="ch-title">${esc(ch.title)}</span>
      <span class="ch-count"></span>`;
    head.addEventListener('click', () => {
      wrap.classList.toggle('collapsed');
    });

    const list = document.createElement('div');
    list.className = 'lessons';

    ch.lessons.forEach((ls) => {
      const el = document.createElement('div');
      el.className = 'ls';
      el.dataset.id = ls.id;
      el.innerHTML = `
        <span class="ls-idx">${String(ls.index).padStart(2, '0')}</span>
        <span class="ls-main"><span class="ls-name"></span></span>
        <span class="ls-flag"></span>
        <span class="ls-prog"><i></i></span>`;
      el.querySelector('.ls-name').textContent = ls.title;
      el.title = `${ch.title} · ${ls.title}`;
      el.addEventListener('click', () => openLesson(ls.id));
      list.appendChild(el);
      chapterEls.set(ls.id, el);
    });

    wrap.appendChild(head);
    wrap.appendChild(list);
    els.chapters.appendChild(wrap);
    wrap._countEl = head.querySelector('.ch-count');
    wrap._ch = ch;
  });

  refreshSidebar();
}

function refreshSidebar() {
  const q = els.q.value.trim().toLowerCase();

  course.chapters.forEach((ch) => {
    const wrap = els.chapters.querySelector(`.ch[data-ch="${ch.id}"]`);
    if (!wrap) return;
    let visible = 0;
    ch.lessons.forEach((ls) => {
      const el = chapterEls.get(ls.id);
      if (!el) return;
      const p = lessonProg(ls.id);
      const hit = !q
        || ls.title.toLowerCase().includes(q)
        || (ls.tags || []).some((t) => t.toLowerCase().includes(q))
        || ch.title.toLowerCase().includes(q);
      el.style.display = hit ? '' : 'none';
      if (hit) visible++;
      el.classList.toggle('done', !!p.done);
      el.classList.toggle('active', current && current.id === ls.id);
      const bar = el.querySelector('.ls-prog i');
      bar.style.width = `${Math.round(ratioOf(ls.id) * 100)}%`;
      el.querySelector('.ls-prog').style.background = ratioOf(ls.id) > 0 ? '#1b2540' : 'transparent';
    });
    const doneCount = ch.lessons.filter((l) => lessonProg(l.id).done).length;
    wrap._countEl.textContent = `${doneCount}/${ch.lessons.length}`;
    wrap.style.display = visible ? '' : 'none';
    if (q) wrap.classList.remove('collapsed');
  });
}

// ------------------------------------------------------------ 字幕
function parseVtt(text) {
  const out = [];
  if (!text) return out;
  const blocks = text.replace(/\r/g, '').split('\n\n');
  for (const b of blocks) {
    const lines = b.split('\n').filter(Boolean);
    const ti = lines.findIndex((l) => l.includes('-->'));
    if (ti < 0) continue;
    const [a, z] = lines[ti].split('-->').map((s) => s.trim());
    const toSec = (s) => {
      const parts = s.split(':');
      if (parts.length === 3) {
        return (+parts[0]) * 3600 + (+parts[1]) * 60 + parseFloat(parts[2]);
      }
      return (+parts[0]) * 60 + parseFloat(parts[1]);
    };
    out.push({ s: toSec(a), e: toSec(z), text: lines.slice(ti + 1).join(' ') });
  }
  return out;
}

function tickSubtitle() {
  if (!subs.length) {
    els.subtitle.classList.remove('show');
    return;
  }
  const on = state.settings.subtitles !== false;
  if (!on) {
    els.subtitle.classList.remove('show');
    return;
  }
  const t = els.video.currentTime;
  const hit = subs.find((x) => t >= x.s && t < x.e);
  if (hit) {
    if (els.subtitle.textContent !== hit.text) els.subtitle.textContent = hit.text;
    els.subtitle.classList.add('show');
  } else {
    els.subtitle.classList.remove('show');
  }
}

// ------------------------------------------------------------ 打开课时
function openLesson(id) {
  const ls = byId.get(id);
  if (!ls) return;

  flushNote();
  current = ls;
  state.lastLesson = id;

  // 侧栏高亮
  chapterEls.forEach((el, k) => el.classList.toggle('active', k === id));

  // 头部信息
  els.crumb.textContent = `${ls.chapterTitle} · 第 ${ls.index} 课`;
  els.lessonTitle.textContent = ls.title;
  els.lessonDur.textContent = fmtDuration(ls.duration);
  els.tags.innerHTML = '';
  (ls.tags || []).forEach((t) => {
    const s = document.createElement('span');
    s.textContent = t;
    els.tags.appendChild(s);
  });

  // 视频
  els.empty.classList.add('hide');
  try { els.video.pause(); } catch { /* 忽略 */ }
  els.video.src = store.videoUrl(ls.video);
  const p = lessonProg(id);
  resumePending = (!p.done && p.t > 5) ? p.t : 0;
  if (resumePending) {
    els.resumeTip.textContent = `将从 ${fmtTime(resumePending)} 继续播放`;
    els.resumeTip.classList.add('show');
  } else {
    els.resumeTip.classList.remove('show');
  }

  // 字幕（数据里已内联，避免 file:// 下再发请求）
  subs = (ls.subtitles && ls.subtitles.length) ? ls.subtitles : [];

  // 代码
  renderCode(ls);
  renderExercises(ls);
  updatePanelHint();

  // 笔记
  els.note.value = state.notes[id] || '';
  els.noteState.textContent = '自动保存';
  els.noteState.classList.remove('flash');

  // 按钮状态
  const done = !!lessonProg(id).done;
  els.btnDone.textContent = done ? '已掌握 ✓' : '标记已学';
  els.btnDone.classList.toggle('done-state', done);

  const i = flat.findIndex((x) => x.id === id);
  els.btnPrev.disabled = i <= 0;
  els.btnNext.disabled = i >= flat.length - 1;
  els.btnNext.textContent = i >= flat.length - 1 ? '已是最后一课' : '下一课';

  saveState(true);
  updateStats();
  refreshSidebar();

  // 自动播放
  const tryPlay = () => {
    if (resumePending) {
      try { els.video.currentTime = resumePending; } catch { /* 忽略 */ }
    }
    if (state.settings.autoplay !== false) {
      els.video.play().catch(() => { /* 需要用户交互时不强求 */ });
    }
  };
  if (els.video.readyState >= 1) tryPlay();
  else els.video.addEventListener('loadedmetadata', tryPlay, { once: true });
}

function makeCodeBlock(code, lang, opts) {
  const wrap = document.createElement('div');
  const pre = document.createElement('pre');
  if (lang === 'bash') {
    pre.classList.add('bash');
    pre.textContent = code;
  } else {
    pre.innerHTML = highlightCpp(code);
  }
  wrap.appendChild(pre);
  if (opts && opts.output) {
    const out = document.createElement('div');
    out.className = 'out';
    out.textContent = opts.output;
    wrap.appendChild(out);
  }
  return wrap;
}

/** 代码块右上角那组小按钮：复制 / 去代码台。 */
function makeCodeButtons(code, opts) {
  const btns = document.createElement('div');
  btns.className = 'btns';

  if ((opts && opts.runnable) !== false) {
    const tryBtn = document.createElement('button');
    tryBtn.className = 'try';
    tryBtn.textContent = '去代码台';
    tryBtn.title = '把这段代码放进代码台，编译运行';
    tryBtn.addEventListener('click', () => openDrawer(code));
    btns.appendChild(tryBtn);
  }

  const btn = document.createElement('button');
  btn.className = 'copy';
  btn.textContent = '复制';
  btn.addEventListener('click', async () => {
    try {
      await navigator.clipboard.writeText(code);
      btn.textContent = '已复制';
      btn.classList.add('ok');
      setTimeout(() => { btn.textContent = '复制'; btn.classList.remove('ok'); }, 1400);
    } catch {
      toast('复制失败');
    }
  });
  btns.appendChild(btn);
  return btns;
}

function renderCode(ls) {
  els.paneCode.innerHTML = '';
  const items = ls.code || [];
  if (!items.length) {
    els.paneCode.innerHTML = '<p class="placeholder">这一课没有代码片段。</p>';
    els.codeHint.textContent = '—';
    return;
  }
  els.codeHint.textContent = `${items.length} 段`;

  items.forEach((it) => {
    const box = document.createElement('div');
    box.className = 'code-item';

    const head = document.createElement('div');
    head.className = 'code-head';
    const t = document.createElement('span');
    t.className = 't';
    t.textContent = it.title || '代码';
    head.appendChild(t);
    head.appendChild(makeCodeButtons(it.code, { runnable: it.lang !== 'bash' }));
    box.appendChild(head);
    box.appendChild(makeCodeBlock(it.code, it.lang, { output: it.output }));

    els.paneCode.appendChild(box);
  });
  els.paneCode.scrollTop = 0;
}

// ------------------------------------------------------------ 练习题
function renderExercises(ls) {
  const list = ls.exercises || [];
  els.paneEx.innerHTML = '';
  els.exCount.textContent = list.length ? String(list.length) : '';

  if (!list.length) {
    els.paneEx.innerHTML = '<p class="placeholder">这一课还没有配练习题。</p>';
    return;
  }

  list.forEach((ex, i) => {
    const item = document.createElement('div');
    item.className = 'ex-item';

    const head = document.createElement('div');
    head.className = 'ex-head';
    const no = document.createElement('span');
    no.className = 'ex-no';
    no.textContent = String(i + 1);
    const q = document.createElement('span');
    q.className = 'ex-q';
    q.textContent = ex.q || '';
    const tg = document.createElement('button');
    tg.className = 'ex-toggle';
    tg.textContent = '答案';
    head.appendChild(no);
    head.appendChild(q);
    head.appendChild(tg);

    const body = document.createElement('div');
    body.className = 'ex-body hidden';
    let built = false;

    const build = () => {
      if (built) return;
      built = true;
      if (ex.hint) {
        const h = document.createElement('p');
        h.className = 'ex-hint';
        h.textContent = ex.hint;
        body.appendChild(h);
      }
      if (ex.answer) {
        const head2 = document.createElement('div');
        head2.className = 'code-head';
        const t2 = document.createElement('span');
        t2.className = 't';
        t2.textContent = '参考答案';
        head2.appendChild(t2);
        head2.appendChild(makeCodeButtons(ex.answer));
        body.appendChild(head2);
        body.appendChild(makeCodeBlock(ex.answer, 'cpp', { output: ex.output }));
      }
      if (ex.note) {
        const n = document.createElement('p');
        n.className = 'ex-note';
        n.textContent = ex.note;
        body.appendChild(n);
      }
    };

    const toggle = () => {
      const open = !item.classList.contains('open');
      build();
      item.classList.toggle('open', open);
      body.classList.toggle('hidden', !open);
      tg.textContent = open ? '收起' : '答案';
    };

    head.addEventListener('click', toggle);
    item.appendChild(head);
    item.appendChild(body);
    els.paneEx.appendChild(item);
  });
  els.paneEx.scrollTop = 0;
}

// ------------------------------------------------------------ 笔记
function flushNote() {
  if (!current) return;
  clearTimeout(noteTimer);
  noteTimer = null;
  const v = els.note.value;
  if ((state.notes[current.id] || '') !== v) {
    if (v.trim()) state.notes[current.id] = v;
    else delete state.notes[current.id];
    saveState(true);
    els.noteState.textContent = '已保存';
    els.noteState.classList.add('flash');
    setTimeout(() => els.noteState.classList.remove('flash'), 1200);
  }
}

els.note.addEventListener('input', () => {
  if (!current) return;
  els.noteState.textContent = '输入中…';
  clearTimeout(noteTimer);
  noteTimer = setTimeout(flushNote, 700);
});

// ------------------------------------------------------------ 进度记录
els.video.addEventListener('timeupdate', () => {
  if (!current) return;
  const d = els.video.duration || current.duration || 0;
  const t = els.video.currentTime;
  if (!d) return;
  const p = state.progress[current.id] || (state.progress[current.id] = { t: 0, d, done: false });
  p.t = t;
  p.d = d;
  if (d > 5 && t / d > 0.92) p.done = true;
  saveState();
  tickSubtitle();

  // 实时更新当前课时的小进度条
  const el = chapterEls.get(current.id);
  if (el) el.querySelector('.ls-prog i').style.width = `${Math.round(ratioOf(current.id) * 100)}%`;
});

els.video.addEventListener('loadedmetadata', () => {
  if (resumePending && Math.abs(els.video.currentTime - resumePending) > 2) {
    try { els.video.currentTime = resumePending; } catch { /* 忽略 */ }
  }
  setTimeout(() => els.resumeTip.classList.remove('show'), 3200);
});

els.video.addEventListener('ended', () => {
  if (!current) return;
  // 只有真正播放到文件结尾才算完成：
  // 切换 src 时浏览器也可能抛出 ended，那种情况不能当作学完、更不能自动跳课
  if (!els.video.ended) return;
  const played = els.video.played;
  const reached = played.length ? played.end(played.length - 1) : 0;
  if (reached < 1) return;

  const p = state.progress[current.id] || (state.progress[current.id] = { t: 0, d: 0, done: false });
  p.done = true;
  p.t = p.d || els.video.duration;
  p.d = p.d || els.video.duration;
  saveState(true);
  refreshSidebar();
  updateStats();
  updateDoneBtn();
  toast('本课完成 ✓');
  // 自动下一课
  const i = flat.findIndex((x) => x.id === current.id);
  if (i >= 0 && i < flat.length - 1) {
    setTimeout(() => openLesson(flat[i + 1].id), 1200);
  }
});

els.video.addEventListener('play', () => {
  els.resumeTip.classList.remove('show');
});

els.video.addEventListener('error', () => {
  if (!current) return;
  toast('视频文件缺失，请重新生成：' + current.video);
});

// ------------------------------------------------------------ 按钮
function updateDoneBtn() {
  if (!current) return;
  const done = !!lessonProg(current.id).done;
  els.btnDone.textContent = done ? '已掌握 ✓' : '标记已学';
  els.btnDone.classList.toggle('done-state', done);
}

els.btnDone.addEventListener('click', () => {
  if (!current) return;
  const p = state.progress[current.id] || (state.progress[current.id] = { t: 0, d: 0, done: false });
  p.done = !p.done;
  if (p.done) { p.t = p.d || els.video.duration || 0; p.d = p.d || els.video.duration || 0; }
  saveState(true);
  updateDoneBtn();
  refreshSidebar();
  updateStats();
  toast(p.done ? '已标记为学完' : '已取消完成标记');
});

function step(delta) {
  if (!current) return;
  const i = flat.findIndex((x) => x.id === current.id);
  const j = i + delta;
  if (j >= 0 && j < flat.length) openLesson(flat[j].id);
}

els.btnPrev.addEventListener('click', () => step(-1));
els.btnNext.addEventListener('click', () => step(1));

// ------------------------------------------------------------ 搜索
els.q.addEventListener('input', refreshSidebar);

// ------------------------------------------------------------ 快捷键
document.addEventListener('keydown', (e) => {
  // 代码台快捷键优先，且不受输入焦点影响
  if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
    e.preventDefault();
    if (pg.open) runCode();
    return;
  }
  if (e.key === 'Escape' && pg.open) {
    e.preventDefault();
    closeDrawer();
    return;
  }

  const typing = ['INPUT', 'TEXTAREA'].includes(document.activeElement.tagName);

  if (e.key === 'Escape' && typing) {
    document.activeElement.blur();
    return;
  }
  if (typing) return;

  if (e.code === 'Space') {
    e.preventDefault();
    if (!current) return;
    els.video.paused ? els.video.play().catch(() => {}) : els.video.pause();
  } else if (e.key === 'ArrowLeft') {
    e.preventDefault();
    els.video.currentTime = Math.max(0, els.video.currentTime - 5);
  } else if (e.key === 'ArrowRight') {
    e.preventDefault();
    els.video.currentTime = Math.min(els.video.duration || 0, els.video.currentTime + 5);
  } else if (e.altKey && e.key === 'ArrowUp') {
    e.preventDefault();
    step(-1);
  } else if (e.altKey && e.key === 'ArrowDown') {
    e.preventDefault();
    step(1);
  } else if (e.key === 'n' || e.key === 'N') {
    e.preventDefault();
    els.note.focus();
  } else if (e.key === 's' || e.key === 'S') {
    e.preventDefault();
    toggleSubs();
  }
});

// ------------------------------------------------------------ 字幕开关
function toggleSubs() {
  state.settings.subtitles = state.settings.subtitles === false;
  saveState(true);
  toast(state.settings.subtitles === false ? '字幕已关闭' : '字幕已开启');
  tickSubtitle();
}

// ------------------------------------------------------------ 练习题 / 代码示例 的 tab
function activeTab() {
  const t = document.querySelector('.tab.active');
  return t ? t.dataset.tab : 'code';
}

/** 右上角那个小提示要跟着当前 tab 和课时一起变。 */
function updatePanelHint() {
  if (!current) {
    els.codeHint.textContent = '—';
    return;
  }
  if (activeTab() === 'ex') {
    const n = (current.exercises || []).length;
    els.codeHint.textContent = n ? `${n} 题` : '—';
  } else {
    const n = (current.code || []).length;
    els.codeHint.textContent = n ? `${n} 段` : '—';
  }
}

document.querySelectorAll('.tab').forEach((tab) => {
  tab.addEventListener('click', () => {
    document.querySelectorAll('.tab').forEach((t) => t.classList.remove('active'));
    tab.classList.add('active');
    const name = tab.dataset.tab;
    els.paneCode.classList.toggle('hidden', name !== 'code');
    els.paneEx.classList.toggle('hidden', name !== 'ex');
    updatePanelHint();
  });
});

// ------------------------------------------------------------ 代码台
const pg = {
  open: false,
  compiler: null,     // {found, path, version, hint}
  checked: false,
  running: false,
  base: '',           // 打开时填入的原始代码，用于「重置」
};

function setBadge(text, cls) {
  els.compilerBadge.textContent = text;
  els.compilerBadge.className = 'compiler-badge' + (cls ? ' ' + cls : '');
}

async function ensureCompiler(force) {
  if (!IS_ELECTRON) {
    setBadge('浏览器模式不支持本地编译，请用桌面版', 'bad');
    return null;
  }
  if (pg.checked && !force) return pg.compiler;
  pg.checked = true;
  setBadge('检测编译器中…', '');
  try {
    const st = await window.cpp.compilerStatus();
    pg.compiler = st;
    if (st && st.found) {
      const name = (st.version || 'g++').replace(/\s+/g, ' ').slice(0, 46);
      setBadge(name, 'ok');
      els.compilerBadge.title = st.path;
      els.btnRun.disabled = false;
    } else {
      setBadge('未检测到 g++，请安装 MinGW 或指定路径', 'bad');
      els.compilerBadge.title = (st && st.hint) || '';
      els.btnRun.disabled = true;
    }
  } catch (e) {
    setBadge('编译器检测失败', 'bad');
    els.btnRun.disabled = true;
  }
  return pg.compiler;
}

function updateGutter() {
  const n = Math.max(1, els.editor.value.split('\n').length);
  let s = '';
  for (let i = 1; i <= n; i++) s += i + '\n';
  els.gutter.textContent = s;
}

function syncScroll() {
  els.hl.scrollTop = els.editor.scrollTop;
  els.hl.scrollLeft = els.editor.scrollLeft;
  els.gutter.scrollTop = els.editor.scrollTop;
}

function refreshEditor() {
  // 末尾补一个换行，保证最后一行的高亮层与光标对齐
  els.hl.innerHTML = highlightCpp(els.editor.value + '\n');
  updateGutter();
  syncScroll();
}

function openDrawer(code) {
  if (!pg.open) {
    pg.base = code || '';
    els.editor.value = code || '';
    els.drawer.classList.add('open');
    els.drawerMask.classList.add('show');
    els.drawer.setAttribute('aria-hidden', 'false');
    pg.open = true;
    refreshEditor();
    ensureCompiler();
  } else {
    // 已打开：直接换掉内容
    pg.base = code || '';
    els.editor.value = code || '';
    refreshEditor();
  }
  setTimeout(() => {
    els.editor.focus();
    els.editor.selectionStart = els.editor.selectionEnd = 0;
  }, 130);
}

function closeDrawer() {
  if (!pg.open) return;
  pg.open = false;
  els.drawer.classList.remove('open');
  els.drawerMask.classList.remove('show');
  els.drawer.setAttribute('aria-hidden', 'true');
}

function setRunStatus(text, cls) {
  els.runStatus.textContent = text;
  els.runStatus.className = 'run-status' + (cls ? ' ' + cls : '');
}

function showRunOutput(text, cls) {
  els.runOutput.textContent = text;
  els.runOutput.className = 'io-out' + (cls ? ' ' + cls : '');
}

async function runCode() {
  if (pg.running) return;
  if (!IS_ELECTRON) {
    showRunOutput('浏览器模式下无法调用本地编译器。\n请用桌面版打开（Windows 的 exe 或 macOS 的 .app）。', 'err');
    setRunStatus('不可用', 'bad');
    return;
  }
  const code = els.editor.value;
  if (!code.trim()) {
    showRunOutput('先写点代码吧。', 'err');
    return;
  }

  pg.running = true;
  els.btnRun.disabled = true;
  els.btnRun.textContent = '运行中…';
  setRunStatus('编译中…', 'busy');
  showRunOutput('', '');

  const t0 = performance.now();
  try {
    const res = await window.cpp.runCode({
      code,
      stdin: els.runStdin.value,
      std: els.stdSelect.value,
      timeoutMs: 6000,
    });
    const ms = Math.round(performance.now() - t0);

    if (res.stage === 'compiler') {
      showRunOutput('没有可用的 C++ 编译器。\n\n' + (res.message || ''), 'err');
      setRunStatus('无编译器', 'bad');
      await ensureCompiler(true);
    } else if (res.ok) {
      const body = (res.output || '').length ? res.output : '（程序没有任何输出）';
      showRunOutput(body, 'ok');
      setRunStatus(`✓ 退出码 ${res.exitCode} · ${ms} ms`, 'ok');
    } else if (res.stage === 'compile') {
      showRunOutput(res.output || res.message || '编译失败', 'err');
      setRunStatus('编译失败', 'bad');
    } else if (res.stage === 'run') {
      showRunOutput((res.output ? res.output + '\n\n' : '') + (res.message || ''), 'err');
      setRunStatus('运行超时', 'bad');
    } else {
      showRunOutput(res.message || '出错了', 'err');
      setRunStatus('失败', 'bad');
    }
  } catch (e) {
    showRunOutput(String(e && e.message || e), 'err');
    setRunStatus('失败', 'bad');
  } finally {
    pg.running = false;
    els.btnRun.disabled = false;
    els.btnRun.textContent = '运行';
  }
}

els.editor.addEventListener('input', refreshEditor);
els.editor.addEventListener('scroll', syncScroll);
els.editor.addEventListener('keydown', (e) => {
  if (e.key === 'Tab') {
    e.preventDefault();
    const s = els.editor.selectionStart;
    const t = els.editor.selectionEnd;
    els.editor.value = els.editor.value.slice(0, s) + '    ' + els.editor.value.slice(t);
    els.editor.selectionStart = els.editor.selectionEnd = s + 4;
    refreshEditor();
  }
});

els.btnRun.addEventListener('click', runCode);
els.btnCloseDrawer.addEventListener('click', closeDrawer);
els.drawerMask.addEventListener('click', closeDrawer);
els.btnResetCode.addEventListener('click', () => {
  els.editor.value = pg.base;
  refreshEditor();
  showRunOutput('已恢复成课时里的示例代码。', '');
  setRunStatus('', '');
});

// ------------------------------------------------------------ 启动
async function boot() {
  try {
    state = await store.load();
  } catch {
    state = { progress: {}, notes: {}, settings: {}, lastLesson: null };
  }
  state.progress = state.progress || {};
  state.notes = state.notes || {};
  state.settings = state.settings || {};

  course = window.COURSE_DATA;
  if (!course) {
    els.chapters.innerHTML = '<p class="placeholder" style="padding:16px">课程数据缺失，请先运行生成脚本。</p>';
    return;
  }

  flat = [];
  course.chapters.forEach((ch) => {
    ch.lessons.forEach((ls) => {
      flat.push({ ...ls, chapterId: ch.id, chapterTitle: ch.title });
    });
  });
  byId = new Map(flat.map((l) => [l.id, l]));

  buildSidebar();
  updateStats();
  els.footInfo.textContent = `${flat.length} 节课 · 空格播放 · ←→ 快进退 · Alt+↑↓ 换课 · S 字幕`;

  const params = new URLSearchParams(location.search);
  const want = params.get('lesson');
  const firstId = (want && byId.has(want))
    ? want
    : (state.lastLesson && byId.has(state.lastLesson) ? state.lastLesson : (flat[0] && flat[0].id));
  if (firstId) openLesson(firstId);
}

window.addEventListener('beforeunload', () => {
  flushNote();
  saveState(true);
});

document.addEventListener('DOMContentLoaded', boot);
