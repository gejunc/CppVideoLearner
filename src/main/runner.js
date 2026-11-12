'use strict';

/**
 * 本地 C++ 编译运行器。
 *
 * 设计要点
 * --------
 * * 编译产物全部走应用数据目录下的临时工作区，跑完即删。
 * * 子进程输出走管道收集 —— 文件描述符继承在 Electron 主进程里不生效。
 * * 系统的 TEMP 在受限环境下可能不可写，会给 g++ 单独指定临时目录，
 *   否则它会报 "Cannot create temporary file ... Permission denied"。
 * * 编译和运行都有硬超时，运行输出有长度上限。
 */

const fs = require('node:fs');
const os = require('node:os');
const path = require('node:path');
const { spawn } = require('node:child_process');

const COMPILE_TIMEOUT = 30000;
const RUN_TIMEOUT_DEFAULT = 6000;
const MAX_OUTPUT = 20000;
const MAX_CODE = 64 * 1024;

const IS_WIN = process.platform === 'win32';
const IS_MAC = process.platform === 'darwin';
const EXE_SUFFIX = IS_WIN ? '.exe' : '';

let cachedCompiler = null;

// ---------------------------------------------------------------- 探测
function exists(p) {
  try { return fs.statSync(p).isFile(); } catch { return false; }
}

function findInPath(exeName) {
  const raw = process.env.PATH || process.env.Path || '';
  for (const dir of raw.split(path.delimiter)) {
    if (!dir) continue;
    const p = path.join(dir, exeName);
    if (exists(p)) return p;
  }
  return null;
}

/** 在若干根目录下按固定深度找 g++.exe（用于 WinGet / MSYS2 / 便携包）。 */
function scanForGpp(roots, depth) {
  const hits = [];
  const walk = (dir, d) => {
    if (d < 0 || hits.length > 8) return;
    let entries;
    try { entries = fs.readdirSync(dir, { withFileTypes: true }); } catch { return; }
    for (const e of entries) {
      if (!e.isDirectory()) continue;
      const full = path.join(dir, e.name);
      if (e.name === 'bin') {
        const g = path.join(full, 'g++.exe');
        if (exists(g)) { hits.push(g); continue; }
      }
      if (/^(Windows|System32|ProgramData|node_modules)$/i.test(e.name)) continue;
      walk(full, d - 1);
    }
  };
  for (const r of roots) {
    if (!r) continue;
    try { if (!fs.statSync(r).isDirectory()) continue; } catch { continue; }
    walk(r, depth);
  }
  return hits;
}

function candidateRoots() {
  const roots = [];
  if (IS_WIN) {
    const la = process.env.LOCALAPPDATA;
    if (la) {
      roots.push(path.join(la, 'Microsoft', 'WinGet', 'Packages'));
      roots.push(path.join(la, 'Programs'));
    }
    roots.push('C:\\msys64', 'C:\\mingw64', 'C:\\MinGW', 'D:\\msys64', 'D:\\mingw64');
    roots.push('C:\\Program Files\\mingw-w64', 'C:\\Program Files\\mingw64');
    roots.push(path.join(process.env.ProgramData || 'C:\\ProgramData', 'mingw64'));
    return roots;
  }
  // macOS / Linux：编译器基本都在固定位置，不需要深扫
  if (IS_MAC) {
    roots.push('/opt/homebrew/opt/llvm/bin', '/usr/local/opt/llvm/bin');
  }
  return roots;
}

/** 各平台要试的可执行文件名（macOS 上 clang++ 才是系统自带的）。 */
function compilerNames() {
  if (IS_WIN) return ['g++' + EXE_SUFFIX, 'clang++' + EXE_SUFFIX];
  return ['clang++', 'g++', 'c++'];
}

/** 各平台的固定候选路径（PATH 之外兜底）。 */
function fixedCandidates() {
  if (IS_WIN) return [];
  const list = ['/usr/bin/clang++', '/usr/bin/g++', '/usr/bin/c++',
    '/usr/local/bin/clang++', '/usr/local/bin/g++',
    '/opt/homebrew/bin/clang++', '/opt/homebrew/bin/g++'];
  return list.filter((p) => exists(p));
}

/** 跨平台杀掉子进程（Windows 要连子进程树一起杀）。 */
function killTree(child) {
  if (!child || !child.pid) return;
  if (IS_WIN) {
    try {
      spawn('taskkill', ['/PID', String(child.pid), '/T', '/F'],
        { stdio: 'ignore', windowsHide: true });
      return;
    } catch { /* 落到下面 */ }
  }
  try { child.kill('SIGKILL'); } catch { /* 忽略 */ }
}

/** 构造子进程环境：编译器目录塞进 PATH，临时目录改到我们可写的位置。 */
function childEnv(binDir, tmpDir) {
  const env = { ...process.env };
  const base = process.env.PATH || process.env.Path || '';
  env.PATH = binDir ? binDir + path.delimiter + base : base;
  env.Path = env.PATH;
  if (tmpDir) {
    env.TEMP = tmpDir;
    env.TMP = tmpDir;
    env.TMPDIR = tmpDir;
  }
  return env;
}

function runCaptured(exe, args, timeoutMs) {
  return new Promise((resolve) => {
    let child;
    let out = '';
    let errMsg = '';
    let done = false;
    const finish = (code) => {
      if (done) return;
      done = true;
      resolve({ code, out, err: errMsg });
    };
    try {
      child = spawn(exe, args, {
        windowsHide: true,
        env: childEnv(path.dirname(exe)),
      });
    } catch (e) {
      errMsg = String((e && e.message) || e);
      finish(-1);
      return;
    }
    child.stdout.on('data', (d) => { out += d.toString(); });
    child.stderr.on('data', (d) => { out += d.toString(); });
    const timer = setTimeout(() => {
      try { child.kill(); } catch { /* 忽略 */ }
      finish(-2);
    }, timeoutMs || 8000);
    child.on('error', (e) => {
      clearTimeout(timer);
      errMsg = String((e && e.message) || e);
      finish(-1);
    });
    child.on('close', (code) => { clearTimeout(timer); finish(code); });
  });
}

/** 返回 { found, path, version, source, tried?, hint? }。结果缓存，除非 force。 */
async function detectCompiler(force = false) {
  if (cachedCompiler && !force && cachedCompiler.found) return cachedCompiler;

  const tried = [];
  const custom = process.env.CPP_COMPILER;
  const candidates = [];
  const seen = new Set();

  const addCandidate = (p, source) => {
    if (!p || seen.has(p)) return;
    seen.add(p);
    candidates.push({ p, source });
  };

  if (custom) addCandidate(custom, 'env');

  for (const name of compilerNames()) {
    const inPath = findInPath(name);
    if (inPath) addCandidate(inPath, 'path');
  }

  for (const p of fixedCandidates()) addCandidate(p, 'fixed');

  if (IS_WIN) {
    for (const g of scanForGpp(candidateRoots(), 4)) addCandidate(g, 'scan');
  }

  for (const c of candidates) {
    if (!c.p || !exists(c.p)) { tried.push({ path: c.p, reason: 'not found' }); continue; }
    const r = await runCaptured(c.p, ['--version'], 8000);
    if (r.code === 0 && /g\+\+|clang|GCC|Apple/i.test(r.out)) {
      const first = (r.out.split('\n')[0] || '').trim();
      cachedCompiler = { found: true, path: c.p, version: first, source: c.source };
      return cachedCompiler;
    }
    tried.push({ path: c.p, code: r.code, err: r.err || '', out: (r.out || '').slice(0, 300) });
  }

  let hint;
  if (IS_MAC) {
    hint = '未检测到 C++ 编译器。macOS 上执行 xcode-select --install 安装命令行工具后重启本应用；'
      + '也可以用 brew install gcc，或设置环境变量 CPP_COMPILER 指向 clang++。';
  } else if (IS_WIN) {
    hint = '未检测到 g++。装一个 MinGW-w64（例如 winget install BrechtSanders.WinLibs.POSIX.UCRT）'
      + '后重启本应用即可；也可以在启动前设置环境变量 CPP_COMPILER 指向 g++.exe。';
  } else {
    hint = '未检测到 C++ 编译器。请安装 g++（如 sudo apt install g++）后重启本应用，'
      + '或设置环境变量 CPP_COMPILER。';
  }

  cachedCompiler = {
    found: false,
    path: null,
    version: null,
    source: null,
    hint,
    tried,
  };
  return cachedCompiler;
}

function setCompiler(p) {
  cachedCompiler = null;
  if (p) process.env.CPP_COMPILER = p;
  else delete process.env.CPP_COMPILER;
  return detectCompiler(true);
}

// ---------------------------------------------------------------- 编译运行
function clip(s, n) {
  if (!s) return '';
  if (s.length <= n) return s;
  return s.slice(0, n) + `\n…（输出过长，已截断，共 ${s.length} 字符）`;
}

/**
 * 编译并运行一段 C++ 代码。
 * @param {{code:string, stdin?:string, timeoutMs?:number, std?:string, workRoot?:string}} opts
 */
async function compileAndRun(opts) {
  const code = String((opts && opts.code) || '');
  if (!code.trim()) {
    return { ok: false, stage: 'input', message: '代码是空的。' };
  }
  if (code.length > MAX_CODE) {
    return { ok: false, stage: 'input', message: `代码太长（上限 ${MAX_CODE / 1024} KB）。` };
  }

  const cc = await detectCompiler();
  if (!cc.found) {
    return { ok: false, stage: 'compiler', message: cc.hint, compiler: null };
  }

  const std = (opts && opts.std) || 'c++20';
  const timeoutMs = Math.min(20000, Math.max(1000, (opts && opts.timeoutMs) || RUN_TIMEOUT_DEFAULT));

  // 工作目录优先放在应用自己的数据目录下 —— 系统临时目录在受限环境里可能不可写
  const workRoot = (opts && opts.workRoot) || path.join(os.tmpdir(), 'cpp-playground');
  let work;
  try {
    fs.mkdirSync(workRoot, { recursive: true });
    work = fs.mkdtempSync(path.join(workRoot, 'run-'));
  } catch (e) {
    return {
      ok: false, stage: 'internal',
      message: '无法创建工作目录：' + String((e && e.message) || e),
    };
  }

  const srcFile = path.join(work, 'main.cpp');
  const exeFile = path.join(work, IS_WIN ? 'main.exe' : 'main');
  const tmpFile = path.join(work, 'tmp');
  const started = Date.now();

  try {
    fs.mkdirSync(tmpFile, { recursive: true });
    fs.writeFileSync(srcFile, code, 'utf8');

    const args = ['-std=' + std, '-O0', '-Wall', '-Wextra',
      '-fdiagnostics-color=never', '-fno-diagnostics-show-caret'];
    // 只有 MinGW 需要静态链接运行时，否则生成的 exe 换台机器就找不到 libstdc++-6.dll。
    // macOS 的 clang 与 Linux 的 g++ 都不认这两个开关，加了会直接编译失败。
    if (IS_WIN) args.push('-static-libgcc', '-static-libstdc++');
    args.push(srcFile, '-o', exeFile);

    // ---- 编译
    const crate = await new Promise((resolve) => {
      let child;
      let out = '';
      let done = false;
      const finish = (c) => {
        if (done) return;
        done = true;
        resolve({ code: c, out });
      };
      try {
        child = spawn(cc.path, args, {
          cwd: work,
          windowsHide: true,
          env: childEnv(path.dirname(cc.path), tmpFile),
        });
      } catch {
        return finish(-1);
      }
      child.stdout.on('data', (d) => { out += d.toString(); });
      child.stderr.on('data', (d) => { out += d.toString(); });
      const t = setTimeout(() => {
        killTree(child);
        finish(-2);
      }, COMPILE_TIMEOUT);
      child.on('error', (e) => {
        clearTimeout(t);
        out += String((e && e.message) || e);
        finish(-1);
      });
      child.on('close', (c) => { clearTimeout(t); finish(c); });
    });

    if (crate.code === -2) {
      return {
        ok: false, stage: 'compile', message: '编译超时（30 秒）。',
        output: clip(crate.out, MAX_OUTPUT), compiler: cc.path,
      };
    }
    if (crate.code !== 0 || !exists(exeFile)) {
      return {
        ok: false, stage: 'compile', message: '编译失败。',
        output: clip(crate.out, MAX_OUTPUT), compiler: cc.path,
      };
    }

    // ---- 运行
    const run = await new Promise((resolve) => {
      let child;
      let out = '';
      let done = false;
      const finish = (c, timedOut) => {
        if (done) return;
        done = true;
        resolve({ code: c, out, timedOut: !!timedOut });
      };
      try {
        child = spawn(exeFile, [], {
          cwd: work,
          windowsHide: true,
          env: childEnv(path.dirname(cc.path), tmpFile),
        });
      } catch {
        return finish(-1, false);
      }
      child.stdout.on('data', (d) => { out += d.toString(); });
      child.stderr.on('data', (d) => { out += d.toString(); });

      try {
        child.stdin.end(String((opts && opts.stdin) || ''), 'utf8');
      } catch { /* 忽略 */ }

      const t = setTimeout(() => {
        killTree(child);
        finish(-2, true);
      }, timeoutMs);
      child.on('error', (e) => {
        clearTimeout(t);
        out += String((e && e.message) || e);
        finish(-1, false);
      });
      child.on('close', (c) => { clearTimeout(t); finish(c, false); });
    });

    if (run.timedOut) {
      return {
        ok: false, stage: 'run',
        message: `运行超时（${timeoutMs / 1000} 秒）——多半是死循环，或者程序在等输入。`,
        output: clip(run.out, MAX_OUTPUT),
        compiler: cc.path,
      };
    }

    // 退出码落在 NTSTATUS 区间（0xC0000000 以上）说明进程是崩溃退出的
    const crashed = run.code !== null && (run.code >>> 0) >= 0xC0000000;
    if (crashed) {
      const hex = '0x' + (run.code >>> 0).toString(16).toUpperCase();
      const why = hex === '0XC0000135' ? '（找不到运行时 DLL）'
        : hex === '0XC0000005' ? '（访问冲突，多半是空指针或越界）'
          : '';
      return {
        ok: false, stage: 'run',
        message: `程序崩溃退出 ${hex}${why}。`,
        output: clip(run.out, MAX_OUTPUT),
        compiler: cc.path,
      };
    }

    return {
      ok: true,
      stage: 'done',
      exitCode: run.code,
      nonZero: run.code !== 0,
      output: clip(run.out, MAX_OUTPUT),
      elapsedMs: Date.now() - started,
      compiler: cc.path,
      std,
    };
  } catch (e) {
    return { ok: false, stage: 'internal', message: String((e && e.message) || e) };
  } finally {
    setTimeout(() => {
      try { fs.rmSync(work, { recursive: true, force: true }); } catch { /* 忽略 */ }
    }, 500);
  }
}

module.exports = { detectCompiler, setCompiler, compileAndRun };
