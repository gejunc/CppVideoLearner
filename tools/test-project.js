'use strict';

/** 验证项目课里的记账程序能真实编译运行（含标准输入交互）。 */

const fs = require('node:fs');
const path = require('node:path');
const r = require(path.join(__dirname, '..', 'src', 'main', 'runner'));

const SRC = path.join(__dirname, '..', 'assets', 'samples', 'account_book.cpp');
const code = fs.readFileSync(SRC, 'utf8');

// 模拟：记一笔支出、记一笔收入、看明细、看统计、退出
const stdin = [
  '1', '2024-05-01', '餐饮', '-32.5', '午餐',
  '1', '2024-05-02', '工资', '8000', '五月工资',
  '2',
  '4',
  '0',
].join('\n') + '\n';

(async () => {
  console.log('源码行数:', code.split('\n').length);
  const res = await r.compileAndRun({
    code,
    stdin,
    std: 'c++20',
    timeoutMs: 8000,
    workRoot: path.join(__dirname, '..', '.tmp', 'proj'),
  });
  console.log('\n状态:', res.stage, res.ok ? 'OK' : 'FAIL');
  if (res.message) console.log('消息:', res.message);
  if (res.output) {
    console.log('---- 程序输出 ----');
    console.log(res.output);
  }
  process.exit(res.ok ? 0 : 1);
})();
