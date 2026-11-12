# -*- coding: utf-8 -*-
"""补充练习：给只有一道题的课时再加一道，凑齐每课 2 题。"""

EXERCISES_EXTRA = {
    "l29": [
        {
            "q": "用条件变量实现“等一个标志位变成 true 再继续”，最多等 500 毫秒。",
            "hint": "wait_for 带超时，返回是否被唤醒。",
            "answer": r"""#include <chrono>
#include <condition_variable>
#include <iostream>
#include <mutex>
#include <thread>

std::mutex m;
std::condition_variable cv;
bool ready = false;

int main() {
    std::thread worker([]{
        std::this_thread::sleep_for(std::chrono::milliseconds(200));
        { std::lock_guard<std::mutex> lk(m); ready = true; }
        cv.notify_one();
    });

    std::unique_lock<std::mutex> lk(m);
    bool ok = cv.wait_for(lk, std::chrono::milliseconds(500), []{ return ready; });
    std::cout << (ok ? "等到了" : "超时了") << '\n';

    worker.join();
    return 0;
}""",
            "note": "wait_for 返回谓词最终是否为真，超时返回 false，不会抛异常。",
        },
    ],
    "l30": [
        {
            "q": "用 atomic 实现一个简单的自旋锁（用 flag 加 compare_exchange）。",
            "hint": "CAS 成功就拿到锁，失败就循环重试。",
            "answer": r"""#include <atomic>
#include <iostream>
#include <thread>

class SpinLock {
public:
    void lock() {
        bool expected = false;
        while (!flag_.compare_exchange_weak(expected, true)) {
            expected = false;          // 每轮都要重置
        }
    }
    void unlock() { flag_.store(false); }
private:
    std::atomic<bool> flag_{false};
};

SpinLock g;
int counter = 0;

int main() {
    std::thread a([]{ for (int i = 0; i < 1000; ++i) { g.lock(); ++counter; g.unlock(); } });
    std::thread b([]{ for (int i = 0; i < 1000; ++i) { g.lock(); ++counter; g.unlock(); } });
    a.join();
    b.join();
    std::cout << counter << '\n';
    return 0;
}""",
            "note": "自旋锁在竞争激烈时会空转烧 CPU，实践中优先用 std::mutex。",
        },
    ],
    "l31": [
        {
            "q": "用 async 并行计算 4 段区间，演示把任务分块。",
            "hint": "把区间按四等分，各起一个 async。",
            "answer": r"""#include <future>
#include <iostream>
#include <vector>

int main() {
    std::vector<int> v(400, 1);
    std::vector<std::future<int>> fs;

    for (int k = 0; k < 4; ++k) {
        int a = k * 100, b = a + 100;
        fs.push_back(std::async(std::launch::async, [&v, a, b] {
            int s = 0;
            for (int i = a; i < b; ++i) s += v[i];
            return s;
        }));
    }

    int total = 0;
    for (auto& f : fs) total += f.get();
    std::cout << total << '\n';        // 400
    return 0;
}""",
            "note": "注意 lambda 捕获的是引用 v，必须保证 v 活到所有 get 完成之后。",
        },
    ],
    "l32": [
        {
            "q": "演示循环包含的问题：A 需要 B、B 需要 A，用前置声明打破。",
            "hint": "class B; 只声明类型名，不包含 B 的头文件。",
            "answer": r"""#include <iostream>

// 前置声明，代替 #include "B.h"
class B;

class A {
public:
    void useB(B* b);       // 只用指针，不需要完整定义
    int value() const { return 1; }
};

class B {
public:
    int fromA(A* a) { return a->value(); }
};

void A::useB(B* b) {
    if (b) std::cout << "A 用了 B\n";
}

int main() {
    A a; B b;
    a.useB(&b);
    std::cout << b.fromA(&a) << '\n';
    return 0;
}""",
            "note": "只要函数体里没有真正访问对象成员，指针和引用的前置声明就够了。",
        },
    ],
    "l33": [
        {
            "q": "在 CMakeLists.txt 里加一条自定义命令，构建时自动打印项目版本号。",
            "hint": "add_custom_target 配 COMMAND。",
            "answer": r"""#include <iostream>

// CMakeLists.txt 里可以这样加一步：
//   add_custom_target(showver
//       COMMAND ${CMAKE_COMMAND} -E echo "版本: ${PROJECT_VERSION}"
//   )
// 构建：cmake --build build --target showver

int main() {
    std::cout << "主程序\n";
    return 0;
}""",
            "note": "add_custom_target 适合跑代码生成、拷贝资源这类构建期动作。",
        },
    ],
    "l34": [
        {
            "q": "写一个会崩的程序（空指针解引用），然后用 gdb 看 backtrace 定位到行。",
            "hint": "编译加 -g -O0，崩了之后敲 bt。",
            "answer": r"""#include <iostream>

void crash() {
    int* p = nullptr;
    *p = 1;                    // 空指针解引用，直接崩
}

int main() {
    std::cout << "准备崩\n";
    crash();
    std::cout << "不会到这里\n";
    return 0;
}

// g++ -g -O0 crash.cpp -o crash
// gdb ./crash  ->  run  ->  bt""",
            "note": "backtrace 会显示 crash() 在第几行，frame N 可以切到任意一层栈帧看变量。",
        },
    ],
    "l35": [
        {
            "q": "用 ASan 检测一个“返回局部数组指针”的错误。",
            "hint": "这类错误 ASan 报的是 stack-use-after-return 或 stack-buffer。",
            "answer": r"""#include <iostream>

int* makeArray() {
    int local[4] = {1, 2, 3, 4};
    return local;              // 返回栈上数组的地址，悬空
}

int main() {
    int* p = makeArray();
    std::cout << p[0] << '\n'; // 读已销毁的栈内存
    return 0;
}

// -g -fsanitize=address 会指出这是返回后使用栈内存""",
            "note": "正确做法是返回 std::vector<int> 或 std::array，让所有权清晰。",
        },
    ],
    "l36": [
        {
            "q": "比较 vector 和 list 顺序遍历一万个元素的耗时，感受缓存的作用。",
            "hint": "两者都遍历一遍累加，看差距。",
            "answer": r"""#include <chrono>
#include <iostream>
#include <list>
#include <vector>

template <typename C>
long long bench(const C& c) {
    auto t0 = std::chrono::steady_clock::now();
    long long s = 0;
    for (auto& x : c) s += x;
    auto ms = std::chrono::duration_cast<std::chrono::microseconds>(
                  std::chrono::steady_clock::now() - t0).count();
    std::cout << ms << " us  ";
    return s;
}

int main() {
    std::vector<int> v(100000, 1);
    std::list<int>   l(100000, 1);
    bench(v);
    bench(l);
    std::cout << '\n';        // vector 通常快一个量级
    return 0;
}""",
            "note": "list 每个节点单独分配，遍历时缓存几乎全部失效，这就是“链表慢”的真正原因。",
        },
    ],
    "l37": [
        {
            "q": "写一个函数模板 swap_values，交换两个同类型变量。",
            "hint": "参数用引用。",
            "answer": r"""#include <iostream>
#include <string>

template <typename T>
void swap_values(T& a, T& b) {
    T t = a; a = b; b = t;
}

int main() {
    int x = 1, y = 2;
    swap_values(x, y);
    std::cout << x << ' ' << y << '\n';

    std::string s1 = "a", s2 = "b";
    swap_values(s1, s2);
    std::cout << s1 << ' ' << s2 << '\n';
    return 0;
}""",
            "note": "标准库的 std::swap 就是这么实现的，而且对容器有更高效的版本。",
        },
    ],
    "l38": [
        {
            "q": "给类模板加一个 static 成员，统计一共创建了多少个实例（每种类型独立计数）。",
            "hint": "每个实例化出来的类模板都有自己的 static 成员。",
            "answer": r"""#include <iostream>

template <typename T>
class Counted {
public:
    Counted() { ++alive_; }
    ~Counted() { --alive_; }
    static int alive() { return alive_; }
private:
    static inline int alive_ = 0;   // C++17 起可以内联定义
};

int main() {
    Counted<int> a, b;
    Counted<double> c;
    std::cout << Counted<int>::alive() << ' '
              << Counted<double>::alive() << '\n';   // 2 1
    return 0;
}""",
            "note": "Counted<int> 和 Counted<double> 是两个不同的类，各自有一份计数器。",
        },
    ],
    "l39": [
        {
            "q": "用 type_traits 实现一个编译期判断：两个类型是否相同。",
            "hint": "std::is_same_v<T, U>。",
            "answer": r"""#include <iostream>
#include <type_traits>

template <typename A, typename B>
void check() {
    if constexpr (std::is_same_v<A, B>) {
        std::cout << "相同\n";
    } else {
        std::cout << "不同\n";
    }
}

int main() {
    check<int, int>();             // 相同
    check<int, long>();            // 不同
    check<const int, int>();       // 不同（const 也算类型的一部分）
    return 0;
}""",
            "note": "比较类型时要留意 const、引用这些限定符都会被算进类型里。",
        },
    ],
    "l40": [
        {
            "q": "用 concept 约束一个函数只能接受浮点类型，传 int 时报错要能看懂。",
            "hint": "template <std::floating_point T>。",
            "answer": r"""#include <concepts>
#include <iostream>

template <std::floating_point T>
T half(T v) { return v / 2; }

int main() {
    std::cout << half(3.0) << '\n';    // 1.5
    // half(3);                        // 编译错误：int 不满足 floating_point
    return 0;
}""",
            "note": "把注释掉那行打开，看看报错有多简洁——这就是 concepts 最大的价值。",
        },
    ],
    "l41": [
        {
            "q": "用 ranges 统计一段数字里的奇数个数，不要手写循环计数。",
            "hint": "std::ranges::count_if。",
            "answer": r"""#include <algorithm>
#include <iostream>
#include <ranges>
#include <vector>

int main() {
    std::vector<int> v{1,2,3,4,5,6,7,8,9};
    auto n = std::ranges::count_if(v, [](int x){ return x % 2 != 0; });
    std::cout << "奇数 " << n << " 个\n";
    return 0;
}""",
            "note": "ranges 版算法可以直接传容器，不用写 begin()/end()。",
        },
    ],
    "l42": [
        {
            "q": "写一个函数用 string_view 统计字符串长度，并验证传字面量不会构造 std::string。",
            "hint": "函数参数写 std::string_view。",
            "answer": r"""#include <iostream>
#include <string>
#include <string_view>

std::size_t len(std::string_view s) { return s.size(); }

int main() {
    std::cout << len("hello") << '\n';           // 字面量，零拷贝
    std::cout << len(std::string("world")) << '\n';
    return 0;
}""",
            "note": "注意 string_view 不拥有内存，别把它存起来指向已销毁的字符串。",
        },
    ],
    "l43": [
        {
            "q": "写一个结构体，用 <=> 支持比较，并试试用 sort 排序。",
            "hint": "默认 <=> 会按成员顺序比较。",
            "answer": r"""#include <algorithm>
#include <iostream>
#include <vector>

struct Item {
    int priority = 0;
    std::string name;
    auto operator<=>(const Item&) const = default;
};

int main() {
    std::vector<Item> v{{3, "c"}, {1, "a"}, {2, "b"}};
    std::sort(v.begin(), v.end());
    for (const auto& it : v) std::cout << it.name << ' ';
    std::cout << '\n';        // a b c
    return 0;
}""",
            "note": "成员顺序决定比较优先级：先比 priority，相同的再比 name。",
        },
    ],
    "l44": [
        {
            "q": "自定义一个异常类型，继承 std::runtime_error，抛出并捕获。",
            "hint": "构造函数把消息传给基类。",
            "answer": r"""#include <iostream>
#include <stdexcept>

class ParseError : public std::runtime_error {
public:
    explicit ParseError(const std::string& msg) : std::runtime_error(msg) {}
};

int parse(const std::string& s) {
    if (s.empty()) throw ParseError("输入为空");
    return static_cast<int>(s.size());
}

int main() {
    try {
        parse("");
    } catch (const ParseError& e) {
        std::cout << "解析失败: " << e.what() << '\n';
    }
    return 0;
}""",
            "note": "继承标准异常后，上层一个 catch (const std::exception&) 就能兜住所有异常。",
        },
    ],
    "l45": [
        {
            "q": "用 RAII 写一个计时器，构造时记时间，析构时打印耗时。",
            "hint": "析构函数里算差值并输出。",
            "answer": r"""#include <chrono>
#include <iostream>

class Timer {
public:
    Timer() : t0_(std::chrono::steady_clock::now()) {}
    ~Timer() {
        auto us = std::chrono::duration_cast<std::chrono::microseconds>(
                      std::chrono::steady_clock::now() - t0_).count();
        std::cout << "耗时 " << us << " us\n";
    }
private:
    std::chrono::steady_clock::time_point t0_;
};

int main() {
    Timer t;
    long long s = 0;
    for (int i = 0; i < 1000000; ++i) s += i;
    std::cout << s << '\n';
    return 0;
}""",
            "note": "这种写法不会漏掉任何一条退出路径，包括提前 return 和抛异常。",
        },
    ],
    "l46": [
        {
            "q": "写一个测试用的断言宏，失败时打印表达式和行号。",
            "hint": "用 #x 把表达式变成字符串。",
            "answer": r"""#include <iostream>

#define CHECK(x) do {                                   \
    if (!(x)) {                                         \
        std::cout << "失败: " #x "  行 " << __LINE__ << '\n'; \
    } else {                                            \
        std::cout << "通过: " #x << '\n';                \
    }                                                   \
} while (0)

int main() {
    CHECK(1 + 1 == 2);
    CHECK(2 * 3 == 7);
    return 0;
}""",
            "note": "#x 是字符串化操作符，宏里的 do {} while(0) 是为了让它像一条语句一样安全。",
        },
    ],
    "l47": [
        {
            "q": "把记账程序的数据模型改成支持“标签”（一笔账可以有多个标签），先设计再写结构体。",
            "hint": "用 vector<string> 存标签，思考存盘时怎么表示。",
            "answer": r"""#include <iostream>
#include <string>
#include <vector>

struct Transaction {
    std::string date;
    double      amount = 0;
    std::vector<std::string> tags;     // 一笔可以有多个标签

    bool hasTag(const std::string& t) const {
        for (const auto& x : tags) if (x == t) return true;
        return false;
    }
};

int main() {
    Transaction t{"2024-05-01", -32.5, {"餐饮", "工作餐"}};
    std::cout << (t.hasTag("工作餐") ? "有" : "没有") << '\n';
    // 存盘时可能写成：2024-05-01,-32.5,餐饮|工作餐
    return 0;
}""",
            "note": "多值字段存 CSV 就会遇到分隔符冲突，这正是上一课提到的“格式局限”。",
        },
    ],
    "l48": [
        {
            "q": "给 Ledger 加一个方法：返回支出最多的分类名。",
            "hint": "复用 byCategory，然后挑出金额最小的那个（支出是负数）。",
            "answer": r"""#include <algorithm>
#include <iostream>
#include <string>
#include <vector>

struct T { std::string cat; double amount; };

std::string topExpense(const std::vector<T>& v) {
    if (v.empty()) return "";
    auto it = std::min_element(v.begin(), v.end(),
        [](const T& a, const T& b) { return a.amount < b.amount; });
    return it->cat;
}

int main() {
    std::vector<T> v{{"餐饮", -320}, {"交通", -80}, {"工资", 8000}};
    std::cout << "花得最多的类别: " << topExpense(v) << '\n';
    return 0;
}""",
            "note": "因为支出是负数，金额越小代表花得越多，所以用 min_element 而不是 max_element。",
        },
    ],
    "l49": [
        {
            "q": "给存盘格式加一个版本号首行，读盘时检查版本，不匹配就拒绝加载。",
            "hint": "第一行写 #v1，读的时候先读这行判断。",
            "answer": r"""#include <fstream>
#include <iostream>
#include <sstream>
#include <string>

int main() {
    {
        std::ofstream out("data.txt");
        out << "#v1\n";
        out << "2024-05-01,餐饮,-32.5,午餐\n";
    }
    {
        std::ifstream in("data.txt");
        std::string header;
        std::getline(in, header);
        if (header != "#v1") {
            std::cout << "格式版本不支持: " << header << '\n';
            return 1;
        }
        std::string line;
        while (std::getline(in, line)) std::cout << "读到 " << line << '\n';
    }
    return 0;
}""",
            "note": "版本号是持久化格式最重要的防御手段，将来改格式才有升级的余地。",
        },
    ],
    "l50": [
        {
            "q": "给主循环加一个“清屏”选项，并做一个简单的命令行参数支持（--file 指定数据文件）。",
            "hint": "main 的 argc/argv 就是命令行参数。",
            "answer": r"""#include <iostream>
#include <string>

int main(int argc, char** argv) {
    std::string dataFile = "ledger.csv";     // 默认值

    for (int i = 1; i < argc; ++i) {
        std::string a = argv[i];
        if (a == "--file" && i + 1 < argc) {
            dataFile = argv[++i];
        }
    }

    std::cout << "使用数据文件: " << dataFile << '\n';
    // 运行：account_book.exe --file my.csv
    return 0;
}""",
            "note": "更复杂的命令行解析可以用 getopt 或者第三方库 CLI11。",
        },
    ],
}
