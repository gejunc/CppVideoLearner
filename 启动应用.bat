@echo off
chcp 65001 >nul
setlocal
cd /d "%~dp0"

REM 部分受限环境（企业策略、远程桌面、沙箱）下，Chromium 需要显式关闭沙箱，
REM 并把用户数据目录放在程序可写位置，否则会直接崩溃。
REM 正常个人电脑上直接双击 release\CppVideoLearner.exe 即可，不需要这个脚本。

set ELECTRON_RUN_AS_NODE=
if not exist "node_modules\electron\dist\electron.exe" (
  echo [错误] 找不到 Electron，请先执行： pnpm install
  pause
  exit /b 1
)

if not exist ".userdata" mkdir ".userdata"

echo 正在启动 C++ 视频学习...
start "" "node_modules\electron\dist\electron.exe" . --no-sandbox --user-data-dir="%CD%\.userdata"
exit /b 0
