# -*- coding: utf-8 -*-
"""C++ 视频课程内容 —— 第 9 ~ 14 章（进阶篇）。

约定与 course_a / course_b 完全一致：
  cover / bullets / code / term / recap 五种页面，
  narration 是该页旁白，决定页面时长。
"""

CHAPTERS_C = [
    # ================= 第 9 章 并发 =================
    {
        "id": "ch9",
        "title": "第 9 章 · 并发编程",
        "desc": "线程、锁、条件变量、原子操作——让程序同时做几件事。",
        "lessons": [
            {
                "id": "l27",
                "title": "线程基础：std::thread",
                "minutes": 5,
                "tags": ["thread", "并发", "join"],
                "pages": [
                    {
                        "kind": "cover",
                        "title": "线程基础",
                        "subtitle": "让程序同时做几件事",
                        "narration": "前面所有代码都是单线程的，一条路走到黑。这一章我们打开并发这扇门。先说一句最重要的话：并发不是性能银弹，它先带来的是复杂度。",
                    },
                    {
                        "kind": "code",
                        "title": "创建与等待",
                        "code": """#include <iostream>
#include <thread>

void work(int id) {
    std::cout << "线程 " << id << " 开始\\n";
}

int main() {
    std::thread t1(work, 1);
    std::thread t2(work, 2);

    t1.join();   // 等它结束
    t2.join();
    std::cout << "全部完成\\n";
}""",
                        "narration": "std::thread 构造时就把函数丢到新线程里跑，参数跟在函数名后面。两个 join 表示主线程在这里等它们结束。记住 join 的必要性：thread 析构时如果还是 joinable 状态，程序会直接调用 terminate 终止，这是很多人第一次写线程就遇到的崩溃。",
                    },
                    {
                        "kind": "code",
                        "title": "join 与 detach",
                        "code": """std::thread t([]{ std::cout << "hi\\n"; });

if (t.joinable()) {
    t.join();      // 等待结束，回收资源
}

// 或者脱离：后台自己跑，且不能再 join
std::thread bg([]{ /* 长时间任务 */ });
bg.detach();

// 危险：detach 后访问已经销毁的局部变量
void bad() {
    int local = 1;
    std::thread t([&]{ std::cout << local; });
    t.detach();    // bad 返回后 local 已经没了
}""",
                        "narration": "每个线程必须二选一：join 等待，或者 detach 放养。detach 的陷阱是悬空引用，线程还在跑，但它引用的局部变量已经随函数返回销毁了。写并发代码的第一原则：先想清楚每个线程活多久，它碰的数据活多久。",
                    },
                    {
                        "kind": "bullets",
                        "title": "并发的三条铁律",
                        "items": [
                            ("数据竞争是未定义行为", "两个线程同时读写同一变量且无同步 = UB，不是“偶尔出错”"),
                            ("线程要么 join 要么 detach", "否则析构时 std::terminate"),
                            ("能不用线程就不用", "先把单线程写对、写快，再考虑并发"),
                        ],
                        "narration": "三条铁律。第一，数据竞争是未定义行为，编译器可以做任何事，包括让代码静默消失。第二，线程必须 join 或 detach。第三，也是最重要的：优先优化单线程。很多所谓需要并发的场景，其实只是算法写得不够好。",
                    },
                    {
                        "kind": "recap",
                        "title": "本课回顾",
                        "items": [
                            "std::thread 构造即启动，参数跟在后面",
                            "join 等待回收，detach 放养但有悬空风险",
                            "数据竞争是 UB，不是“偶尔出错”",
                        ],
                        "narration": "下一课我们解决数据竞争：互斥量和锁。",
                    },
                ],
            },
            {
                "id": "l28",
                "title": "互斥量与锁：给数据加把门",
                "minutes": 5,
                "tags": ["mutex", "lock_guard", "死锁"],
                "pages": [
                    {
                        "kind": "cover",
                        "title": "互斥量与锁",
                        "subtitle": "mutex · lock_guard · 死锁",
                        "narration": "多个线程改同一个变量，就会出现数据竞争。互斥量是最直接的解决办法：一把锁，谁拿到谁改，别人排队。",
                    },
                    {
                        "kind": "code",
                        "title": "手写 lock / unlock 是错的",
                        "code": """// 反面教材
int counter = 0;
std::mutex m;

void bad() {
    m.lock();
    if (someCondition) return;   // 忘了 unlock！
    counter++;
    m.unlock();
}

// 正确写法：RAII
void good() {
    std::lock_guard<std::mutex> lock(m);
    counter++;                   // 离开作用域自动解锁
}""",
                        "narration": "手写 lock 和 unlock 一定会出事：中间任何一次提前返回、抛异常，锁就永远不释放，其他线程全部卡死。所以标准库提供了 lock guard：构造时加锁，析构时解锁，异常和提前返回都安全。这就是 RAII 在并发里的应用。",
                    },
                    {
                        "kind": "code",
                        "title": "几种锁的取舍",
                        "code": """std::mutex m;

std::lock_guard<std::mutex> a(m);      // 最简单，不可手动解锁

std::unique_lock<std::mutex> b(m);     // 更灵活：可提前 unlock
b.unlock();

std::shared_mutex sm;                  // 读写锁（C++17）
{
    std::shared_lock sl(sm);           // 多个读者可同时持有
    read();
}
{
    std::unique_lock ul(sm);           // 写者独占
    write();
}

// 多个互斥量一起用：std::scoped_lock 一次性锁住，避免死锁
std::scoped_lock both(m1, m2);""",
                        "narration": "选择顺序：默认用 lock guard；需要中途解锁或者配合条件变量，用 unique lock；读多写少的场景用 shared mutex 加 shared lock；需要同时锁多个互斥量，一定用 scoped lock，它内部会按固定顺序加锁，避免死锁。",
                    },
                    {
                        "kind": "code",
                        "title": "死锁是怎么发生的",
                        "code": """// 线程 A          线程 B
// lock(m1);       lock(m2);
// lock(m2);       lock(m1);   ← 互相等对方，永远卡住

// 修法一：固定加锁顺序
void f() {
    std::scoped_lock lock(m1, m2);   // 内部按地址排序加锁
}

// 修法二：一切都在同一个锁里做，别嵌套
// 修法三：缩小临界区，尽量不在持锁时调用别人的代码

// 自查：持锁时调用外部回调 = 高风险""",
                        "narration": "死锁的经典成因是加锁顺序不一致：你等我的锁，我等你已经拿到的锁。解决办法是让所有人按同一顺序加锁，scoped lock 帮你做到了。还有一个更隐蔽的死锁：你持锁的时候调用了别人的回调函数，而那个回调又去拿同一把锁。原则是临界区越短越好，绝不在持锁时调用外部代码。",
                    },
                    {
                        "kind": "recap",
                        "title": "本课回顾",
                        "items": [
                            "永远用 lock_guard / unique_lock，别手写 lock",
                            "多锁用 scoped_lock，避免顺序死锁",
                            "临界区越短越好，持锁时别调外部代码",
                        ],
                        "narration": "锁能保证正确性，但它把并发变成了串行，性能会掉。下一课讲在没有数据可抢时怎么高效等待。",
                    },
                ],
            },
            {
                "id": "l29",
                "title": "条件变量与生产者消费者",
                "minutes": 6,
                "tags": ["condition_variable", "生产者消费者"],
                "pages": [
                    {
                        "kind": "cover",
                        "title": "条件变量",
                        "subtitle": "等一个条件，而不是空转",
                        "narration": "一个线程等另一个线程准备好数据，它该怎么等？轮询会浪费 CPU。条件变量就是标准答案：没准备好就睡，准备好了被叫醒。",
                    },
                    {
                        "kind": "code",
                        "title": "生产者消费者骨架",
                        "code": """#include <queue>
#include <mutex>
#include <condition_variable>

std::mutex mtx;
std::condition_variable cv;
std::queue<int> q;

void producer() {
    for (int i = 0; i < 10; ++i) {
        {
            std::lock_guard<std::mutex> lk(mtx);
            q.push(i);
        }
        cv.notify_one();          // 通知一个等待者
    }
}

void consumer() {
    while (true) {
        std::unique_lock<std::mutex> lk(mtx);
        cv.wait(lk, []{ return !q.empty(); });  // 睡到有数据
        int v = q.front(); q.pop();
        lk.unlock();
        use(v);                    // 耗时处理放在锁外
    }
}""",
                        "narration": "生产者往队列塞数据，塞完 notify one 叫醒一个消费者。消费者用 unique lock 配合 wait，第二个参数是谓词：它在被唤醒后重新检查条件，条件不满足就继续睡。这个谓词不是可选项，它防的是虚假唤醒。还有一点很重要：数据取出来之后先解锁，再做耗时处理，否则并发又退化成串行。",
                    },
                    {
                        "kind": "bullets",
                        "title": "三个必须知道的细节",
                        "items": [
                            ("必须用谓词版本", "wait 可能在没通知的情况下自己醒来（虚假唤醒）"),
                            ("notify 不必持锁", "持锁 notify 会让被唤醒者立刻又阻塞，白白多切换一次"),
                            ("带停止标志", "消费者要能优雅退出，否则永远等下去"),
                        ],
                        "narration": "三个细节。第一，一定要用带谓词的 wait，虚假唤醒是真会发生的。第二，notify 不需要持锁，持锁通知只会让被叫醒的线程立刻又撞在锁上。第三，别忘了停止标志，生产者结束后要能让消费者退出，不然程序卡在那里不退。",
                    },
                    {
                        "kind": "code",
                        "title": "带退出条件的版本",
                        "code": """std::atomic<bool> done{false};

void consumer() {
    while (true) {
        std::unique_lock<std::mutex> lk(mtx);
        cv.wait(lk, []{ return done || !q.empty(); });

        if (q.empty() && done) return;   // 真正该退出了

        int v = q.front(); q.pop();
        lk.unlock();
        use(v);
    }
}

// 生产者结束时
{
    std::lock_guard<std::mutex> lk(mtx);
    done = true;
}
cv.notify_all();""",
                        "narration": "加一个 done 标志，谓词从“队列非空”变成“有数据或者已结束”。真正退出前还要再判一次：如果队列空了并且已经结束，才返回。通知用 notify all，让所有等待的消费者都重新检查条件。这个模式几乎所有后台任务队列都在用。",
                    },
                    {
                        "kind": "recap",
                        "title": "本课回顾",
                        "items": [
                            "wait 一定要带谓词，防虚假唤醒",
                            "notify 不必持锁，处理耗时任务要放到锁外",
                            "给消费者一个明确的停止条件",
                        ],
                        "narration": "下一课我们看更轻量的同步原语：原子操作，以及它背后那套容易被误解的内存序。",
                    },
                ],
            },
            {
                "id": "l30",
                "title": "原子操作与内存序",
                "minutes": 6,
                "tags": ["atomic", "内存序", "无锁"],
                "pages": [
                    {
                        "kind": "cover",
                        "title": "原子操作",
                        "subtitle": "atomic · memory order",
                        "narration": "如果只是一个计数器，用互斥量有点重。原子类型提供了不加锁的线程安全读写。但它背后有一套内存序规则，是 C++ 里最抽象的部分之一。",
                    },
                    {
                        "kind": "code",
                        "title": "基本用法",
                        "code": """#include <atomic>

std::atomic<int> counter{0};      // 注意：必须初始化

void add() {
    counter.fetch_add(1);         // 原子自增
    counter++;                    // 等价写法
}

int load() {
    return counter.load();        // 原子读
}

void store(int v) {
    counter.store(v);             // 原子写
}

// 常用成员
// fetch_add / fetch_sub / exchange / compare_exchange_weak""",
                        "narration": "atomic 包装一个类型，所有操作都是原子的，不会被其他线程看到中间状态。用 ++ 和 fetch add 效果一样，都是原子自增。compare exchange 是比较并交换，它是实现无锁数据结构的基石。注意 atomic 不能拷贝，而且必须初始化，未初始化的 atomic 是垃圾值。",
                    },
                    {
                        "kind": "code",
                        "title": "内存序：把默认值用好",
                        "code": """// 默认是顺序一致（seq_cst）：最安全，也最慢
counter.fetch_add(1, std::memory_order_seq_cst);

// 常用的三档
// relaxed        只保证原子性，不保证与其他变量的顺序
// acquire/release 成对使用，建立 happens-before 关系
// seq_cst        全局单一顺序，最好推理

// 典型：用 release 发布数据，用 acquire 接收
std::atomic<bool> ready{false};
int data = 0;

// 线程 A
data = 42;
ready.store(true, std::memory_order_release);

// 线程 B
while (!ready.load(std::memory_order_acquire)) {}
assert(data == 42);        // 保证能看到""",
                        "narration": "这是全课最难的一页，但你只需要记住一条实践准则：除非你在写底层库，否则全部用默认的 seq cst，不要自作聪明改内存序。默认值最安全，性能差异在绝大多数业务里根本测不出来。如果你一定要优化，记住 release 和 acquire 必须成对出现，它们建立的是一种“我改的东西，你能看见”的保证。",
                    },
                    {
                        "kind": "bullets",
                        "title": "什么时候适合用原子",
                        "items": [
                            ("单个计数器", "最典型的场景，性能远好于锁"),
                            ("标志位", "stop flag / ready flag"),
                            ("注意", "atomic 不能替代锁去保护多个变量的组合状态"),
                            ("ABA 问题", "CAS 循环里要小心值被改回原样"),
                        ],
                        "narration": "原子适合单个变量的场景：计数器、标志位。它不适合保护多个变量的组合状态，因为原子操作之间没有整体性，你还是得用锁。另外写无锁结构时要注意 ABA 问题：值从 A 变成 B 又变回 A，CAS 会误判成没变过。",
                    },
                    {
                        "kind": "recap",
                        "title": "本课回顾",
                        "items": [
                            "atomic 提供不加锁的单变量原子操作",
                            "内存序默认 seq_cst，不要轻易改",
                            "多变量的组合状态仍然要用锁",
                        ],
                        "narration": "下一课讲更高层的并发工具：async 和 future，它让你不用手动管线程。",
                    },
                ],
            },
            {
                "id": "l31",
                "title": "async、future 与线程池思想",
                "minutes": 5,
                "tags": ["async", "future", "线程池"],
                "pages": [
                    {
                        "kind": "cover",
                        "title": "更高层的并发",
                        "subtitle": "async · future · 线程池",
                        "narration": "手动管线程是件麻烦事：创建、join、异常传递，全都要自己处理。标准库提供了 async 和 future，让你像调用一个异步函数那样使用并发。",
                    },
                    {
                        "kind": "code",
                        "title": "std::async 与 future",
                        "code": """#include <future>
#include <numeric>
#include <vector>

int sum(const std::vector<int>& v, size_t a, size_t b) {
    return std::accumulate(v.begin() + a, v.begin() + b, 0);
}

int main() {
    std::vector<int> v(1000000, 1);
    size_t half = v.size() / 2;

    auto f1 = std::async(std::launch::async, sum, std::cref(v), 0, half);
    auto f2 = std::async(std::launch::async, sum, std::cref(v), half, v.size());

    int total = f1.get() + f2.get();   // get 会阻塞直到完成
    std::cout << total;
}""",
                        "narration": "async 立刻在后台跑一个任务，返回一个 future。future 的 get 会阻塞，直到结果算好，然后返回它，而且只能取一次。注意 launch async 参数：不加它的话，编译器可以选择延迟执行，那样就变成同步了，测性能会得出错误结论。参数要用 cref 包一下，因为 async 默认会拷贝实参。",
                    },
                    {
                        "kind": "code",
                        "title": "异常也能传回来",
                        "code": """auto f = std::async(std::launch::async, []() -> int {
    throw std::runtime_error("后台出错");
});

try {
    int v = f.get();      // 异常在这里重新抛出
} catch (const std::exception& e) {
    std::cout << "捕获: " << e.what() << '\\n';
}

// 注意：future 析构会阻塞等待任务结束
// 想让它后台自生自灭，得自己接住 future""",
                        "narration": "future 不光传结果，还能把异常传回来，在 get 的时候重新抛出，这一点比裸线程友好得多。但要小心 future 的析构：它会阻塞等待任务完成，所以不要以为把 future 丢掉就等于放养。",
                    },
                    {
                        "kind": "bullets",
                        "title": "通往线程池",
                        "items": [
                            ("问题", "每个任务开一个线程，任务多了线程数量会失控"),
                            ("思路", "固定 N 个常驻线程，从一个任务队列里取活干"),
                            ("组成", "任务队列 + 互斥量 + 条件变量 + 若干 worker"),
                            ("进阶", "C++20 有 std::jthread，收尾更省心；生产环境常用成熟的线程池库"),
                        ],
                        "narration": "async 的底层可能是每次开新线程，任务一多就撑不住。真正生产环境用的是线程池：固定几个常驻线程，从一个任务队列里取活干，队列用我们上一课学的互斥量加条件变量就能实现。C++20 的 jthread 让停止变得更容易，但线程池本身标准库还没有，通常用现成的库。",
                    },
                    {
                        "kind": "recap",
                        "title": "本课回顾",
                        "items": [
                            "async + future 让并发像调函数一样简单",
                            "future.get 只能取一次，且会重新抛出异常",
                            "大量小任务要用线程池，而不是每次开线程",
                        ],
                        "narration": "并发这一章结束。下一章转向工程能力：怎么把一个项目拆成多个文件，怎么用 CMake 组织构建。",
                    },
                ],
            },
        ],
    },
    # ================= 第 10 章 工具链 =================
    {
        "id": "ch10",
        "title": "第 10 章 · 工具链与调试",
        "desc": "多文件工程、CMake、gdb、内存检查、性能剖析——从写代码到做工程。",
        "lessons": [
            {
                "id": "l32",
                "title": "多文件工程与头文件",
                "minutes": 5,
                "tags": ["头文件", "声明", "include guard"],
                "pages": [
                    {
                        "kind": "cover",
                        "title": "把代码拆成多个文件",
                        "subtitle": "头文件 · 声明 · 编译单元",
                        "narration": "真实项目不可能把所有代码塞进一个 cpp。这一课讲清楚头文件和源文件的分工，以及那个经典的重复定义错误是怎么来的。",
                    },
                    {
                        "kind": "code",
                        "title": "声明放头文件，定义放源文件",
                        "code": """// ---------- math_utils.h ----------
#pragma once
#include <string>

int    add(int a, int b);            // 只有声明
double average(const std::vector<int>& v);
extern int counter;                  // 变量的声明

// ---------- math_utils.cpp ----------
#include "math_utils.h"

int counter = 0;                     // 定义只能出现一次

int add(int a, int b) {
    return a + b;
}""",
                        "narration": "头文件放声明，源文件放定义，这是 C++ 的基本分工。pragma once 保证头文件在同一个编译单元里只被展开一次。extern 声明的变量，定义要放在某一个 cpp 里，只能出现一次，这是链接器最常报的重复定义错误的根源。",
                    },
                    {
                        "kind": "code",
                        "title": "头文件里能写什么",
                        "code": """#pragma once

// 可以：类定义（不是实现）
class Point {
public:
    int x() const;          // 声明
private:
    int x_ = 0;
};

// 可以：inline 函数、模板、constexpr
inline int square(int v) { return v * v; }

template <class T>
T twice(T v) { return v + v; }

// 可以：常量表达式
constexpr int kMax = 100;

// 不可以：非 inline 的普通函数定义
// 不可以：非 extern 的变量定义""",
                        "narration": "头文件里可以放类定义、inline 函数、模板、constexpr 常量，因为它们要么被允许重复（inline），要么本身必须在头文件里（模板）。但普通的函数定义和变量定义不能放，那会让每个包含它的 cpp 都产生一份定义，链接时冲突。",
                    },
                    {
                        "kind": "bullets",
                        "title": "三个常见坑",
                        "items": [
                            ("循环包含", "A 包含 B，B 包含 A —— 用前向声明（class B;）打破"),
                            ("头文件里 using namespace", "会污染所有包含它的文件，绝不要写"),
                            ("包含顺序", "自己的头文件放第一行，能暴露缺失的依赖"),
                        ],
                        "narration": "三个坑。循环包含用前向声明解决：只声明类名不包含头文件，把 include 挪到 cpp 里。头文件里千万别写 using namespace，它会把命名空间泄漏给每一个包含者。习惯上把自己模块的头文件放在第一行 include，这样头文件缺依赖会立刻暴露。",
                    },
                    {
                        "kind": "recap",
                        "title": "本课回顾",
                        "items": [
                            "声明进头文件，定义进 cpp，定义只能有一份",
                            "inline / 模板 / constexpr 可以放头文件",
                            "用 #pragma once 和前置声明管理依赖",
                        ],
                        "narration": "下一课讲怎么把这一堆文件交给 CMake 去编译。",
                    },
                ],
            },
            {
                "id": "l33",
                "title": "CMake 入门",
                "minutes": 6,
                "tags": ["CMake", "构建", "target"],
                "pages": [
                    {
                        "kind": "cover",
                        "title": "CMake 入门",
                        "subtitle": "从手敲 g++ 到工程化构建",
                        "narration": "手动敲 g++ 命令，文件一多就不现实了：要写长长的文件列表、依赖关系、编译选项。CMake 是 C++ 事实标准的构建工具，它生成各个平台的构建文件。",
                    },
                    {
                        "kind": "code",
                        "title": "最小的 CMakeLists.txt",
                        "code": """cmake_minimum_required(VERSION 3.20)

project(MyApp VERSION 1.0 LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

add_executable(myapp
    src/main.cpp
    src/math_utils.cpp
)

target_include_directories(myapp PRIVATE include)""",
                        "narration": "这是最小可用的 CMake 文件。第一行声明最低版本，第二行定义项目，然后设置 C++ 标准。add executable 列出一个可执行文件和它所有的源文件。target include directories 给这个目标加头文件搜索路径。注意所有配置都挂在 target 上，这叫做现代 CMake。",
                    },
                    {
                        "kind": "term",
                        "title": "构建流程",
                        "lines": [
                            "$ cmake -S . -B build -G \"MinGW Makefiles\" -DCMAKE_BUILD_TYPE=Debug",
                            "",
                            "$ cmake --build build -j 8",
                            "",
                            "# 运行",
                            "$ ./build/myapp.exe",
                            "",
                            "# 重新配置（改了 CMakeLists 之后）",
                            "$ cmake -S . -B build",
                        ],
                        "narration": "标准三步：配置、构建、运行。减 S 指定源码目录，减 B 指定构建目录，这样编译产物和源码分开，不会弄脏仓库。减 D 传变量，这里设成 Debug 便于调试。构建用 cmake build 加并行数。改了 CMakeLists 要重新配置一次。",
                    },
                    {
                        "kind": "code",
                        "title": "库与依赖",
                        "code": """# 编译成静态库
add_library(math_utils STATIC
    src/math_utils.cpp
)
target_include_directories(math_utils PUBLIC include)

# 可执行文件链接它
add_executable(myapp src/main.cpp)
target_link_libraries(myapp PRIVATE math_utils)

# 找第三方库
find_package(fmt CONFIG REQUIRED)
target_link_libraries(myapp PRIVATE fmt::fmt)

# 让警告成为错误
target_compile_options(myapp PRIVATE -Wall -Wextra -Werror)""",
                        "narration": "把公共代码做成库，其他目标链接它。注意 include 目录用 PUBLIC，这样链接这个库的目标会自动获得头文件路径，这就是传递性依赖。第三方库用 find package 加重命名空间名的 target 链接。建议一开始就把警告全打开，甚至加 Werror 让警告变成错误，这能逼你写干净的代码。",
                    },
                    {
                        "kind": "recap",
                        "title": "本课回顾",
                        "items": [
                            "配置一次，重复构建；构建目录与源码分离",
                            "所有设置挂在 target 上（现代 CMake）",
                            "库用 add_library，依赖用 target_link_libraries",
                        ],
                        "narration": "CMake 能玩得很复杂，但百分之九十的项目只需要这几个命令。下一课讲程序崩了怎么办：调试。",
                    },
                ],
            },
            {
                "id": "l34",
                "title": "调试：gdb 与断点",
                "minutes": 6,
                "tags": ["gdb", "断点", "core dump"],
                "pages": [
                    {
                        "kind": "cover",
                        "title": "调试",
                        "subtitle": "gdb · 断点 · 崩溃现场",
                        "narration": "printf 调试能解决一部分问题，但一旦遇到崩溃、死循环、逻辑错乱，你需要的是一步一步看程序在干什么。这就是调试器。",
                    },
                    {
                        "kind": "code",
                        "title": "关键：带调试信息编译",
                        "code": """# 必须加 -g，否则没有行号、没有变量名
g++ -std=c++20 -g -O0 main.cpp -o main.exe

# 优化过的代码很难调试：变量会被优化掉、行号会跳
# 所以调试构建一般用 -O0，发布才用 -O2

# CMake 里
# cmake -DCMAKE_BUILD_TYPE=Debug

# 启动调试
gdb ./main.exe""",
                        "narration": "调试的前提是编译时带调试信息，也就是减 g 参数。同时要用减 O0 关掉优化，因为优化后变量可能被优化到寄存器里甚至直接消失，单步执行的行号也会跳来跳去。用 CMake 的话，把构建类型设成 Debug 就自动带这些参数。",
                    },
                    {
                        "kind": "term",
                        "title": "gdb 常用命令",
                        "lines": [
                            "(gdb) break main.cpp:42       # 在指定行下断点",
                            "(gdb) run                     # 开始运行",
                            "(gdb) next                    # 单步，不进入函数",
                            "(gdb) step                    # 单步，进入函数",
                            "(gdb) print value             # 打印变量",
                            "(gdb) backtrace               # 看调用栈",
                            "(gdb) frame 2                 # 切到第 2 层栈帧",
                            "(gdb) continue                # 继续到下一个断点",
                            "(gdb) watch counter           # 变量变化时停住",
                        ],
                        "narration": "这一屏是日常用到的命令，值得抄下来。break 下断点，run 启动，next 和 step 是单步的区别（进不进入函数）。程序崩溃时第一件事是 backtrace，看调用栈，找到是哪一行炸的。watch 监视变量，值一变就停，找“这个变量什么时候被改坏的”特别有效。",
                    },
                    {
                        "kind": "code",
                        "title": "程序崩溃时怎么定位",
                        "code": """// Linux 上崩溃会生成 core 文件，直接能看现场
// gdb ./main core

// 更实用的做法：编译时打开 sanitizer
g++ -g -fsanitize=address,undefined main.cpp -o main.exe

// 它会精确报告：
// - 越界访问，以及是哪一行、访问了第几个下标
// - 使用已释放的内存
// - 整数溢出
// - 空指针解引用

// 注意：sanitizer 有性能开销，只在调试构建里开""",
                        "narration": "程序崩溃最难受的是不知道为什么崩。除了 core 文件，最有效的工具是 sanitizer：编译时加减 fsanitize 参数，程序一旦越界访问、用了已释放的内存、整数溢出，它会立刻报出精确到行的信息，而不是等你到另一个地方才发现数据被改坏了。代价是运行变慢，所以只在调试时开。",
                    },
                    {
                        "kind": "recap",
                        "title": "本课回顾",
                        "items": [
                            "-g 加 -O0 才有好的调试体验",
                            "崩溃先 backtrace，改坏变量用 watch",
                            "sanitizer 是查内存问题最快的工具",
                        ],
                        "narration": "下一课专门讲内存错误怎么查，这是 C++ 最高发的线上事故类型。",
                    },
                ],
            },
            {
                "id": "l35",
                "title": "内存错误与 sanitizer",
                "minutes": 5,
                "tags": ["ASan", "UBSan", "内存"],
                "pages": [
                    {
                        "kind": "cover",
                        "title": "内存错误",
                        "subtitle": "越界 · 悬空 · 泄漏",
                        "narration": "C++ 最常见的线上事故几乎都是内存问题。它们的共同特点是：出问题的地方，和真正出错的地方，往往离得很远。",
                    },
                    {
                        "kind": "bullets",
                        "title": "四类内存错误",
                        "items": [
                            ("越界访问", "读写数组范围外，可能悄悄改坏相邻变量"),
                            ("悬空引用", "对象已销毁，指针/引用还在用"),
                            ("重复释放", "同一块内存 delete 两次"),
                            ("内存泄漏", "new 了没 delete，长跑后内存涨满"),
                        ],
                        "narration": "四类问题。越界最常见，也最阴险：它常常不报错，只是把旁边的数据改掉。悬空引用是对象已经销毁还在用，读到的可能是完全无关的新数据。重复释放会直接崩溃。内存泄漏不一定立刻出问题，但服务跑久了必然 OOM。",
                    },
                    {
                        "kind": "code",
                        "title": "AddressSanitizer 一网打尽",
                        "code": """g++ -g -fsanitize=address main.cpp -o main.exe

// 越界
int* a = new int[5];
a[7] = 1;          // ASan 立刻报 heap-buffer-overflow

// 释放后使用
delete[] a;
a[0] = 2;          // heap-use-after-free

// 栈上越界
int buf[4];
buf[4] = 0;        // stack-buffer-overflow

// 泄漏
new int(1);        // LeakSanitizer 在退出时报告""",
                        "narration": "AddressSanitizer 用编译器插桩加影子内存，能立刻发现越界、释放后使用、重复释放。UndefinedBehaviorSanitizer 管整数溢出、空指针、对齐这些未定义行为。两个可以一起开。它的报告会给出完整的分配栈和使用栈，一眼就能看出哪里写错了。",
                    },
                    {
                        "kind": "code",
                        "title": "从根本上减少内存错误",
                        "code": """// 1. 用容器，不用裸数组
std::vector<int> v(5);
v.at(7);                  // 抛异常，而不是越界写

// 2. 用智能指针，不用裸 new
auto p = std::make_unique<int[]>(5);

// 3. 用 string / string_view，不用 char[]
std::string s = "hello";

// 4. 返回值、参数用引用和值，减少裸指针
double avg(const std::vector<int>& v);

// 5. 在 CI 里跑 sanitizer 构建
//    把内存错误挡在合并之前""",
                        "narration": "工具能帮你抓，但更好的策略是让错误写不出来。用 vector 代替裸数组，用 at 而不是方括号；用智能指针代替裸 new；用 string 代替字符数组；参数尽量用引用和值。最后一条很关键：把 sanitizer 构建放进持续集成，每次提交都跑，这样内存错误在合并之前就被拦下了。",
                    },
                    {
                        "kind": "recap",
                        "title": "本课回顾",
                        "items": [
                            "越界、悬空、重复释放、泄漏是四大类",
                            "-fsanitize=address,undefined 是首选工具",
                            "用容器和智能指针，让错误写不出来",
                        ],
                        "narration": "下一课讲性能：什么时候该优化，以及怎么找到真正的瓶颈。",
                    },
                ],
            },
            {
                "id": "l36",
                "title": "性能：先测量，再优化",
                "minutes": 5,
                "tags": ["性能", "profiling", "优化级别"],
                "pages": [
                    {
                        "kind": "cover",
                        "title": "性能优化",
                        "subtitle": "先测量，再优化",
                        "narration": "关于性能，最重要的一句话是：不要猜。程序百分之八十的时间通常花在百分之二十的代码上，而你猜的那部分大概率不是瓶颈。",
                    },
                    {
                        "kind": "code",
                        "title": "先测量",
                        "code": """#include <chrono>

auto t0 = std::chrono::steady_clock::now();

// 被测代码
work();

auto t1 = std::chrono::steady_clock::now();
auto ms = std::chrono::duration_cast<
            std::chrono::milliseconds>(t1 - t0).count();

std::cout << ms << " ms\\n";

// 注意：用 steady_clock，不要用 system_clock
// system_clock 会被系统时间调整影响""",
                        "narration": "最朴素也最有效的测量手段就是计时。用 steady clock，它是单调的，不会被系统时间同步干扰。但计时只告诉你哪一段慢，不告诉你为什么慢，这时候需要 profiler。",
                    },
                    {
                        "kind": "term",
                        "title": "常见性能手段",
                        "lines": [
                            "# 1. 找瓶颈：profiler",
                            "$ gprof ./main gmon.out",
                            "$ perf record ./main && perf report",
                            "",
                            "# 2. 看编译器优化等级",
                            "-O2  常用发布级",
                            "-O3  更激进，可能增大体积",
                            "",
                            "# 3. 让编译器告诉你为什么没优化",
                            "$ g++ -O2 -fopt-info-vec-optimized main.cpp",
                        ],
                        "narration": "性能工程的标准流程：先用 profiler 找到热点函数，再看那个函数的汇编和优化报告。gcc 有 opt info 参数，会告诉你哪些循环被向量化了、哪些没被向量化以及原因。不要一上来就手写 SIMD，先用好编译器的自动向量化。",
                    },
                    {
                        "kind": "bullets",
                        "title": "高性价比的优化顺序",
                        "items": [
                            ("算法与数据结构", "O(n²) 换成 O(n log n)，比任何微优化都值"),
                            ("减少拷贝", "用 const 引用、移动语义、reserve 预分配"),
                            ("内存布局", "连续内存比链表快得多，缓存友好"),
                            ("再谈微优化", "分支预测、内联、SIMD，最后才考虑"),
                        ],
                        "narration": "优化要按性价比排序。第一是算法和数据结构，量级差异是几十上百倍。第二是减少不必要的拷贝，用 const 引用传参、用移动语义、vector 预分配。第三是内存布局，同样逻辑用 vector 往往比 list 快好几倍，因为缓存命中率高。最后才是分支、内联、SIMD 这些微优化。",
                    },
                    {
                        "kind": "recap",
                        "title": "本课回顾",
                        "items": [
                            "先测量再优化，不要凭直觉",
                            "算法 > 拷贝 > 布局 > 微优化",
                            "相信编译器，先看好优化等级和优化报告",
                        ],
                        "narration": "工具链这一章结束。下一章进入模板，C++ 泛型编程的核心。",
                    },
                ],
            },
        ],
    },
    # ================= 第 11 章 模板 =================
    {
        "id": "ch11",
        "title": "第 11 章 · 模板与泛型",
        "desc": "函数模板、类模板、特化——写一份代码，适配所有类型。",
        "lessons": [
            {
                "id": "l37",
                "title": "函数模板与类型推导",
                "minutes": 5,
                "tags": ["template", "推导", "泛型"],
                "pages": [
                    {
                        "kind": "cover",
                        "title": "函数模板",
                        "subtitle": "一份代码，多种类型",
                        "narration": "如果同一个逻辑要适配 int、double、string，你要写三个几乎一样的函数吗？模板让你只写一份，编译器替你生成各个版本。",
                    },
                    {
                        "kind": "code",
                        "title": "基本形态",
                        "code": """template <typename T>
T maximum(T a, T b) {
    return a > b ? a : b;
}

maximum(3, 5);           // T 推导为 int
maximum(2.5, 1.5);       // T 推导为 double
maximum(std::string("a"), std::string("b"));

// 显式指定类型
maximum<double>(3, 5);   // 3 和 5 转成 double

// 多参数
template <typename A, typename B>
auto add(A a, B b) { return a + b; }""",
                        "narration": "模板用 template 关键字开头，尖括号里声明类型参数。调用时编译器从实参推导出 T 的具体类型，然后生成对应的函数，这叫实例化。注意模板的推导要求严格匹配：一个 int 一个 double，两个参数类型不一致就推导失败，这时候要么显式指定，要么用两个类型参数。",
                    },
                    {
                        "kind": "bullets",
                        "title": "模板的三个特性",
                        "items": [
                            ("编译期展开", "每个用到的类型都生成一份机器码，不是运行时多态"),
                            ("零开销", "和手写针对具体类型的函数性能完全一样"),
                            ("定义要在头文件", "因为实例化发生在调用点，编译器需要看到完整定义"),
                        ],
                        "narration": "模板是编译期展开的：你用了 int 和 double 两种类型，编译器就生成两份代码。所以它没有运行时开销，性能和你手写两份函数完全一致。代价是编译变慢、二进制变大。还有一个实践要点：模板的定义必须放在头文件里，因为编译器在调用点需要看到完整定义才能实例化。",
                    },
                    {
                        "kind": "code",
                        "title": "约束：模板报错为什么那么长",
                        "code": """// C++20 之前：错误信息在模板内部爆炸
template <typename T>
T twice(T v) { return v + v; }      // 要求 T 支持 +

twice(std::vector<int>{1,2});       // 编译错误，报错几百行

// C++20：用 concept 约束，报错清晰
#include <concepts>

template <std::integral T>
T twice(T v) { return v + v; }

// 现在传 vector 会直接说：约束不满足""",
                        "narration": "模板最让人头疼的是报错。一个类型不满足要求，编译器会在模板内部层层展开，最后吐给你几百行没人看得懂的信息。C++20 的 concept 就是来解决这个问题的：把类型要求写在签名里，不满足时直接告诉你哪个约束没过。这个概念我们下一章详细讲。",
                    },
                    {
                        "kind": "recap",
                        "title": "本课回顾",
                        "items": [
                            "template <typename T> 声明类型参数",
                            "推导严格，类型不一致要显式指定",
                            "模板定义放头文件，编译期展开、零运行时开销",
                        ],
                        "narration": "下一课把模板用在类上，做出能装任意类型的容器。",
                    },
                ],
            },
            {
                "id": "l38",
                "title": "类模板",
                "minutes": 5,
                "tags": ["类模板", "成员模板", "推导指引"],
                "pages": [
                    {
                        "kind": "cover",
                        "title": "类模板",
                        "subtitle": "写一个能装任意类型的容器",
                        "narration": "标准库的 vector、map、optional 全是类模板。这一课我们自己写一个，理解它们是怎么被造出来的。",
                    },
                    {
                        "kind": "code",
                        "title": "一个简单的栈",
                        "code": """template <typename T>
class Stack {
public:
    void push(const T& v) { data_.push_back(v); }

    void pop() {
        if (empty()) throw std::out_of_range("栈为空");
        data_.pop_back();
    }

    T& top() {
        if (empty()) throw std::out_of_range("栈为空");
        return data_.back();
    }

    bool empty() const { return data_.empty(); }
    size_t size() const { return data_.size(); }

private:
    std::vector<T> data_;
};

Stack<int> s;
s.push(1);""",
                        "narration": "类模板就是把 template 写在类前面，类里的成员函数可以自由使用类型参数 T。使用时必须显式写出类型：Stack 尖括号 int。这就是为什么 vector 要写 vector int，而函数模板可以自动推导。顺便注意边界检查：空栈弹栈抛异常，比直接崩溃好。",
                    },
                    {
                        "kind": "code",
                        "title": "成员函数的定义写在类外",
                        "code": """template <typename T>
class Stack {
public:
    void push(const T& v);
    T& top();
private:
    std::vector<T> data_;
};

// 类外定义要重复写 template 和类名限定
template <typename T>
void Stack<T>::push(const T& v) {
    data_.push_back(v);
}

template <typename T>
T& Stack<T>::top() {
    return data_.back();
}

// C++17 类模板参数推导
std::pair p{1, 2.0};              // 自动推导为 pair<int,double>
Stack s2{std::string("a")};       // 需要推导指引才work""",
                        "narration": "类外定义成员函数时，要再写一遍 template 声明，并用类名加尖括号和双冒号限定，这个语法很丑但必须记住。C++17 引入了类模板参数推导，像 pair 这种能从构造函数实参推断的类型可以直接省略尖括号。如果你自己的类也想支持推导，需要写推导指引。",
                    },
                    {
                        "kind": "bullets",
                        "title": "实践要点",
                        "items": [
                            ("模板类通常全写在头文件", "实现放 cpp 会链接失败（看不到定义无法实例化）"),
                            ("能不用模板就不用", "模板让代码变抽象、编译变慢、报错变长"),
                            ("优先用标准库的", "vector / optional / variant 已经覆盖大多数需求"),
                            ("显式实例化", "想在 cpp 里放实现，可以用显式实例化，但只适合类型集合固定的场景"),
                        ],
                        "narration": "四个要点。第一，类模板的实现一般全写在头文件，否则链接时找不到定义。第二，别为了炫技用模板，它会让代码抽象、编译慢、报错长。第三，标准库的容器和工具已经覆盖绝大多数需求。第四，如果确实想把实现放到 cpp 里，可以用显式实例化声明你支持的有限类型集合。",
                    },
                    {
                        "kind": "recap",
                        "title": "本课回顾",
                        "items": [
                            "类模板让容器适配任意类型",
                            "类外定义成员要重复 template 声明",
                            "实现放头文件，否则链接失败",
                        ],
                        "narration": "下一课讲模板特化：当某个类型需要特殊处理时怎么办。",
                    },
                ],
            },
            {
                "id": "l39",
                "title": "模板特化与编译期分支",
                "minutes": 5,
                "tags": ["特化", "if constexpr", "type_traits"],
                "pages": [
                    {
                        "kind": "cover",
                        "title": "特化与编译期分支",
                        "subtitle": "为特定类型说不同的话",
                        "narration": "通用模板能处理大多数类型，但总有例外。比如把对象转成字符串，指针就要特殊处理。模板特化就是为这些例外开的口子。",
                    },
                    {
                        "kind": "code",
                        "title": "全特化与偏特化",
                        "code": """template <typename T>
struct Printer {
    static void print(const T& v) { std::cout << v; }
};

// 全特化：针对 bool
template <>
struct Printer<bool> {
    static void print(bool v) { std::cout << (v ? "true" : "false"); }
};

// 偏特化：针对所有指针类型
template <typename T>
struct Printer<T*> {
    static void print(T* p) {
        std::cout << (p ? "non-null" : "null");
    }
};""",
                        "narration": "全特化是完全指定所有模板参数，偏特化是只指定一部分。注意函数模板只能全特化不能偏特化，所以常用类模板加静态函数代替。这个模式在标准库里到处都是，比如 hash、numeric limits 都是这样做的。",
                    },
                    {
                        "kind": "code",
                        "title": "C++17 if constexpr：更简单的分支",
                        "code": """template <typename T>
void show(const T& v) {
    if constexpr (std::is_pointer_v<T>) {
        std::cout << "指针 " << v;
    } else if constexpr (std::is_integral_v<T>) {
        std::cout << "整数 " << v;
    } else {
        std::cout << v;
    }
}

// 关键区别：
// if constexpr 在编译期就选定分支，没被选中的分支
// 不会被实例化 —— 所以可以写只在某些类型下合法的代码

// 普通 if 不行：
// 两个分支都会被编译，哪怕不会执行""",
                        "narration": "对比特化，if constexpr 好用太多。它在编译期就决定走哪个分支，没被选中的分支根本不会实例化，所以你在分支里可以写只在特定类型下才合法的代码，比如对指针类型解引用、对数值类型做算术。普通 if 做不到这一点，因为它要求所有分支都能编译通过。",
                    },
                    {
                        "kind": "bullets",
                        "title": "type_traits 常用工具",
                        "items": [
                            ("is_pointer / is_integral", "判断类型类别，返回编译期布尔值"),
                            ("is_same", "判断两个类型是否完全相同"),
                            ("remove_reference / decay", "去掉引用、做数组到指针的退化"),
                            ("enable_if_t", "C++17 之前的约束手段，C++20 基本被 concepts 取代"),
                        ],
                        "narration": "type traits 是一组编译期问询工具：这个类型是不是指针、是不是整数、两个类型是不是一样、去掉引用后是什么。它们是 if constexpr 和 concepts 的底层基础。enable if 是老式的约束手段，语法非常难读，C++20 之后应该改用 concepts。",
                    },
                    {
                        "kind": "recap",
                        "title": "本课回顾",
                        "items": [
                            "全特化指定全部参数，偏特化指定部分",
                            "if constexpr 让分支在编译期消失",
                            "type_traits 提供编译期类型问询",
                        ],
                        "narration": "模板这一章结束。下一章看 C++20，现代 C++ 最重要的一次更新。",
                    },
                ],
            },
        ],
    },
    # ================= 第 12 章 C++20 =================
    {
        "id": "ch12",
        "title": "第 12 章 · C++20 新特性",
        "desc": "concepts、ranges、span、三路比较——让 C++ 写起来像现代语言。",
        "lessons": [
            {
                "id": "l40",
                "title": "concepts：让模板报错能看懂",
                "minutes": 5,
                "tags": ["concept", "requires", "约束"],
                "pages": [
                    {
                        "kind": "cover",
                        "title": "concepts",
                        "subtitle": "给模板参数加约束",
                        "narration": "这是 C++20 对日常编码改善最大的特性。模板报错难懂的问题，被 concept 基本解决了。",
                    },
                    {
                        "kind": "code",
                        "title": "定义与使用",
                        "code": """#include <concepts>

// 定义约束：类型必须支持 + 且结果可比较
template <typename T>
concept Addable = requires(T a, T b) {
    { a + b } -> std::convertible_to<T>;
};

template <Addable T>
T add(T a, T b) { return a + b; }

// 标准库现成的
template <std::integral T>
T gcd2(T a, T b) { return b == 0 ? a : gcd2(b, a % b); }

template <std::floating_point T>
T safe_div(T a, T b) { return b == 0 ? T{} : a / b; }""",
                        "narration": "concept 就是一个编译期谓词：给一个类型，回答它满不满足要求。requires 表达式可以检查“这个类型上 a 加 b 合不合法、结果类型能不能转成 T”。用的时候把 concept 写在 template 尖括号里，当成类型约束。标准库已经提供了大量现成的：integral、floating point、copyable 等等。",
                    },
                    {
                        "kind": "code",
                        "title": "两种写法与简写",
                        "code": """// 写法一：template <Concept T>
template <std::integral T>
void f1(T v);

// 写法二：requires 子句，可组合多个条件
template <typename T>
    requires std::integral<T> && std::copyable<T>
void f2(T v);

// 简写：直接用 concept 当参数类型（最清爽）
void f3(std::integral auto v);

// 组合自定义约束
template <typename T>
concept Numeric = std::integral<T> || std::floating_point<T>;

template <Numeric T>
T clamp01(T v) { return v < 0 ? 0 : (v > 1 ? 1 : v); }""",
                        "narration": "三种写法：写在 template 里、用 requires 子句（适合组合多个条件）、直接用 concept 当参数类型（最简洁）。我推荐日常用简写形式，它就是普通的 auto 加一个约束，可读性最好。定义自己的 concept 时可以用逻辑运算符组合标准 concept。",
                    },
                    {
                        "kind": "bullets",
                        "title": "为什么要用它",
                        "items": [
                            ("报错从几百行变成一行", "“约束不满足”直接指向调用点"),
                            ("重载解析更精确", "约束越强的重载优先级越高"),
                            ("文档作用", "函数签名自己说明了要求，比注释可靠"),
                            ("注意", "它只是编译期检查，不产生任何运行时开销"),
                        ],
                        "narration": "四个价值。第一，报错从几百行变成一行，直接告诉你是哪个约束没过。第二，重载解析会优先选约束更强的版本，这让泛型代码的组合变得可控。第三，它本身就是最好的文档：看一眼签名就知道要求什么。第四，零运行时开销，全是编译期的事。",
                    },
                    {
                        "kind": "recap",
                        "title": "本课回顾",
                        "items": [
                            "concept = 编译期类型谓词",
                            "requires 表达式描述类型要满足的操作",
                            "优先用 `std::integral auto` 这种简写",
                        ],
                        "narration": "下一课讲 ranges，C++20 另一个改变写法的大特性。",
                    },
                ],
            },
            {
                "id": "l41",
                "title": "ranges：像流水线一样处理序列",
                "minutes": 5,
                "tags": ["ranges", "views", "管道"],
                "pages": [
                    {
                        "kind": "cover",
                        "title": "ranges",
                        "subtitle": "声明式的序列处理",
                        "narration": "以前我们要筛一遍、再变换一遍、再取前几个，得写三段循环或者嵌套一堆算法调用。ranges 让你用竖线把操作串起来。",
                    },
                    {
                        "kind": "code",
                        "title": "管道写法",
                        "code": """#include <ranges>
#include <vector>
#include <iostream>

std::vector<int> v{1,2,3,4,5,6,7,8,9,10};

// 取偶数 → 平方 → 前 3 个
auto result = v
    | std::views::filter([](int n){ return n % 2 == 0; })
    | std::views::transform([](int n){ return n * n; })
    | std::views::take(3);

for (int x : result) std::cout << x << ' ';
// 4 16 36""",
                        "narration": "这就是 ranges 的魅力：竖线从左往右读，filter 筛，transform 变换，take 取前几个，意图一目了然。重要的是它完全惰性：不会创建中间 vector，数据是一个元素一个元素流过去的，内存开销极小。",
                    },
                    {
                        "kind": "code",
                        "title": "常用 views",
                        "code": """std::views::filter(pred)      // 筛选
std::views::transform(f)      // 变换
std::views::take(n)           // 前 n 个
std::views::drop(n)           // 跳过前 n 个
std::views::reverse           // 反转
std::views::iota(1, 10)       // 生成 1..9
std::views::split(delim)      // 按分隔符切分

// 组合
for (auto i : std::views::iota(1, 100)
            | std::views::filter([](int n){ return n % 7 == 0; })
            | std::views::take(5))
    std::cout << i << ' ';""",
                        "narration": "这张表是日常最常用的几个 views。iota 特别实用，它能凭空生成一个整数序列，不用先造一个 vector。split 可以按分隔符切分字符串，省掉一堆手动找位置和截取的代码。这些都能自由组合，像搭积木一样。",
                    },
                    {
                        "kind": "bullets",
                        "title": "要注意的地方",
                        "items": [
                            ("view 不拥有数据", "它只是原序列的视图，原数据销毁它就悬空"),
                            ("惰性求值", "不遍历就不计算，调试时看不到中间结果"),
                            ("性能", "简单场景手写循环可能更快，但差距通常不大"),
                            ("调试", "可以转成 vector 再打印，方便观察"),
                        ],
                        "narration": "几个坑。第一，view 不拥有数据，它只是视图，如果原容器销毁了，view 就悬空了。第二，惰性是双刃剑：不遍历就不会计算，所以你在调试器里看不到中间结果。第三，对于极其简单的场景，手写循环可能还快一点，但通常差距不到一倍，可读性的收益更大。第四，想看中间结果就转成 vector 再打印。",
                    },
                    {
                        "kind": "recap",
                        "title": "本课回顾",
                        "items": [
                            "ranges 用管道组合操作，可读性大幅提升",
                            "views 是惰性的、零拷贝的视图",
                            "view 不拥有数据，注意生命周期",
                        ],
                        "narration": "下一课讲 span 和 string view，它们是 ranges 世界里的“非拥有引用”。",
                    },
                ],
            },
            {
                "id": "l42",
                "title": "span 与 string_view：非拥有视图",
                "minutes": 4,
                "tags": ["span", "string_view", "零拷贝"],
                "pages": [
                    {
                        "kind": "cover",
                        "title": "非拥有视图",
                        "subtitle": "span · string_view",
                        "narration": "函数接受一段数据，但不想拷贝，也不想只能接受 vector。span 和 string view 就是这个问题的答案。",
                    },
                    {
                        "kind": "code",
                        "title": "std::span",
                        "code": """#include <span>

// 接受任意连续容器：数组、vector、C 数组都行
double sum(std::span<const double> data) {
    double s = 0;
    for (double v : data) s += v;
    return s;
}

double arr[] = {1, 2, 3};
std::vector<double> v{4, 5};
sum(arr);                       // C 数组
sum(v);                         // vector
sum(std::span(v).subspan(0, 1));  // 子视图

// 关键：零拷贝，它只存指针和长度""",
                        "narration": "span 就是一个指针加长度，零拷贝。它的价值在于统一接口：同一个函数既能接受 C 数组，也能接受 vector，还能接受子范围。以前这种函数要么只能收指针加长度两个参数，要么就得为每种容器写重载。现在一个 span 搞定。",
                    },
                    {
                        "kind": "code",
                        "title": "std::string_view",
                        "code": """#include <string_view>

// 以前：传 const std::string& 会为字面量构造临时 string
size_t count_vowels(const std::string& s);

// 现在：零拷贝，接受字面量和 string
size_t count_vowels(std::string_view s);

count_vowels("hello");          // 不构造 string
count_vowels(std::string("hi"));

// 陷阱：string_view 不拥有内存
std::string_view bad() {
    std::string local = "temp";
    return local;               // 返回后 local 已销毁！
}""",
                        "narration": "string view 解决的是只读字符串参数的问题：传字面量不再构造临时 string，零拷贝。但它的生命线在于被引用的字符串必须活得足够久。返回局部字符串的 view 是典型的悬空，这个错误很难被发现，因为读出来的通常是看起来正常的垃圾数据。",
                    },
                    {
                        "kind": "bullets",
                        "title": "使用原则",
                        "items": [
                            ("参数用它", "只读参数优先 string_view / span"),
                            ("成员不要用它", "除非你能保证生命周期"),
                            ("返回值慎用", "除非返回的是调用方提供的对象"),
                            ("需要持有就用 string", "所有权清晰比省一次拷贝重要"),
                        ],
                        "narration": "使用原则很清晰：作为函数参数用它，因为生命周期覆盖了函数调用；作为成员变量或返回值要非常谨慎，除非你能保证被引用的对象活得更久；如果真的需要持有，就老老实实用 string，所有权清晰比省一次拷贝重要得多。",
                    },
                    {
                        "kind": "recap",
                        "title": "本课回顾",
                        "items": [
                            "span / string_view 是零拷贝的非拥有视图",
                            "适合做只读参数，统一多种容器接口",
                            "拿去持有或返回，先想清楚生命周期",
                        ],
                        "narration": "下一课讲 C++20 里几个让代码变短的小特性。",
                    },
                ],
            },
            {
                "id": "l43",
                "title": "三路比较与其他 C++20 便利",
                "minutes": 5,
                "tags": ["<=>", "指定初始化", "constexpr"],
                "pages": [
                    {
                        "kind": "cover",
                        "title": "C++20 的便利",
                        "subtitle": "<=> · 指定初始化 · constexpr",
                        "narration": "这一课四个小特性，每一个都能让你少写不少样板代码。",
                    },
                    {
                        "kind": "code",
                        "title": "三路比较：六个运算符一次写完",
                        "code": """struct Version {
    int major, minor, patch;

    // 一行生成 == != < <= > >=
    auto operator<=>(const Version&) const = default;
};

Version a{1, 2, 0}, b{1, 10, 0};
std::cout << (a < b) << (a == b) << (a >= b);

// 也可以手写返回自定义语义
auto cmp = value <=> 0;   // 与 0 比较的结果
if (cmp < 0) { /* 负 */ }
else if (cmp == 0) { /* 零 */ }""",
                        "narration": "以前写一个可比较的类，要手写六个运算符，最多写错其中一个。C++20 的默认三路比较一行就生成全部六个。注意它是按成员的声明顺序依次比较，所以成员的顺序就是你想要的字典序。手写的时候返回的是一个比较类别对象，可以直接和零比较。",
                    },
                    {
                        "kind": "code",
                        "title": "指定初始化与 constexpr",
                        "code": """// 指定初始化器：字段名写在前面，顺序必须一致
struct Config {
    std::string host;
    int port;
    bool tls;
};

Config c{.host = "localhost", .port = 8080, .tls = true};

// constexpr 增强：更多东西能编译期算
constexpr auto square(int x) { return x * x; }

consteval int cube(int x) { return x * x * x; }   // 必须编译期

// 编译期容器（vector/string 也能在 constexpr 里用了）
constexpr int sum_first_n(int n) {
    int s = 0;
    for (int i = 1; i <= n; ++i) s += i;
    return s;
}
static_assert(sum_first_n(10) == 55);""",
                        "narration": "指定初始化让你在构造时把字段名写出来，可读性大幅提升，尤其是字段很多的结构体。注意顺序必须和声明一致。constexpr 在 C++20 里大幅增强，循环、虚函数、甚至 vector 和 string 都能在编译期用了，所以很多计算可以直接挪到编译期，运行时零成本。consteval 更严格，强制必须编译期求值。",
                    },
                    {
                        "kind": "bullets",
                        "title": "其他值得知道的",
                        "items": [
                            ("std::format", "类似 Python 的格式化，比 printf 安全、比流舒服"),
                            ("模板 lambda", "[]<typename T>(T v){} 可以直接用类型参数"),
                            ("std::bit_cast", "安全的类型双关，替代 memcpy 的写法"),
                            ("模块 modules", "理论上能替代头文件，但目前编译器支持还不齐"),
                        ],
                        "narration": "另外几个值得知道的。format 是终于到来的现代格式化，语法和 Python 的 f-string 很像，类型安全。模板 lambda 让你在 lambda 里直接声明类型参数。bit cast 是安全的位级重解释，替代过去用 memcpy 的写法。模块理论上是头文件的替代品，但编译器支持还不完整，短期内可以不用。",
                    },
                    {
                        "kind": "recap",
                        "title": "本课回顾",
                        "items": [
                            "<=> 默认实现一次生成六个比较运算符",
                            "指定初始化让结构体构造可读",
                            "constexpr 大幅增强，编译期能做的事更多",
                        ],
                        "narration": "C++20 这一章结束。最后一章讲工程实践，以及那个把前面所有东西串起来的项目。",
                    },
                ],
            },
        ],
    },
    # ================= 第 13 章 工程实践 =================
    {
        "id": "ch13",
        "title": "第 13 章 · 工程实践",
        "desc": "错误处理、RAII 进阶、接口设计与测试——让代码能被别人接手。",
        "lessons": [
            {
                "id": "l44",
                "title": "错误处理：异常、错误码与 optional",
                "minutes": 5,
                "tags": ["异常", "optional", "错误处理"],
                "pages": [
                    {
                        "kind": "cover",
                        "title": "错误处理",
                        "subtitle": "异常 · 错误码 · optional",
                        "narration": "错误处理是区分玩具代码和工程代码的分水岭。C++ 提供了好几种手段，用错地方会让代码变成灾难。",
                    },
                    {
                        "kind": "code",
                        "title": "三种手段各自的场合",
                        "code": """// 1. 异常：真正的“异常”，调用方无法本地处理
//    如：文件损坏、网络断开、内存不足
throw std::runtime_error("无法打开配置文件");

// 2. 错误码：可预期的失败，调用方必须处理
std::error_code ec;
auto file = open("a.txt", ec);
if (ec) { /* 处理 */ }

// 3. optional：可能没有值，但不算错误
std::optional<int> findIndex(const std::string& s, char c) {
    auto p = s.find(c);
    if (p == std::string::npos) return std::nullopt;
    return static_cast<int>(p);
}

if (auto i = findIndex("abc", 'b')) std::cout << *i;""",
                        "narration": "三种手段的分工。异常用于真正意外的、调用方无法在原地处理的错误。错误码用于可预期的失败，比如文件不存在，调用方必须显式检查。optional 用于“可能有也可能没有”的情况，比如查找，找不到不算错误，只是一种正常的结果。判断标准很简单：调用方能不能在这里处理？能就用返回值，不能才抛异常。",
                    },
                    {
                        "kind": "bullets",
                        "title": "异常使用的三条纪律",
                        "items": [
                            ("不要用异常做流程控制", "性能差，而且让代码难以推理"),
                            ("异常类型要有意义", "自定义异常类，而不是 throw 一个字符串"),
                            ("析构函数里不要抛", "栈展开过程中再抛会直接 terminate"),
                        ],
                        "narration": "三条纪律。第一，不要用异常做正常的流程控制，异常抛出很昂贵，而且让人读不懂逻辑。第二，抛有意义的异常类型，不要扔字符串或整数，这样调用方能精确捕获。第三，析构函数绝对不要抛异常：栈展开过程中又抛一个，程序直接终止。",
                    },
                    {
                        "kind": "code",
                        "title": "一种务实的折中：Result 类型",
                        "code": """// C++23 有 std::expected，在那之前可以自己写一个简版
template <typename T, typename E>
class Result {
public:
    Result(T v) : value_(v) {}
    Result(E e) : err_(e) {}

    bool ok() const { return value_.has_value(); }
    T& value() { return *value_; }
    const E& error() const { return *err_; }

private:
    std::optional<T> value_;
    std::optional<E> err_;
};

// 用法：错误显式化，不靠异常也不靠全局 errno
auto r = parseConfig("a.txt");
if (!r.ok()) {
    log(r.error());
    return;
}
use(r.value());""",
                        "narration": "很多团队（特别是游戏引擎和高频交易）禁用异常，改用 Result 类型：把成功值和错误放在一个返回类型里，强制调用方检查。Rust 的 Result、C++23 的 expected 都是这个思路。它的好处是错误路径在类型系统里可见，坏处是代码会多一层解包。选哪种取决于团队约定，但要统一，不要一半异常一半错误码。",
                    },
                    {
                        "kind": "recap",
                        "title": "本课回顾",
                        "items": [
                            "异常用于意外，错误码/optional 用于可预期失败",
                            "自定义异常类型，别抛字符串",
                            "团队内要统一错误处理风格",
                        ],
                        "narration": "下一课回到 RAII，看它在更复杂的场景（作用域守卫、事务）里怎么用。",
                    },
                ],
            },
            {
                "id": "l45",
                "title": "RAII 进阶：作用域守卫",
                "minutes": 4,
                "tags": ["RAII", "scope_guard", "资源"],
                "pages": [
                    {
                        "kind": "cover",
                        "title": "RAII 进阶",
                        "subtitle": "作用域守卫与事务语义",
                        "narration": "RAII 不只是管内存。任何“进入时要建立、离开时必须撤销”的状态，都可以用对象生命周期来保证。",
                    },
                    {
                        "kind": "code",
                        "title": "一个通用作用域守卫",
                        "code": """class ScopeGuard {
public:
    explicit ScopeGuard(std::function<void()> f) : f_(std::move(f)) {}
    ~ScopeGuard() { if (active_ && f_) f_(); }

    void dismiss() { active_ = false; }   // 取消

    ScopeGuard(const ScopeGuard&) = delete;
    ScopeGuard& operator=(const ScopeGuard&) = delete;

private:
    std::function<void()> f_;
    bool active_ = true;
};

// 用
void work() {
    auto guard = ScopeGuard([]{ cleanup(); });
    if (ok()) guard.dismiss();   // 成功就别清理
}""",
                        "narration": "这个模式叫作用域守卫：构造时登记一个要在退出时执行的动作，析构时执行，除非你显式 dismiss。它把“一定会执行”变成语言保证。注意拷贝构造和赋值要删掉，否则对象被复制时清理动作会执行两次。",
                    },
                    {
                        "kind": "bullets",
                        "title": "RAII 能表达的东西",
                        "items": [
                            ("锁", "lock_guard / unique_lock"),
                            ("文件与句柄", "ifstream、自定义 File"),
                            ("临时状态", "进入函数时改全局状态，退出时改回来"),
                            ("事务", "成功提交，异常回滚"),
                            ("计时", "进入时记开始，退出时打日志"),
                        ],
                        "narration": "RAII 能表达的范围比你想的宽：锁、文件和句柄是最常见的；临时状态切换也可以（进入函数改配置，退出改回来）；事务语义（成功提交、异常回滚）是它的经典应用；甚至计时器都能这么写。判断标准就是：这个动作是不是“一定要在离开作用域时执行”？是的话就封装成对象。",
                    },
                    {
                        "kind": "code",
                        "title": "写 RAII 类的检查清单",
                        "code": """class Resource {
public:
    explicit Resource(const std::string& name);   // 获取
    ~Resource();                                  // 释放

    // 拷贝：删除（独占）或者实现深拷贝
    Resource(const Resource&) = delete;
    Resource& operator=(const Resource&) = delete;

    // 移动：移交所有权
    Resource(Resource&& other) noexcept;
    Resource& operator=(Resource&& other) noexcept;

private:
    Handle h_ = kInvalid;   // 必须在成员声明处给初始值
};""",
                        "narration": "写 RAII 类的检查清单：构造函数获取资源，析构函数释放；成员变量一定要在声明处给初始值，防止构造失败时析构函数碰到垃圾值；拷贝要么深拷贝要么删掉；移动要标 noexcept 并移交所有权。这就是三法则、五法则的实际应用。",
                    },
                    {
                        "kind": "recap",
                        "title": "本课回顾",
                        "items": [
                            "任何“退出时必须撤销”的动作都能做成 RAII",
                            "作用域守卫可以替代大量重复的清理代码",
                            "RAII 类要正确处理拷贝与移动",
                        ],
                        "narration": "下一课讲接口设计：怎么写出别人愿意用的 API。",
                    },
                ],
            },
            {
                "id": "l46",
                "title": "接口设计与测试",
                "minutes": 5,
                "tags": ["接口", "const", "单元测试"],
                "pages": [
                    {
                        "kind": "cover",
                        "title": "接口设计与测试",
                        "subtitle": "让别人愿意用，让 bug 早暴露",
                        "narration": "写了十年的代码和写了两年的代码，差别往往不在语法，而在接口设计。好的接口让人用不错，坏的接口让人天天踩坑。",
                    },
                    {
                        "kind": "code",
                        "title": "接口设计清单",
                        "code": """class Account {
public:
    // 1. const 正确性：只读的接口都加 const
    int balance() const { return balance_; }

    // 2. 参数用 const 引用，不用裸指针
    void transfer(Account& to, int amount);

    // 3. 单参数构造函数加 explicit，防隐式转换
    explicit Account(int initial) : balance_(initial) {}

    // 4. 返回 const 引用避免拷贝，但别返回内部可变引用
    const std::string& name() const { return name_; }

    // 5. 难用的接口就是坏接口：参数顺序要能自然读出来
    void deposit(int amount);          // 好
    // void update(int flag, int amount, bool force, int id);  // 坏

private:
    int balance_ = 0;
    std::string name_;
};""",
                        "narration": "接口设计的几个要点：只读函数一律加 const；参数能传引用就别传指针；单参数构造函数加 explicit，防止 5 被意外转成 Account；返回值不要暴露内部可变状态；最重要的一条是参数顺序要能读出来，一个五个参数的函数，调用处根本看不出谁是谁。",
                    },
                    {
                        "kind": "code",
                        "title": "写一个最小的测试",
                        "code": """// 不引入框架也能测：断言 + 独立的小 main
#include <cassert>

int add(int a, int b) { return a + b; }

void test_add() {
    assert(add(1, 2) == 3);
    assert(add(-1, 1) == 0);
    assert(add(0, 0) == 0);
}

int main() {
    test_add();
    std::cout << "全部测试通过\\n";
}

// 上规模后用框架：Catch2 / GoogleTest
// TEST(MathTest, AddWorks) {
//     EXPECT_EQ(add(1, 2), 3);
// }""",
                        "narration": "测试不一定要一开始就上框架。断言加一个测试用的 main，就能覆盖掉大部分低级错误。上规模之后再引入 Catch2 或 GoogleTest，它们提供更好的用例组织和失败信息。关键不是工具，而是习惯：每修一个 bug，就补一条测试，这样它永远不会再犯。",
                    },
                    {
                        "kind": "bullets",
                        "title": "工程习惯",
                        "items": [
                            ("CI 跑三件事", "编译、测试、sanitizer 构建"),
                            ("警告当错误", "-Wall -Wextra -Werror，从第一天就开"),
                            ("统一格式", "clang-format 配置文件进仓库，避免无意义的格式 diff"),
                            ("小步提交", "一次提交只做一件事，出问题好回滚"),
                        ],
                        "narration": "最后是四条工程习惯。持续集成至少跑三件事：编译、测试、sanitizer 构建。编译警告从第一天就当成错误，否则代码库长大之后你再也改不动。格式用 clang format 统一，配置文件进仓库，评审时就不会有格式争论。提交要小，一次只做一件事，出问题好回滚。",
                    },
                    {
                        "kind": "recap",
                        "title": "本课回顾",
                        "items": [
                            "const 正确、explicit、参数顺序是接口质量的核心",
                            "测试从断言开始，修一个 bug 补一条用例",
                            "CI + 警告当错误 + 统一格式 = 可持续的代码库",
                        ],
                        "narration": "到这里 13 章结束。最后一章我们把所有东西用起来，做一个完整的命令行项目。",
                    },
                ],
            },
        ],
    },
]
