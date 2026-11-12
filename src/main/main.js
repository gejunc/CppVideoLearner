'use strict';

const { app, BrowserWindow, ipcMain, shell, Menu, screen } = require('electron');
const path = require('node:path');
const fs = require('node:fs');
const runner = require('./runner');

// 本应用是纯离线课件（本地 HTML + 本地 mp4），没有远程内容，
// 因此在受限环境（企业策略、沙箱、某些远程桌面）里关闭 Chromium 沙箱，
// 换取"双击即用"。若需要恢复默认行为，删掉下面这行即可。
try { app.commandLine.appendSwitch('no-sandbox'); } catch { /* 忽略 */ }
try { app.commandLine.appendSwitch('disable-gpu-sandbox'); } catch { /* 忽略 */ }

// 部分核显（实测 Intel Arc / Ultra 系列）的 D3D11 硬件解码会把 H.264 解成
// 满屏彩色马赛克。本应用只有 1080p24 的幻灯片式视频，CPU 软解开销可以忽略，
// 用稳定性换这一点性能非常划算。遇到花屏就是这个开关在起作用。
try { app.commandLine.appendSwitch('disable-accelerated-video-decode'); } catch { /* 忽略 */ }

/**
 * 选一个真正可写的用户数据目录。
 *
 * Chromium 在启动早期就要写 userData / sessionData，若默认位置（%APPDATA%）
 * 不可写，进程会直接崩溃且没有任何提示。这里逐个探测候选目录，
 * 优先沿用系统默认，失败再退到程序同级或临时目录。
 */
function pickUserDataDir() {
  const candidates = [];
  if (process.env.CPP_DATA_DIR) candidates.push(process.env.CPP_DATA_DIR);
  try { candidates.push(app.getPath('userData')); } catch { /* 忽略 */ }
  try { candidates.push(path.join(path.dirname(app.getPath('exe')), 'userdata')); } catch { /* 忽略 */ }
  try { candidates.push(path.join(app.getPath('temp'), 'CppVideoLearner')); } catch { /* 忽略 */ }

  for (const dir of candidates) {
    if (!dir) continue;
    try {
      fs.mkdirSync(dir, { recursive: true });
      const probe = path.join(dir, '.write-probe');
      fs.writeFileSync(probe, 'ok');
      fs.unlinkSync(probe);
      app.setPath('userData', dir);
      try { app.setPath('sessionData', dir); } catch { /* 旧版本无此路径 */ }
      return dir;
    } catch {
      // 换下一个候选
    }
  }
  return null;
}

const DATA_DIR = pickUserDataDir() || app.getPath('userData');
const STATE_FILE = path.join(DATA_DIR, 'learn-state.json');

/** 启动诊断日志：受限环境下没有控制台，写文件才能看到问题。 */
function log(msg) {
  try {
    fs.appendFileSync(path.join(DATA_DIR, 'startup.log'),
      `[${new Date().toISOString()}] ${msg}\n`);
  } catch { /* 忽略 */ }
}
log('boot pid=' + process.pid + ' dataDir=' + DATA_DIR);

let win = null;

/** 读取学习状态（进度 / 笔记 / 设置）。 */
function loadState() {
  try {
    const raw = fs.readFileSync(STATE_FILE, 'utf8');
    const data = JSON.parse(raw);
    return {
      progress: data.progress || {},
      notes: data.notes || {},
      settings: data.settings || {},
      lastLesson: data.lastLesson || null,
    };
  } catch {
    return { progress: {}, notes: {}, settings: {}, lastLesson: null };
  }
}

/** 原子写入，避免断电或强杀时把状态写坏。 */
function saveState(state) {
  try {
    const tmp = STATE_FILE + '.tmp';
    fs.mkdirSync(path.dirname(STATE_FILE), { recursive: true });
    fs.writeFileSync(tmp, JSON.stringify(state, null, 1), 'utf8');
    fs.renameSync(tmp, STATE_FILE);
    return true;
  } catch (e) {
    console.error('保存状态失败', e);
    return false;
  }
}

function createWindow() {
  // 高 DPI 屏幕上窗口容易超出可视区域，按工作区尺寸收敛
  let wa = { width: 1420, height: 900 };
  try {
    wa = screen.getPrimaryDisplay().workAreaSize;
  } catch { /* 忽略 */ }
  try {
    const d = screen.getPrimaryDisplay();
    log(`display size=${d.size.width}x${d.size.height} ` +
        `workArea=${d.workArea.width}x${d.workArea.height},${d.workArea.x},${d.workArea.y} ` +
        `workAreaSize=${d.workAreaSize.width}x${d.workAreaSize.height} sf=${d.scaleFactor}`);
  } catch { /* 忽略 */ }
  const width = Math.max(900, Math.min(1420, wa.width - 24));
  const height = Math.max(620, Math.min(900, wa.height - 24));

  const isMac = process.platform === 'darwin';

  const winOptions = {
    width,
    height,
    minWidth: Math.min(1080, width),
    minHeight: Math.min(700, height),
    backgroundColor: '#0b1020',
    show: false,
    autoHideMenuBar: true,
    // macOS 用 hiddenInset 让红绿灯嵌进自绘标题栏；Windows 用 titleBarOverlay 画系统按钮
    titleBarStyle: isMac ? 'hiddenInset' : 'hidden',
    webPreferences: {
      preload: path.join(__dirname, 'preload.js'),
      contextIsolation: true,
      nodeIntegration: false,
      sandbox: false,
      // 本地视频通过 file:// 读取，允许自动播放
      autoplayPolicy: 'no-user-gesture-required',
    },
  };

  if (!isMac) {
    winOptions.titleBarOverlay = {
      color: '#0b1020',
      symbolColor: '#c8d0e0',
      height: 44,
    };
  }

  win = new BrowserWindow(winOptions);

  // 居中显示，避免出现在屏幕外
  try { win.center(); } catch { /* 忽略 */ }

  win.loadFile(path.join(__dirname, '..', 'renderer', 'index.html'));
  log('loadFile 已发出');

  win.webContents.on('did-fail-load', (_e, code, desc, url) => {
    log(`did-fail-load code=${code} desc=${desc} url=${url}`);
  });
  win.webContents.on('render-process-gone', (_e, details) => {
    log('render-process-gone ' + JSON.stringify(details));
  });
  win.webContents.on('console-message', (_e, level, message, line, source) => {
    if (level >= 2) log(`console[${level}] ${message} @${source}:${line}`);
  });
  win.webContents.on('dom-ready', () => log('dom-ready'));

  win.once('ready-to-show', () => {
    log('ready-to-show');
    win.show();
    // 以渲染进程看到的可用区域为准再校一次窗口尺寸。
    // 某些高 DPI 环境下主进程拿到的 screen 尺寸单位并不可靠。
    win.webContents.executeJavaScript(
      '({aw: window.screen.availWidth, ah: window.screen.availHeight,' +
      ' dpr: window.devicePixelRatio, iw: window.innerWidth, ih: window.innerHeight})',
      true,
    ).then((info) => {
      log('renderer screen ' + JSON.stringify(info));
      if (!info || !info.aw || !info.ah) return;
      const b = win.getBounds();
      let nw = Math.min(b.width, info.aw - 16);
      let nh = Math.min(b.height, info.ah - 16);
      if (nw < 860) nw = Math.max(860, Math.min(info.aw - 16, b.width));
      if (nh < 600) nh = Math.max(600, Math.min(info.ah - 16, b.height));
      if (Math.abs(nw - b.width) > 2 || Math.abs(nh - b.height) > 2) {
        log(`resize ${b.width}x${b.height} -> ${nw}x${nh}`);
        win.setBounds({
          x: Math.max(0, Math.round((info.aw - nw) / 2)),
          y: Math.max(0, Math.round((info.ah - nh) / 2)),
          width: Math.round(nw),
          height: Math.round(nh),
        });
      }
    }).catch(() => { /* 忽略 */ });
  });

  // 兜底：某些环境下 ready-to-show 可能不触发，超时后强制显示
  setTimeout(() => {
    if (win && !win.isDestroyed() && !win.isVisible()) {
      log('兜底 show');
      win.show();
    }
  }, 4000);

  // 记住窗口尺寸（并保证不越界）
  const state = loadState();
  if (state.settings && state.settings.window) {
    try {
      const wa2 = screen.getPrimaryDisplay().workArea;
      const b = state.settings.window;
      const w2 = Math.min(b.width || width, wa2.width);
      const h2 = Math.min(b.height || height, wa2.height);
      const x2 = Math.max(wa2.x, Math.min(b.x ?? wa2.x, wa2.x + wa2.width - w2));
      const y2 = Math.max(wa2.y, Math.min(b.y ?? wa2.y, wa2.y + wa2.height - h2));
      win.setBounds({ x: x2, y: y2, width: w2, height: h2 });
    } catch { /* 忽略 */ }
  }
  win.on('close', () => {
    try {
      const s = loadState();
      s.settings = s.settings || {};
      s.settings.window = win.getBounds();
      saveState(s);
    } catch { /* 忽略 */ }
  });

  win.on('closed', () => { win = null; });

  // 外链用系统浏览器打开，不在应用内导航
  win.webContents.setWindowOpenHandler(({ url }) => {
    if (/^https?:/.test(url)) shell.openExternal(url);
    return { action: 'deny' };
  });
}

if (!app.requestSingleInstanceLock()) {
  app.quit();
} else {
  app.on('second-instance', () => {
    if (win) {
      if (win.isMinimized()) win.restore();
      win.focus();
    }
  });

  app.whenReady().then(() => {
    if (process.platform === 'darwin') {
      // macOS 上必须有应用菜单，否则 Cmd+Q / Cmd+C / Cmd+V 这些标准快捷键会失效
      Menu.setApplicationMenu(Menu.buildFromTemplate([
        { role: 'appMenu' },
        { role: 'editMenu' },
        { role: 'viewMenu' },
        { role: 'windowMenu' },
      ]));
    } else {
      Menu.setApplicationMenu(null);
    }
    createWindow();

    app.on('activate', () => {
      if (BrowserWindow.getAllWindows().length === 0) createWindow();
    });
  });

  app.on('window-all-closed', () => {
    if (process.platform !== 'darwin') app.quit();
  });
}

// ---------------------------------------------------------------- IPC
ipcMain.handle('state:load', () => loadState());
ipcMain.handle('state:save', (_e, state) => saveState(state));
ipcMain.handle('app:info', () => ({
  version: app.getVersion(),
  dataDir: app.getPath('userData'),
  stateFile: STATE_FILE,
}));

ipcMain.handle('window:minimize', () => win && win.minimize());
ipcMain.handle('window:maximize', () => {
  if (!win) return;
  win.isMaximized() ? win.unmaximize() : win.maximize();
});
ipcMain.handle('window:close', () => win && win.close());

// ---- 本地编译运行
ipcMain.handle('compiler:status', (_e, force) => runner.detectCompiler(!!force));
ipcMain.handle('compiler:run', (_e, opts) => runner.compileAndRun({
  ...(opts || {}),
  workRoot: path.join(DATA_DIR, 'playground'),
}));
ipcMain.handle('compiler:set', (_e, p) => runner.setCompiler(p));
