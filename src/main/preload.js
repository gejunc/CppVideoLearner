'use strict';

const { contextBridge, ipcRenderer } = require('electron');
const path = require('node:path');
const fs = require('node:fs');

// assets 与 src 同级（打包后依然成立，因为 asar 已关闭）
const ASSETS = path.join(__dirname, '..', '..', 'assets');

function assetPath(rel) {
  return path.join(ASSETS, rel.replace(/^[/\\]+/, ''));
}

function toFileUrl(abs) {
  return 'file:///' + abs.replace(/\\/g, '/');
}

contextBridge.exposeInMainWorld('cpp', {
  // 状态持久化
  loadState: () => ipcRenderer.invoke('state:load'),
  saveState: (state) => ipcRenderer.invoke('state:save', state),
  appInfo: () => ipcRenderer.invoke('app:info'),

  // 读取课程数据（file:// 下 fetch 受限，改走主进程侧的文件读取）
  readCourse: () => {
    const p = assetPath('data/course.json');
    return JSON.parse(fs.readFileSync(p, 'utf8'));
  },
  readVtt: (rel) => {
    try {
      return fs.readFileSync(assetPath(rel), 'utf8');
    } catch {
      return '';
    }
  },
  videoUrl: (rel) => toFileUrl(assetPath(rel)),
  thumbUrl: (rel) => toFileUrl(assetPath(rel)),

  // 平台信息：界面要按平台微调标题栏内边距与字体
  platform: process.platform,

  // 本地编译运行
  compilerStatus: (force) => ipcRenderer.invoke('compiler:status', !!force),
  runCode: (opts) => ipcRenderer.invoke('compiler:run', opts),
  setCompiler: (p) => ipcRenderer.invoke('compiler:set', p),

  // 窗口控制
  minimize: () => ipcRenderer.invoke('window:minimize'),
  maximize: () => ipcRenderer.invoke('window:maximize'),
  close: () => ipcRenderer.invoke('window:close'),
});
