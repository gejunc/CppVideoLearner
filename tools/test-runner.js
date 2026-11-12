'use strict';

/** 直接调用主进程的编译运行器，验证调用链路（不经过界面）。 */

const path = require('node:path');
const r = require(path.join(__dirname, '..', 'src', 'main', 'runner'));

const HELLO = `#include <iostream>
int main() {
    int a = 7, b = 2;
    std::cout << "hello " << a / b << " " << a / 2.0 << std::endl;
    return 0;
}`;

const CIN = `#include <iostream>
#include <string>
int main() {
    std::string name; int age;
    std::cin >> name >> age;
    std::cout << name << " is " << age << std::endl;
}`;

const BROKEN = `int main() {
    return undefined_var;
}`;

const INFINITE = `int main() { while (true) {} }`;

const CXX20 = `#include <iostream>
#include <vector>
#include <ranges>
int main() {
    std::vector<int> v{1,2,3,4,5,6};
    for (int x : v | std::views::filter([](int n){ return n % 2 == 0; }))
        std::cout << x << ' ';
    std::cout << '\\n';
}`;

function show(title, res) {
  console.log(`\n=== ${title} ===`);
  if (res.ok) {
    console.log(`[OK] exit=${res.exitCode} ${res.elapsedMs}ms`);
    console.log(res.output.trim().slice(0, 400));
  } else {
    console.log(`[FAIL stage=${res.stage}] ${res.message || ''}`);
    if (res.output) console.log(res.output.trim().split('\n').slice(0, 6).join('\n'));
  }
}

(async () => {
  const st = await r.detectCompiler();
  console.log('编译器探测:', st.found ? st.version : '未找到');
  if (st.found) console.log('  路径:', st.path);
  if (!st.found) process.exit(1);

  show('普通输出', await r.compileAndRun({ code: HELLO }));
  show('标准输入', await r.compileAndRun({ code: CIN, stdin: 'Tom 18\n' }));
  show('编译错误', await r.compileAndRun({ code: BROKEN }));
  show('死循环超时', await r.compileAndRun({ code: INFINITE, timeoutMs: 1500 }));
  show('C++20 ranges', await r.compileAndRun({ code: CXX20, std: 'c++20' }));
  show('空代码', await r.compileAndRun({ code: '   ' }));

  console.log('\n全部场景执行完毕');
})();
