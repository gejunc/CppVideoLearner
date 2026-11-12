# macOS 打包指南（每个新软件都要走一遍）

这份文档解决一件事：**Windows 上开发、也能给 macOS 用户出包**。

核心结论先说：`electron-builder` 拒绝在 Windows 上构建 macOS 目标。

```
⨯ Build for macOS is supported only on macOS
```

所以要么有一台 Mac，要么用 GitHub Actions 的 macOS 机器。下面两部分：
[一、代码层面必须做的跨平台适配](#一代码层面必须做的跨平台适配)（不做好，包出来了也跑不对）
[二、两种出包方式](#二两种出包方式)。

---

## 一、代码层面必须做的跨平台适配

这些是踩过的坑，新项目直接照做。

### 1. 编译器探测（如果软件要调用本地工具链）

```js
const IS_WIN = process.platform === 'win32';
const IS_MAC = process.platform === 'darwin';
const EXE_SUFFIX = IS_WIN ? '.exe' : '';

// 各平台的可执行文件名不同
function compilerNames() {
  if (IS_WIN) return ['g++' + EXE_SUFFIX, 'clang++' + EXE_SUFFIX];
  return ['clang++', 'g++', 'c++'];   // macOS 系统自带 clang++
}

// 固定位置兜底
const fixed = ['/usr/bin/clang++', '/opt/homebrew/bin/clang++',
               '/usr/local/bin/clang++'];
```

macOS 上 `clang++` 来自 Xcode Command Line Tools：`xcode-select --install`。

### 2. 编译参数必须分支

```js
const args = ['-std=' + std, '-O0', '-Wall', '-Wextra'];
if (IS_WIN) args.push('-static-libgcc', '-static-libstdc++');  // 仅 MinGW 需要
```

`clang` 不认 `-static-libstdc++`，加上会直接编译失败。

### 3. 子进程终止不能用 taskkill

```js
function killTree(child) {
  if (!child || !child.pid) return;
  if (IS_WIN) {
    spawn('taskkill', ['/PID', String(child.pid), '/T', '/F'], { stdio: 'ignore' });
    return;
  }
  try { child.kill('SIGKILL'); } catch {}
}
```

### 4. 产物文件名

```js
const exeFile = path.join(work, IS_WIN ? 'main.exe' : 'main');
```

### 5. macOS 必须有应用菜单

```js
if (process.platform === 'darwin') {
  Menu.setApplicationMenu(Menu.buildFromTemplate([
    { role: 'appMenu' }, { role: 'editMenu' },
    { role: 'viewMenu' }, { role: 'windowMenu' },
  ]));
} else {
  Menu.setApplicationMenu(null);
}
```

**没有菜单栏，`Cmd+C` / `Cmd+V` / `Cmd+Q` 全部失效**，这是最容易漏的一条。

### 6. 标题栏

```js
titleBarStyle: isMac ? 'hiddenInset' : 'hidden',
// titleBarOverlay 只在 Windows 生效，不要给 mac 设
```

macOS 的红绿灯在左上角，CSS 要给标题栏让位：

```css
body.platform-darwin .titlebar { padding-left: 88px; }
```

界面里打平台标记：

```js
document.body.classList.add('platform-' + (window.cpp.platform || 'win32'));
```

### 7. 字体栈

不写 Mac 字体会掉到难看的默认字体：

```css
font-family: "Microsoft YaHei UI", "Microsoft YaHei",
             "PingFang SC", "Hiragino Sans GB", "Heiti SC",
             system-ui, -apple-system, sans-serif;

--mono: "Cascadia Mono", "Consolas", "SF Mono", "Menlo", "Monaco", monospace;
```

### 8. 图标

macOS 用 1024×1024 PNG，`electron-builder` 会自动转 `.icns`：

```json
"mac": { "icon": "build/icon.png" }
```

### 9. 窗口关闭行为

macOS 关窗口不退出应用，要在 Dock 里能重新打开：

```js
app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') app.quit();
});
app.on('activate', () => {
  if (BrowserWindow.getAllWindows().length === 0) createWindow();
});
```

### 10. 路径

不要手拼 `\\`，用 `path.join`；`file://` 转换要 `replace(/\\/g, '/')`。

---

## 二、两种出包方式

### 方式 A：有 Mac

```bash
xcode-select --install                 # 命令行工具（clang++ 也来自这里）
pnpm install
node node_modules/electron/install.js  # pnpm 会拦 postinstall，手动补
pnpm run build:mac                     # 同时出 arm64 与 x64 的 dmg
```

产物：

```
release/CppVideoLearner-2.0.0-arm64.dmg
release/CppVideoLearner-2.0.0-x64.dmg
```

### 方式 B：没有 Mac，用 GitHub Actions

仓库里已配好 `.github/workflows/build-mac.yml`：

1. 代码推到 GitHub
2. Actions → **Build macOS** → Run workflow
3. 跑完在运行页底部下载 Artifacts

**注意资源体积**：本项目 `assets/videos/` 有 237 MB，要一起提交。单个 mp4 都远小于 GitHub 的
100 MB 单文件上限，可以直接提交；嫌仓库大就上 Git LFS。

---

## 三、签名与公证

### 不签名（现在的方式）

```json
"mac": { "identity": null }
```

用户首次打开会被 Gatekeeper 拦：

- 提示「无法验证开发者」→ 右键 App → 打开
- 或提示「已损坏」→ 终端执行 `xattr -cr /Applications/xxx.app`

### 签名 + 公证（想彻底免提示）

需要 Apple Developer Program（99 美元/年）：

```json
"mac": {
  "identity": "Developer ID Application: Your Name (TEAMID)",
  "hardenedRuntime": true,
  "gatekeeperAssess": false,
  "notarize": { "teamId": "TEAMID" }
}
```

CI 里通过环境变量提供证书：

```
CSC_LINK=<base64 或 p12 路径>
CSC_KEY_PASSWORD=<密码>
APPLE_ID / APPLE_APP_SPECIFIC_PASSWORD / APPLE_TEAM_ID
```

---

## 四、新软件检查清单

每个新软件出 Mac 版之前，逐条过一遍：

- [ ] 所有 `spawn` / `exec` 的路径有平台分支
- [ ] 不用 `taskkill`，改用 `SIGKILL`
- [ ] 产物文件名不含写死的 `.exe`
- [ ] macOS 有应用菜单
- [ ] `titleBarStyle` 按平台分支，不滥用 `titleBarOverlay`
- [ ] CSS 字体栈含 PingFang SC / SF Mono
- [ ] 图标有 1024×1024 PNG
- [ ] `window-all-closed` / `activate` 处理正确
- [ ] 路径拼接全部用 `path.join`
- [ ] 在 Mac 上实跑一次：启动、窗口、快捷键、核心功能
- [ ] `pnpm run build:mac` 能出 dmg
- [ ] 把 dmg 传到下载服务，更新网站 `softwares.js` 的下载项

---

## 五、常见问题

**Q：Windows 上能不能用 WSL 出 mac 包？**
不能。WSL 是 Linux，同样不支持 macOS 目标。

**Q：能不能用 Docker 出 mac 包？**
不能。需要真实的 macOS 内核与 `hdiutil`。

**Q：云 Mac 怎么租？**
MacStadium、AWS EC2 mac 实例、MacinCloud，按小时计费，几分钟能装好环境跑一遍构建。

**Q：dmg 有 500 MB 正常吗？**
正常。视频资源占大头，和 Windows 版体积接近。
