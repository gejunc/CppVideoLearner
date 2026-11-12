# -*- coding: utf-8 -*-
"""每课 2 道练习题：题目、提示、可直接运行的参考答案、讲解。

约定：answer 里的代码必须是完整可编译的单文件程序，
      方便前端一键丢进代码台运行。
"""

EXERCISES = {
    # ---------------- 第 1 章 ----------------
    "l01": [
        {
            "q": "写一个程序，输出你的名字和三行自我介绍。",
            "hint": "用 std::cout 连续输出，每行结尾用 std::endl 或 '\\n'。",
            "answer": r"""#include <iostream>

int main() {
    std::cout << "你好，我是小林\n";
    std::cout << "正在学 C++\n";
    std::cout << "目标：写出能用的程序\n";
    return 0;
}""",
            "note": "endl 会额外刷一次缓冲区，纯换行用 '\\n' 更快。",
        },
        {
            "q": "把 main 的返回值改成 3，用 echo %ERRORLEVEL%（Windows）或 echo $?（Linux）看看系统拿到什么。",
            "hint": "return 的值就是进程退出码，0 表示成功。",
            "answer": r"""#include <iostream>

int main() {
    std::cout << "我返回 3\n";
    return 3;          // 退出码非 0 通常表示失败
}""",
            "note": "脚本和 CI 就是靠退出码判断程序有没有出错。",
        },
    ],
    "l02": [
        {
            "q": "故意写一个语法错误和一个未定义符号，观察两类报错有什么不同。",
            "hint": "语法错误报 error: expected ';'；未定义符号报 undefined reference。",
            "answer": r"""#include <iostream>

void declared_but_not_defined();   // 只有声明

int main() {
    declared_but_not_defined();    // 链接期才会报错
    std::cout << "不会执行到这里\n";
    return 0;
}""",
            "note": "编译错误在编译阶段就停了；undefined reference 是链接阶段的问题。",
        },
        {
            "q": "用 #define 定义一个常量 PI，再写一个函数算圆面积。",
            "hint": "#define 是预处理期的文本替换，没有类型检查。",
            "answer": r"""#include <iostream>

#define PI 3.14159

double area(double r) { return PI * r * r; }

int main() {
    std::cout << area(2.0) << '\n';
    return 0;
}""",
            "note": "现代写法应该用 constexpr double PI，有类型、能调试、作用域可控。",
        },
    ],
    # ---------------- 第 2 章 ----------------
    "l03": [
        {
            "q": "已知两个 int 变量 a=7、b=2，分别算出整数商和浮点商。",
            "hint": "把其中一个转成 double，或者写 2.0。",
            "answer": r"""#include <iostream>

int main() {
    int a = 7, b = 2;
    std::cout << "整数商: " << a / b << '\n';        // 3
    std::cout << "浮点商: " << a / 2.0 << '\n';      // 3.5
    std::cout << "转换后: " << static_cast<double>(a) / b << '\n';
    return 0;
}""",
            "note": "两个 int 相除结果一定是 int，小数部分直接丢弃。",
        },
        {
            "q": "声明一个有符号 char，加几次 1 越过上限，观察结果（注意这可能是未定义行为）。",
            "hint": "换成 unsigned char 才能观察到确定的回绕。",
            "answer": r"""#include <iostream>

int main() {
    unsigned char uc = 255;
    uc = static_cast<unsigned char>(uc + 1);
    std::cout << "回绕后: " << static_cast<int>(uc) << '\n';   // 0

    // signed char 溢出是 UB，不要依赖它的结果
    return 0;
}""",
            "note": "无符号回绕是标准定义的行为；有符号溢出是未定义行为，编译器可以做任何事。",
        },
    ],
    "l04": [
        {
            "q": "用 constexpr 定义一个数组长度常量，创建一个数组并遍历打印。",
            "hint": "只有 constexpr 才能当数组长度。",
            "answer": r"""#include <iostream>

constexpr int kSize = 5;

int main() {
    int arr[kSize] = {1, 2, 3, 4, 5};
    for (const auto& v : arr) std::cout << v << ' ';
    std::cout << '\n';
    return 0;
}""",
            "note": "const 只保证“不修改”，constexpr 才保证“编译期已知”。",
        },
        {
            "q": "用 auto 和范围 for 求一个 vector 的平均值。",
            "hint": "注意用 const auto& 避免拷贝，同时注意整数除法。",
            "answer": r"""#include <iostream>
#include <vector>

int main() {
    std::vector<int> v{10, 20, 30, 40};
    double sum = 0;
    for (const auto& x : v) sum += x;
    std::cout << "平均: " << sum / v.size() << '\n';
    return 0;
}""",
            "note": "sum 声明成 double，累加时就在做浮点加法，最后不会截断。",
        },
    ],
    "l05": [
        {
            "q": "写一个判断年份是不是闰年的表达式（能被 4 整除且不能被 100 整除，或能被 400 整除）。",
            "hint": "用逻辑与/或组合，注意比较运算符不能连写。",
            "answer": r"""#include <iostream>

bool isLeap(int y) {
    return (y % 4 == 0 && y % 100 != 0) || (y % 400 == 0);
}

int main() {
    for (int y : {1900, 2000, 2024, 2023})
        std::cout << y << " -> " << (isLeap(y) ? "闰年" : "平年") << '\n';
    return 0;
}""",
            "note": "1900 不是闰年（被 100 整除但不被 400 整除），2000 是。",
        },
        {
            "q": "用三目运算符写一个函数，返回两个数中较大的那个。",
            "hint": "a > b ? a : b",
            "answer": r"""#include <iostream>

int maxOf(int a, int b) { return a > b ? a : b; }

int main() {
    std::cout << maxOf(3, 7) << '\n';
    std::cout << maxOf(-1, -5) << '\n';
    return 0;
}""",
            "note": "标准库已经有 std::max，自己写只是为了理解三目运算符。",
        },
    ],
    "l06": [
        {
            "q": "读入两个整数，输出它们的和与平均值。",
            "hint": "平均值要用浮点运算。",
            "answer": r"""#include <iostream>

int main() {
    int a, b;
    std::cout << "输入两个整数: ";
    if (!(std::cin >> a >> b)) {
        std::cout << "输入无效\n";
        return 1;
    }
    std::cout << "和: " << a + b << '\n';
    std::cout << "平均: " << (a + b) / 2.0 << '\n';
    return 0;
}""",
            "note": "cin 放进 if 里，可以一行同时完成读取和失败判断。",
        },
        {
            "q": "读入一整行文字（可能包含空格），原样输出。",
            "hint": "cin >> 会在空格处停下，要用 getline。",
            "answer": r"""#include <iostream>
#include <string>

int main() {
    std::string line;
    std::cout << "输入一句话: ";
    std::getline(std::cin, line);
    std::cout << "你输入了: " << line << '\n';
    return 0;
}""",
            "note": "如果前面用过 cin >>，要先 cin.ignore() 吃掉多余的换行符。",
        },
    ],
    # ---------------- 第 3 章 ----------------
    "l07": [
        {
            "q": "把百分制成绩转换成等级（90+ A，75+ B，60+ C，其余 D）。",
            "hint": "阶梯判断要从最严格的条件开始写。",
            "answer": r"""#include <iostream>

int main() {
    int score = 78;
    if (score >= 90)      std::cout << "A\n";
    else if (score >= 75) std::cout << "B\n";
    else if (score >= 60) std::cout << "C\n";
    else                  std::cout << "D\n";
    return 0;
}""",
            "note": "如果先判断 >= 60，那么 95 分会落到 C，顺序决定结果。",
        },
        {
            "q": "用 switch 把数字 1~7 映射成星期几，非 1~7 输出“未知”。",
            "hint": "记得每个 case 后面写 break。",
            "answer": r"""#include <iostream>

int main() {
    for (int d : {1, 4, 7, 9}) {
        switch (d) {
            case 1: std::cout << "周一\n"; break;
            case 2: std::cout << "周二\n"; break;
            case 3: std::cout << "周三\n"; break;
            case 4: std::cout << "周四\n"; break;
            case 5: std::cout << "周五\n"; break;
            case 6: std::cout << "周六\n"; break;
            case 7: std::cout << "周日\n"; break;
            default: std::cout << "未知\n"; break;
        }
    }
    return 0;
}""",
            "note": "忘了 break 会“贯穿”到下一个 case，这是 switch 最经典的 bug。",
        },
    ],
    "l08": [
        {
            "q": "用循环输出 1 到 100 里所有能被 7 整除的数。",
            "hint": "for + if (i % 7 == 0)。",
            "answer": r"""#include <iostream>

int main() {
    for (int i = 1; i <= 100; ++i)
        if (i % 7 == 0) std::cout << i << ' ';
    std::cout << '\n';
    return 0;
}""",
            "note": "也可以从 7 开始每次加 7，少判断 100 次。",
        },
        {
            "q": "用 while 计算一个正整数的位数（例如 12345 有 5 位）。",
            "hint": "每次除以 10，直到变成 0。",
            "answer": r"""#include <iostream>

int main() {
    int n = 12345;
    int digits = 0;
    while (n > 0) {
        ++digits;
        n /= 10;
    }
    std::cout << "位数: " << digits << '\n';
    return 0;
}""",
            "note": "注意 n 被改掉了，如果需要保留原值，用临时变量。",
        },
    ],
    "l09": [
        {
            "q": "在 1~100 里找第一个能被 3、5、7 同时整除的数，找到就跳出。",
            "hint": "用 break，或者在 for 的条件里加标志。",
            "answer": r"""#include <iostream>

int main() {
    for (int i = 1; i <= 100; ++i) {
        if (i % 3 == 0 && i % 5 == 0 && i % 7 == 0) {
            std::cout << "第一个: " << i << '\n';
            break;
        }
    }
    return 0;
}""",
            "note": "答案就是 105 以内的 105，其实超出了 100，循环因此什么也不输出——可以自己改上限验证。",
        },
        {
            "q": "用 continue 跳过奇数，只累加 1~10 里的偶数。",
            "hint": "continue 之后本轮剩下的语句不执行。",
            "answer": r"""#include <iostream>

int main() {
    int sum = 0;
    for (int i = 1; i <= 10; ++i) {
        if (i % 2 != 0) continue;
        sum += i;
    }
    std::cout << "偶数之和: " << sum << '\n';   // 30
    return 0;
}""",
            "note": "continue 只影响当前这一轮，不会结束循环。",
        },
    ],
    # ---------------- 第 4 章 ----------------
    "l10": [
        {
            "q": "写三个同名函数 print，分别接受 int、double、string，验证重载。",
            "hint": "参数列表不同才能构成重载。",
            "answer": r"""#include <iostream>
#include <string>

void print(int x)                { std::cout << "int: " << x << '\n'; }
void print(double x)             { std::cout << "double: " << x << '\n'; }
void print(const std::string& s) { std::cout << "string: " << s << '\n'; }

int main() {
    print(42);
    print(3.14);
    print(std::string("hi"));
    return 0;
}""",
            "note": "传字符串字面量时可能匹配 const char* 版本，所以这里显式构造 std::string。",
        },
        {
            "q": "写一个函数，返回两个整数中较大的；再写一个重载版本，返回三个中最大的。",
            "hint": "三个数可以复用两个数的版本。",
            "answer": r"""#include <iostream>

int biggest(int a, int b) { return a > b ? a : b; }

int biggest(int a, int b, int c) { return biggest(biggest(a, b), c); }

int main() {
    std::cout << biggest(3, 7) << '\n';
    std::cout << biggest(3, 7, 5) << '\n';
    return 0;
}""",
            "note": "参数个数不同也是合法重载。",
        },
    ],
    "l11": [
        {
            "q": "写一个函数交换两个整数，分别用引用和指针两种方式实现。",
            "hint": "引用版更简洁，指针版需要判空。",
            "answer": r"""#include <iostream>

void swapRef(int& a, int& b) { int t = a; a = b; b = t; }

void swapPtr(int* a, int* b) {
    if (!a || !b) return;
    int t = *a; *a = *b; *b = t;
}

int main() {
    int x = 1, y = 2;
    swapRef(x, y);
    std::cout << x << ' ' << y << '\n';
    swapPtr(&x, &y);
    std::cout << x << ' ' << y << '\n';
    return 0;
}""",
            "note": "标准库已经有 std::swap，这里只是为了理解两种传参。",
        },
        {
            "q": "写一个函数接收大的 vector，用 const 引用传参并返回总和，体会零拷贝。",
            "hint": "const std::vector<int>& 既不改也不拷贝。",
            "answer": r"""#include <iostream>
#include <vector>

long long total(const std::vector<int>& v) {
    long long s = 0;
    for (const auto& x : v) s += x;
    return s;
}

int main() {
    std::vector<int> v(1000000, 1);
    std::cout << total(v) << '\n';
    return 0;
}""",
            "note": "如果把参数写成 std::vector<int> v，这一百万个元素会被完整复制一遍。",
        },
    ],
    "l12": [
        {
            "q": "写一个带默认参数的函数 log(msg, level=0, withTime=false)。",
            "hint": "默认参数必须从右往左连续给出。",
            "answer": r"""#include <iostream>
#include <string>

void log(const std::string& msg, int level = 0, bool withTime = false) {
    std::cout << (withTime ? "[时间] " : "") << "[L" << level << "] " << msg << '\n';
}

int main() {
    log("启动");
    log("警告", 2);
    log("调试", 1, true);
    return 0;
}""",
            "note": "调用方只能从右边开始省略，不能只给第三个参数。",
        },
        {
            "q": "写一个递归函数计算斐波那契数列第 n 项，再想想为什么 n=40 会很慢。",
            "hint": "朴素递归会重复计算大量子问题。",
            "answer": r"""#include <iostream>

long long fib(int n) {
    if (n <= 1) return n;
    return fib(n - 1) + fib(n - 2);
}

int main() {
    std::cout << fib(20) << '\n';   // 6765，20 已经能感觉到慢了
    return 0;
}""",
            "note": "复杂度是 O(2^n)。改进办法：加记忆化，或者直接改成循环 O(n)。",
        },
    ],
    # ---------------- 第 5 章 ----------------
    "l13": [
        {
            "q": "用 std::array 存 5 个分数，求最大值和平均值。",
            "hint": "std::array 知道自己的长度，可以配合范围 for。",
            "answer": r"""#include <array>
#include <iostream>

int main() {
    std::array<int, 5> scores{88, 92, 76, 95, 60};
    int mx = scores[0];
    double sum = 0;
    for (int s : scores) { if (s > mx) mx = s; sum += s; }
    std::cout << "最高: " << mx << '\n';
    std::cout << "平均: " << sum / scores.size() << '\n';
    return 0;
}""",
            "note": "也可以用 std::max_element，少写一个循环。",
        },
        {
            "q": "写一个 3x3 二维数组并输出为矩阵，再求主对角线之和。",
            "hint": "grid[i][i] 就是主对角线。",
            "answer": r"""#include <iostream>

int main() {
    int g[3][3] = {{1,2,3},{4,5,6},{7,8,9}};
    for (int i = 0; i < 3; ++i) {
        for (int j = 0; j < 3; ++j) std::cout << g[i][j] << ' ';
        std::cout << '\n';
    }
    int s = 0;
    for (int i = 0; i < 3; ++i) s += g[i][i];
    std::cout << "对角线和: " << s << '\n';
    return 0;
}""",
            "note": "二维数组是行优先存储的，先行后列遍历对缓存更友好。",
        },
    ],
    "l14": [
        {
            "q": "统计一个字符串里有多少个元音字母（a e i o u）。",
            "hint": "用范围 for 遍历，配合 find。",
            "answer": r"""#include <iostream>
#include <string>

int main() {
    std::string s = "hello world, this is c++";
    int n = 0;
    for (char c : s)
        if (std::string("aeiou").find(c) != std::string::npos) ++n;
    std::cout << "元音数: " << n << '\n';
    return 0;
}""",
            "note": "npos 是个很大的无符号数，只能和 npos 比较，不能写 < 0。",
        },
        {
            "q": "把一句话按空格切分成单词，每个单词单独一行输出。",
            "hint": "用 istringstream 自动按空白分词。",
            "answer": r"""#include <iostream>
#include <sstream>
#include <string>

int main() {
    std::string line = "C++  is  a  compiled  language";
    std::istringstream ss(line);
    std::string w;
    while (ss >> w) std::cout << w << '\n';
    return 0;
}""",
            "note": "istringstream 是内存里的流，处理和 cin 一样的语法。",
        },
    ],
    "l15": [
        {
            "q": "用指针遍历一个数组并求和，全程不使用下标。",
            "hint": "end 用 a + n，循环条件是指针不相等。",
            "answer": r"""#include <iostream>

int main() {
    int a[5] = {1, 2, 3, 4, 5};
    int sum = 0;
    for (int* p = a; p != a + 5; ++p) sum += *p;
    std::cout << "和: " << sum << '\n';
    return 0;
}""",
            "note": "指针算术按元素大小步进，int* 加 1 前进 4 个字节。",
        },
        {
            "q": "写一个函数，通过指针参数同时返回数组的最小值和最大值。",
            "hint": "输出参数用指针，调用方传地址进来。",
            "answer": r"""#include <iostream>

void minmax(const int* a, int n, int* mn, int* mx) {
    if (!a || n <= 0 || !mn || !mx) return;
    *mn = *mx = a[0];
    for (int i = 1; i < n; ++i) {
        if (a[i] < *mn) *mn = a[i];
        if (a[i] > *mx) *mx = a[i];
    }
}

int main() {
    int a[5] = {3, 9, -2, 7, 0};
    int lo = 0, hi = 0;
    minmax(a, 5, &lo, &hi);
    std::cout << "最小 " << lo << " 最大 " << hi << '\n';
    return 0;
}""",
            "note": "现代 C++ 更推荐返回 std::pair，输出参数只在需要多返回值时用。",
        },
    ],
    "l16": [
        {
            "q": "用引用参数写一个函数，把 vector 里所有元素翻倍。",
            "hint": "参数写 std::vector<int>&，不加 const 才能改。",
            "answer": r"""#include <iostream>
#include <vector>

void doubleAll(std::vector<int>& v) {
    for (auto& x : v) x *= 2;
}

int main() {
    std::vector<int> v{1, 2, 3};
    doubleAll(v);
    for (int x : v) std::cout << x << ' ';
    std::cout << '\n';
    return 0;
}""",
            "note": "如果参数写成 const 引用，里面的修改会编译失败，这正是我们想要的安全。",
        },
        {
            "q": "写一个返回引用参数的函数，用于取两个数中较大的那个，并说明为什么不能返回局部变量的引用。",
            "hint": "参数的生命周期由调用方保证。",
            "answer": r"""#include <iostream>

int& pick(int& a, int& b) { return a > b ? a : b; }

// int& bad() { int x = 1; return x; }   // 悬空引用，绝对不要

int main() {
    int x = 3, y = 7;
    pick(x, y) = 100;              // 直接修改较大的那个
    std::cout << x << ' ' << y << '\n';
    return 0;
}""",
            "note": "返回引用让函数可以作为赋值左值，标准库的 vector::operator[] 就是这么做的。",
        },
    ],
    # ---------------- 第 6 章 ----------------
    "l17": [
        {
            "q": "定义一个 Rectangle 类，有宽高，提供 area() 和 perimeter()。",
            "hint": "数据私有，方法公开。",
            "answer": r"""#include <iostream>

class Rectangle {
public:
    Rectangle(double w, double h) : w_(w), h_(h) {}
    double area() const      { return w_ * h_; }
    double perimeter() const { return 2 * (w_ + h_); }
private:
    double w_ = 0, h_ = 0;
};

int main() {
    Rectangle r(3, 4);
    std::cout << "面积 " << r.area() << " 周长 " << r.perimeter() << '\n';
    return 0;
}""",
            "note": "两个查询方法都加了 const，这样 const 对象也能调用它们。",
        },
        {
            "q": "用 struct 定义 Point，并写一个函数计算两点距离。",
            "hint": "纯数据聚合用 struct，数学运算用 std::sqrt。",
            "answer": r"""#include <cmath>
#include <iostream>

struct Point { double x = 0, y = 0; };

double dist(const Point& a, const Point& b) {
    return std::sqrt((a.x - b.x) * (a.x - b.x) + (a.y - b.y) * (a.y - b.y));
}

int main() {
    Point p{0, 0}, q{3, 4};
    std::cout << dist(p, q) << '\n';   // 5
    return 0;
}""",
            "note": "结构体默认 public，适合这种纯数据场景。",
        },
    ],
    "l18": [
        {
            "q": "写一个有析构函数的类，在构造和析构时各打印一行，观察对象生命周期。",
            "hint": "进入和离开作用域时各触发一次。",
            "answer": r"""#include <iostream>

class Tracer {
public:
    explicit Tracer(const char* name) : name_(name) {
        std::cout << "构造 " << name_ << '\n';
    }
    ~Tracer() { std::cout << "析构 " << name_ << '\n'; }
private:
    const char* name_;
};

int main() {
    Tracer a("a");
    {
        Tracer b("b");
    }   // b 在这里析构
    std::cout << "main 结束\n";
    return 0;
}""",
            "note": "析构顺序和构造顺序严格相反，这是栈展开保证的。",
        },
        {
            "q": "用一个 RAII 类管理一段动态数组，构造时 new，析构时 delete[]。",
            "hint": "记得处理拷贝（这里直接删掉）。",
            "answer": r"""#include <iostream>

class IntArray {
public:
    explicit IntArray(int n) : p_(new int[n]{}), n_(n) {}
    ~IntArray() { delete[] p_; }

    IntArray(const IntArray&) = delete;
    IntArray& operator=(const IntArray&) = delete;

    int& operator[](int i) { return p_[i]; }
    int size() const { return n_; }

private:
    int* p_ = nullptr;
    int  n_ = 0;
};

int main() {
    IntArray a(5);
    for (int i = 0; i < a.size(); ++i) a[i] = i * i;
    for (int i = 0; i < a.size(); ++i) std::cout << a[i] << ' ';
    std::cout << '\n';
    return 0;
}""",
            "note": "这个类其实就等价于 std::vector，真实项目直接用它就行。",
        },
    ],
    "l19": [
        {
            "q": "给类加一个 const 成员函数和一个非 const 成员函数，验证 const 对象只能调用前者。",
            "hint": "const 对象调用非 const 成员函数会编译失败。",
            "answer": r"""#include <iostream>

class Counter {
public:
    void inc() { ++n_; }
    int value() const { return n_; }
private:
    int n_ = 0;
};

int main() {
    Counter c;
    c.inc();
    const Counter& rc = c;
    std::cout << rc.value() << '\n';
    // rc.inc();        // 编译错误：不能修改 const 对象
    return 0;
}""",
            "note": "把只读方法都标成 const，你的类才能被 const 引用安全使用。",
        },
        {
            "q": "实现一个链式调用的计数器（inc 返回自身引用）。",
            "hint": "返回 *this。",
            "answer": r"""#include <iostream>

class Counter {
public:
    Counter& inc() { ++n_; return *this; }
    Counter& add(int k) { n_ += k; return *this; }
    int value() const { return n_; }
private:
    int n_ = 0;
};

int main() {
    Counter c;
    c.inc().add(10).inc();
    std::cout << c.value() << '\n';   // 12
    return 0;
}""",
            "note": "std::cout 的连续 << 就是靠返回流引用实现的。",
        },
    ],
    "l20": [
        {
            "q": "定义一个基类 Shape 和派生类 Circle，验证构造和析构顺序。",
            "hint": "构造：先基类后派生；析构：反过来。",
            "answer": r"""#include <iostream>

struct Base {
    Base()  { std::cout << "Base 构造\n"; }
    ~Base() { std::cout << "Base 析构\n"; }
};

struct Derived : Base {
    Derived()  { std::cout << "Derived 构造\n"; }
    ~Derived() { std::cout << "Derived 析构\n"; }
};

int main() {
    Derived d;
    std::cout << "---\n";
    return 0;
}""",
            "note": "派生类析构先执行，基类析构后执行，保证资源按逆序释放。",
        },
        {
            "q": "写一个基类 Animal 带 eat()，派生类 Dog 增加 bark()，验证派生类能用基类的公开方法。",
            "hint": "public 继承会把公开成员继承下来。",
            "answer": r"""#include <iostream>

class Animal {
public:
    void eat() const { std::cout << "eating\n"; }
};

class Dog : public Animal {
public:
    void bark() const { std::cout << "woof\n"; }
};

int main() {
    Dog d;
    d.eat();
    d.bark();
    return 0;
}""",
            "note": "注意这里不是多态：如果通过 Animal* 调用，只能看到 eat。",
        },
    ],
    # ---------------- 第 7 章 ----------------
    "l21": [
        {
            "q": "定义抽象基类 Shape（纯虚 area），派生 Circle 和 Square，用基类指针容器统一调用。",
            "hint": "基类要有虚析构。",
            "answer": r"""#include <iostream>
#include <vector>
#include <memory>

class Shape {
public:
    virtual double area() const = 0;
    virtual ~Shape() = default;
};

class Circle : public Shape {
public:
    explicit Circle(double r) : r_(r) {}
    double area() const override { return 3.14159 * r_ * r_; }
private:
    double r_;
};

class Square : public Shape {
public:
    explicit Square(double s) : s_(s) {}
    double area() const override { return s_ * s_; }
private:
    double s_;
};

int main() {
    std::vector<std::unique_ptr<Shape>> v;
    v.push_back(std::make_unique<Circle>(1.0));
    v.push_back(std::make_unique<Square>(2.0));
    double sum = 0;
    for (const auto& s : v) sum += s->area();
    std::cout << "总面积 " << sum << '\n';
    return 0;
}""",
            "note": "新增一种图形时，这个求和循环一行都不用改，这就是多态的价值。",
        },
        {
            "q": "不加 virtual 直接通过基类指针调用同名函数，观察结果和加了 virtual 有什么不同。",
            "hint": "这就是静态绑定和动态绑定的区别。",
            "answer": r"""#include <iostream>

struct Base { void hello() const { std::cout << "Base\n"; } };
struct Derived : Base { void hello() const { std::cout << "Derived\n"; } };

int main() {
    Derived d;
    Base* p = &d;
    p->hello();      // 输出 Base —— 非虚函数按静态类型绑定
    d.hello();       // 输出 Derived
    return 0;
}""",
            "note": "把基类的 hello 改成 virtual，第一行就会输出 Derived。",
        },
    ],
    "l22": [
        {
            "q": "用 unique_ptr 管理一个对象，演示所有权转移。",
            "hint": "move 之后原指针变空。",
            "answer": r"""#include <iostream>
#include <memory>

struct Widget {
    int id = 0;
    explicit Widget(int i) : id(i) { std::cout << "创建 " << id << '\n'; }
    ~Widget() { std::cout << "销毁 " << id << '\n'; }
};

int main() {
    auto p = std::make_unique<Widget>(1);
    auto q = std::move(p);          // 所有权转移
    std::cout << "p 为空: " << (p == nullptr) << '\n';
    return 0;                        // q 析构，对象销毁
}""",
            "note": "unique_ptr 不能拷贝，只能移动，这正是“独占所有权”的编译期保证。",
        },
        {
            "q": "用 shared_ptr 演示引用计数的变化。",
            "hint": "use_count() 看当前有多少个持有者。",
            "answer": r"""#include <iostream>
#include <memory>

int main() {
    auto a = std::make_shared<int>(42);
    std::cout << a.use_count() << '\n';    // 1
    {
        auto b = a;
        std::cout << a.use_count() << '\n';  // 2
    }
    std::cout << a.use_count() << '\n';    // 1
    return 0;
}""",
            "note": "引用计数归零才释放对象。循环引用会让计数永远不归零，要用 weak_ptr 打破。",
        },
    ],
    "l23": [
        {
            "q": "用 vector 存 10 个整数，排序后输出，再统计有多少个大于 5。",
            "hint": "std::sort + std::count_if。",
            "answer": r"""#include <algorithm>
#include <iostream>
#include <vector>

int main() {
    std::vector<int> v{7, 2, 9, 4, 1, 8, 3, 10, 6, 5};
    std::sort(v.begin(), v.end());
    for (int x : v) std::cout << x << ' ';
    std::cout << '\n';
    int n = static_cast<int>(std::count_if(v.begin(), v.end(),
                                           [](int x) { return x > 5; }));
    std::cout << "大于 5 的: " << n << '\n';
    return 0;
}""",
            "note": "sort 默认升序，要降序就传 std::greater<>{} 作为比较器。",
        },
        {
            "q": "用 map 统计一段文字里每个字符出现的次数。",
            "hint": "map<char,int>，用 [] 自增。",
            "answer": r"""#include <iostream>
#include <map>
#include <string>

int main() {
    std::string s = "hello";
    std::map<char, int> cnt;
    for (char c : s) ++cnt[c];          // 不存在时自动插入 0 再自增
    for (const auto& [ch, n] : cnt)
        std::cout << ch << ": " << n << '\n';
    return 0;
}""",
            "note": "统计场景正好适合用 []，因为“不存在就插入”正是我们要的行为。",
        },
    ],
    "l24": [
        {
            "q": "用 lambda 和 std::sort 按字符串长度排序一个 vector<string>。",
            "hint": "比较器返回 a.size() < b.size()。",
            "answer": r"""#include <algorithm>
#include <iostream>
#include <string>
#include <vector>

int main() {
    std::vector<std::string> v{"ccc", "a", "bbbb", "dd"};
    std::sort(v.begin(), v.end(),
              [](const std::string& a, const std::string& b) {
                  return a.size() < b.size();
              });
    for (const auto& s : v) std::cout << s << ' ';
    std::cout << '\n';
    return 0;
}""",
            "note": "长度相同的元素相对顺序不保证，需要稳定排序就用 stable_sort。",
        },
        {
            "q": "写一个函数返回大 vector，在主函数里接收，体会移动语义（不写 std::move 也能零拷贝）。",
            "hint": "返回局部对象时编译器会做 RVO，不需要手写 move。",
            "answer": r"""#include <iostream>
#include <vector>

std::vector<int> makeBig() {
    std::vector<int> v(1000000, 7);
    return v;                 // RVO，不拷贝
}

int main() {
    auto v = makeBig();
    std::cout << v.size() << '\n';
    return 0;
}""",
            "note": "手写 std::move(v) 反而可能阻止返回值优化。",
        },
    ],
    # ---------------- 第 8 章 ----------------
    "l25": [
        {
            "q": "写一个函数在参数不合法时抛异常，调用方用 try/catch 捕获并打印。",
            "hint": "抛 std::invalid_argument，捕获用 const 引用。",
            "answer": r"""#include <iostream>
#include <stdexcept>

double divide(double a, double b) {
    if (b == 0) throw std::invalid_argument("除数不能为 0");
    return a / b;
}

int main() {
    try {
        std::cout << divide(1, 0) << '\n';
    } catch (const std::invalid_argument& e) {
        std::cout << "错误: " << e.what() << '\n';
    }
    return 0;
}""",
            "note": "捕获参数一定要用 const 引用，按值捕获会切片并多一次拷贝。",
        },
        {
            "q": "把一段文字写入文件，再读回来逐行打印。",
            "hint": "ofstream 写、ifstream 配合 getline 读。",
            "answer": r"""#include <fstream>
#include <iostream>
#include <string>

int main() {
    {
        std::ofstream out("demo.txt");
        out << "第一行\n第二行\n";
    }

    std::ifstream in("demo.txt");
    if (!in) { std::cout << "打开失败\n"; return 1; }
    std::string line;
    while (std::getline(in, line)) std::cout << line << '\n';
    return 0;
}""",
            "note": "文件会在流对象析构时自动关闭，所以用大括号控制生命周期就够。",
        },
    ],
    "l26": [
        {
            "q": "给成绩管理程序加一个功能：按平均分从高到低排序输出。",
            "hint": "std::sort 配 lambda 比较器。",
            "answer": r"""#include <algorithm>
#include <iostream>
#include <string>
#include <vector>

struct Student {
    std::string name;
    double avg = 0;
};

int main() {
    std::vector<Student> v{{"Ann", 88.5}, {"Bob", 92.0}, {"Cid", 76.5}};
    std::sort(v.begin(), v.end(),
              [](const Student& a, const Student& b) { return a.avg > b.avg; });
    for (const auto& s : v)
        std::cout << s.name << ' ' << s.avg << '\n';
    return 0;
}""",
            "note": "想升序就把 > 换成 <。比较器必须满足严格弱序，不要写 <=。",
        },
        {
            "q": "统计成绩的及格率（>=60 的比例）。",
            "hint": "用 count_if 配合 double 除法。",
            "answer": r"""#include <algorithm>
#include <iostream>
#include <vector>

int main() {
    std::vector<int> scores{88, 92, 55, 76, 41, 60};
    auto pass = std::count_if(scores.begin(), scores.end(),
                              [](int s) { return s >= 60; });
    double rate = 100.0 * pass / scores.size();
    std::cout << "及格率 " << rate << "%\n";
    return 0;
}""",
            "note": "乘 100.0 而不是 100，避免整数除法把小数丢掉。",
        },
    ],
    # ---------------- 第 9 章 并发 ----------------
    "l27": [
        {
            "q": "开两个线程各自打印 5 行，主线程 join 之后输出“完成”。",
            "hint": "线程函数可以用 lambda。",
            "answer": r"""#include <iostream>
#include <thread>

int main() {
    std::thread t1([]{ for (int i = 0; i < 5; ++i) std::cout << "A" << i << '\n'; });
    std::thread t2([]{ for (int i = 0; i < 5; ++i) std::cout << "B" << i << '\n'; });

    t1.join();
    t2.join();
    std::cout << "完成\n";
    return 0;
}""",
            "note": "两个线程的输出会交错，这是正常的；控制台输出本身不是线程安全的。",
        },
        {
            "q": "不加 join 直接让 thread 对象析构，观察会发生什么。",
            "hint": "joinable 的 thread 析构会调用 std::terminate。",
            "answer": r"""#include <iostream>
#include <thread>

int main() {
    std::thread t([]{ std::cout << "在跑\n"; });
    // 故意不 join：
    // t 离开作用域时析构 -> std::terminate -> 程序异常终止
    std::cout << "主线程继续\n";
    return 0;
}""",
            "note": "真正的程序里，要么 join，要么 detach，二者必选其一。",
        },
    ],
    "l28": [
        {
            "q": "两个线程各把同一个计数器加 10000 次，用 mutex 保护，最后结果应该是 20000。",
            "hint": "用 lock_guard 包住临界区。",
            "answer": r"""#include <iostream>
#include <mutex>
#include <thread>

int counter = 0;
std::mutex m;

void work() {
    for (int i = 0; i < 10000; ++i) {
        std::lock_guard<std::mutex> lock(m);
        ++counter;
    }
}

int main() {
    std::thread a(work), b(work);
    a.join();
    b.join();
    std::cout << counter << '\n';    // 20000
    return 0;
}""",
            "note": "把 lock_guard 去掉再跑几十次，你会看到小于 20000 的结果，那就是数据竞争。",
        },
        {
            "q": "用 scoped_lock 同时锁两个互斥量，避免死锁。",
            "hint": "一次传入两个 mutex，它内部会按固定顺序加锁。",
            "answer": r"""#include <iostream>
#include <mutex>
#include <thread>

std::mutex m1, m2;
int a = 0, b = 0;

void transfer() {
    std::scoped_lock lock(m1, m2);   // 不会死锁
    ++a;
    ++b;
}

int main() {
    std::thread t1(transfer), t2(transfer);
    t1.join();
    t2.join();
    std::cout << a << ' ' << b << '\n';
    return 0;
}""",
            "note": "手写 m1.lock(); m2.lock(); 在两个线程里顺序相反，就会死锁。",
        },
    ],
    "l29": [
        {
            "q": "实现一个最简单的生产者消费者：生产者放 5 个数，消费者取走并打印。",
            "hint": "condition_variable + wait 的谓词版本。",
            "answer": r"""#include <condition_variable>
#include <iostream>
#include <mutex>
#include <queue>
#include <thread>

std::mutex m;
std::condition_variable cv;
std::queue<int> q;
bool done = false;

int main() {
    std::thread prod([]{
        for (int i = 1; i <= 5; ++i) {
            { std::lock_guard<std::mutex> lk(m); q.push(i); }
            cv.notify_one();
        }
        { std::lock_guard<std::mutex> lk(m); done = true; }
        cv.notify_all();
    });

    std::thread cons([]{
        while (true) {
            std::unique_lock<std::mutex> lk(m);
            cv.wait(lk, []{ return done || !q.empty(); });
            if (q.empty() && done) return;
            int v = q.front(); q.pop();
            lk.unlock();
            std::cout << "取到 " << v << '\n';
        }
    });

    prod.join();
    cons.join();
    return 0;
}""",
            "note": "wait 的谓词是关键，它防止虚假唤醒导致取到空队列。",
        },
    ],
    "l30": [
        {
            "q": "用 atomic 实现两个线程各加 10000 次，不用锁。",
            "hint": "atomic 的 ++ 是原子的。",
            "answer": r"""#include <atomic>
#include <iostream>
#include <thread>

std::atomic<int> counter{0};

void work() {
    for (int i = 0; i < 10000; ++i) ++counter;
}

int main() {
    std::thread a(work), b(work);
    a.join();
    b.join();
    std::cout << counter.load() << '\n';   // 20000
    return 0;
}""",
            "note": "单变量计数用 atomic 比 mutex 快很多，因为没有加锁的开销。",
        },
    ],
    "l31": [
        {
            "q": "用 std::async 并行计算两段区间的和，再用 future.get 汇总。",
            "hint": "记得传 std::launch::async。",
            "answer": r"""#include <future>
#include <iostream>
#include <numeric>
#include <vector>

int main() {
    std::vector<int> v(1000, 1);

    auto f1 = std::async(std::launch::async, [&]{ return std::accumulate(v.begin(), v.begin() + 500, 0); });
    auto f2 = std::async(std::launch::async, [&]{ return std::accumulate(v.begin() + 500, v.end(), 0); });

    std::cout << f1.get() + f2.get() << '\n';   // 1000
    return 0;
}""",
            "note": "future.get 会阻塞到结果就绪，且只能调用一次。",
        },
    ],
    # ---------------- 第 10 章 工具链 ----------------
    "l32": [
        {
            "q": "把打印函数拆到单独的 .h / .cpp 里，主程序包含头文件调用。演示头文件放声明、源文件放定义。",
            "hint": "头文件用 #pragma once；单文件演示可以把声明和定义都写在同一个文件里对比。",
            "answer": r"""#include <iostream>

// 相当于头文件里的声明
void greet(const char* name);

// 相当于源文件里的定义
void greet(const char* name) {
    std::cout << "你好, " << name << '\n';
}

int main() {
    greet("世界");
    return 0;
}""",
            "note": "拆成两个文件时，定义只能出现在一个 .cpp 里，否则链接期重复定义。",
        },
    ],
    "l33": [
        {
            "q": "把这个程序的编译命令改写成 CMakeLists.txt（可多文件）。",
            "hint": "add_executable + target_include_directories。",
            "answer": r"""#include <iostream>

// 假设有 src/main.cpp 和 src/math_utils.cpp
// CMakeLists.txt:
//   cmake_minimum_required(VERSION 3.20)
//   project(Demo LANGUAGES CXX)
//   set(CMAKE_CXX_STANDARD 20)
//   add_executable(demo src/main.cpp src/math_utils.cpp)
//
// 构建：
//   cmake -S . -B build
//   cmake --build build

int main() {
    std::cout << "用 CMake 构建我\n";
    return 0;
}""",
            "note": "配置目录和构建目录分开，是 CMake 的标准实践。",
        },
    ],
    "l34": [
        {
            "q": "故意制造一个数组越界，分别在不带和带 -fsanitize=address 的情况下运行，对比提示信息。",
            "hint": "sanitizer 会精确报出越界的地址和使用栈。",
            "answer": r"""#include <iostream>

int main() {
    int* a = new int[5]{};
    a[7] = 42;                     // 越界写
    std::cout << a[7] << '\n';
    delete[] a;
    return 0;
}

// 编译时加：-g -fsanitize=address
// 运行会打印 heap-buffer-overflow 和完整调用栈""",
            "note": "不加 sanitizer 时这段代码可能“看起来正常”，这正是内存错误最难查的地方。",
        },
    ],
    "l35": [
        {
            "q": "写一个使用已释放内存的程序，观察 ASan 的 heap-use-after-free 报告。",
            "hint": "delete 之后继续访问。",
            "answer": r"""#include <iostream>

int main() {
    int* p = new int(10);
    delete p;
    std::cout << *p << '\n';       // 释放后使用
    return 0;
}

// -g -fsanitize=address 会报 heap-use-after-free""",
            "note": "改成 std::unique_ptr 后，这类错误在编译期就写不出来了。",
        },
    ],
    "l36": [
        {
            "q": "用 chrono 测量一段循环的耗时，输出毫秒数。",
            "hint": "steady_clock 是单调时钟，适合计时。",
            "answer": r"""#include <chrono>
#include <iostream>

int main() {
    auto t0 = std::chrono::steady_clock::now();

    long long s = 0;
    for (int i = 0; i < 10000000; ++i) s += i;

    auto t1 = std::chrono::steady_clock::now();
    auto ms = std::chrono::duration_cast<std::chrono::milliseconds>(t1 - t0).count();

    std::cout << "耗时 " << ms << " ms，结果 " << s << '\n';
    return 0;
}""",
            "note": "测性能时注意别让编译器把整个循环优化掉，可以用 volatile 或者把结果输出。",
        },
    ],
    # ---------------- 第 11 章 模板 ----------------
    "l37": [
        {
            "q": "写一个函数模板 my_max，能比较 int、double、string。",
            "hint": "typename T 作为类型参数。",
            "answer": r"""#include <iostream>
#include <string>

template <typename T>
T my_max(const T& a, const T& b) { return a > b ? a : b; }

int main() {
    std::cout << my_max(3, 7) << '\n';
    std::cout << my_max(2.5, 1.5) << '\n';
    std::cout << my_max(std::string("apple"), std::string("pear")) << '\n';
    return 0;
}""",
            "note": "两个实参类型必须一致，否则要显式写 my_max<double>(3, 5)。",
        },
    ],
    "l38": [
        {
            "q": "写一个类模板 Box<T>，能存一个值并提供 get/set。",
            "hint": "类模板使用时必须显式指定类型。",
            "answer": r"""#include <iostream>
#include <string>

template <typename T>
class Box {
public:
    explicit Box(T v) : v_(v) {}
    T get() const { return v_; }
    void set(const T& v) { v_ = v; }
private:
    T v_;
};

int main() {
    Box<int> a(42);
    Box<std::string> b("hi");
    std::cout << a.get() << ' ' << b.get() << '\n';
    a.set(7);
    std::cout << a.get() << '\n';
    return 0;
}""",
            "note": "Box<int> 和 Box<string> 是两个完全不同的类型，互相不能赋值。",
        },
    ],
    "l39": [
        {
            "q": "用 if constexpr 写一个函数，对整数输出“整数”，对其他类型输出“其他”。",
            "hint": "std::is_integral_v<T> 是编译期布尔值。",
            "answer": r"""#include <iostream>
#include <type_traits>

template <typename T>
void describe(const T& v) {
    if constexpr (std::is_integral_v<T>) {
        std::cout << "整数 " << v << '\n';
    } else {
        std::cout << "其他 " << v << '\n';
    }
}

int main() {
    describe(42);
    describe(3.14);
    describe(std::string("hi"));
    return 0;
}""",
            "note": "if constexpr 的分支在编译期就选定，没选中的分支不会实例化。",
        },
    ],
    # ---------------- 第 12 章 C++20 ----------------
    "l40": [
        {
            "q": "定义一个 concept，要求类型支持 + 且结果可以比较大小，并用它约束一个函数。",
            "hint": "requires 表达式里写 { a + b } -> ...。",
            "answer": r"""#include <concepts>
#include <iostream>

template <typename T>
concept Addable = requires(T a, T b) { { a + b } -> std::convertible_to<T>; };

template <Addable T>
T add(T a, T b) { return a + b; }

int main() {
    std::cout << add(1, 2) << '\n';
    std::cout << add(1.5, 2.5) << '\n';
    return 0;
}""",
            "note": "传一个不支持 + 的类型时，报错会直接说约束不满足，而不是几百行模板展开。",
        },
    ],
    "l41": [
        {
            "q": "用 ranges 取出 1~20 里的偶数平方的前 5 个。",
            "hint": "iota | filter | transform | take。",
            "answer": r"""#include <iostream>
#include <ranges>

int main() {
    auto r = std::views::iota(1, 21)
           | std::views::filter([](int n){ return n % 2 == 0; })
           | std::views::transform([](int n){ return n * n; })
           | std::views::take(5);

    for (int x : r) std::cout << x << ' ';
    std::cout << '\n';        // 4 16 36 64 100
    return 0;
}""",
            "note": "整个管道是惰性的，不会生成中间 vector。",
        },
    ],
    "l42": [
        {
            "q": "写一个函数用 std::span 接收任意连续容器并求和。",
            "hint": "span<const double> 可以接 vector、数组。",
            "answer": r"""#include <iostream>
#include <span>
#include <vector>

double sum(std::span<const double> data) {
    double s = 0;
    for (double v : data) s += v;
    return s;
}

int main() {
    double arr[] = {1.0, 2.0};
    std::vector<double> v{3.0, 4.0};
    std::cout << sum(arr) << ' ' << sum(v) << '\n';
    return 0;
}""",
            "note": "span 只存指针和长度，零拷贝；注意被引用的容器要活得比它久。",
        },
    ],
    "l43": [
        {
            "q": "用默认的 <=> 让一个结构体支持全部六个比较运算符。",
            "hint": "auto operator<=>(const T&) const = default;",
            "answer": r"""#include <iostream>

struct Version {
    int major, minor, patch;
    auto operator<=>(const Version&) const = default;
};

int main() {
    Version a{1, 2, 0}, b{1, 10, 0};
    std::cout << (a < b) << (a == b) << '\n';   // 1 0
    return 0;
}""",
            "note": "默认实现按成员声明顺序依次比较，所以成员顺序就是比较优先级。",
        },
    ],
    # ---------------- 第 13 章 工程 ----------------
    "l44": [
        {
            "q": "写一个函数，找不到元素时返回 optional，调用方用 if 判断。",
            "hint": "std::optional<T>，返回 std::nullopt 表示没有。",
            "answer": r"""#include <iostream>
#include <optional>
#include <string>

std::optional<int> findIndex(const std::string& s, char c) {
    auto p = s.find(c);
    if (p == std::string::npos) return std::nullopt;
    return static_cast<int>(p);
}

int main() {
    if (auto i = findIndex("hello", 'l')) std::cout << "位置 " << *i << '\n';
    if (!findIndex("hello", 'z')) std::cout << "没找到\n";
    return 0;
}""",
            "note": "optional 表达“可能没有”，不需要用 -1 这种魔法值。",
        },
    ],
    "l45": [
        {
            "q": "写一个 RAII 类，构造时打印进入作用域，析构时打印离开，用来观察代码块。",
            "hint": "就是构造/析构函数的应用。",
            "answer": r"""#include <iostream>

class ScopedLog {
public:
    explicit ScopedLog(const char* name) : n_(name) { std::cout << "进入 " << n_ << '\n'; }
    ~ScopedLog() { std::cout << "离开 " << n_ << '\n'; }
private:
    const char* n_;
};

int main() {
    ScopedLog a("main");
    { ScopedLog b("block"); }
    std::cout << "中间\n";
    return 0;
}""",
            "note": "即使中间抛异常，析构照样执行，这就是 RAII 的可靠性来源。",
        },
    ],
    "l46": [
        {
            "q": "给一个加法函数写三条断言测试。",
            "hint": "assert(条件)，失败会打印文件名和行号。",
            "answer": r"""#include <cassert>
#include <iostream>

int add(int a, int b) { return a + b; }

void test() {
    assert(add(1, 2) == 3);
    assert(add(-1, 1) == 0);
    assert(add(0, 0) == 0);
}

int main() {
    test();
    std::cout << "全部测试通过\n";
    return 0;
}""",
            "note": "N 是 NDEBUG 宏时 assert 会被移除，所以别在 assert 里写有副作用的代码。",
        },
    ],
    # ---------------- 第 14 章 项目 ----------------
    "l47": [
        {
            "q": "给记账程序加一个字段 currency（货币单位），默认 \"CNY\"，并让明细表显示它。",
            "hint": "给结构体加成员，记得在初始化时给默认值。",
            "answer": r"""#include <iostream>
#include <string>

struct Transaction {
    std::string date;
    std::string category;
    double      amount = 0;
    std::string note;
    std::string currency = "CNY";
};

int main() {
    Transaction t{"2024-05-01", "餐饮", -32.5, "午餐"};
    std::cout << t.date << ' ' << t.category << ' '
              << t.amount << ' ' << t.currency << '\n';
    return 0;
}""",
            "note": "新增字段要同步改存盘和读盘逻辑，否则数据会错位——这是最常见的回归。",
        },
    ],
    "l48": [
        {
            "q": "实现一个函数，找出金额最大的一笔记录。",
            "hint": "用 max_element 配 lambda 比较器。",
            "answer": r"""#include <algorithm>
#include <iostream>
#include <vector>

struct Transaction { std::string date; double amount = 0; };

int main() {
    std::vector<Transaction> v{
        {"2024-05-01", -32.5},
        {"2024-05-02", 8000},
        {"2024-05-03", -120},
    };
    auto it = std::max_element(v.begin(), v.end(),
        [](const auto& a, const auto& b) { return a.amount < b.amount; });
    std::cout << it->date << " " << it->amount << '\n';
    return 0;
}""",
            "note": "max_element 返回迭代器，用之前要确认容器非空。",
        },
    ],
    "l49": [
        {
            "q": "把结构体写成 CSV 行并读回来，验证能还原。",
            "hint": "用 ostringstream 拼行，用 istringstream 拆行。",
            "answer": r"""#include <iostream>
#include <sstream>
#include <string>

int main() {
    // 写
    std::ostringstream os;
    os << "2024-05-01" << ',' << "餐饮" << ',' << -32.5 << ',' << "午餐";
    std::string line = os.str();
    std::cout << "CSV: " << line << '\n';

    // 读
    std::istringstream is(line);
    std::string date, cat, note, amt;
    std::getline(is, date, ',');
    std::getline(is, cat, ',');
    std::getline(is, amt, ',');
    std::getline(is, note, ',');
    std::cout << "还原: " << date << '|' << cat << '|'
              << std::stod(amt) << '|' << note << '\n';
    return 0;
}""",
            "note": "备注里含逗号会破坏这个格式，真实项目要么转义，要么换格式。",
        },
    ],
    "l50": [
        {
            "q": "给菜单加一个“撤销上一次删除”的功能，用栈保存被删的记录。",
            "hint": "std::vector 当栈用，push_back 和 pop_back。",
            "answer": r"""#include <iostream>
#include <string>
#include <vector>

int main() {
    std::vector<std::string> items{"吃饭", "打车", "工资"};
    std::vector<std::string> undo;          // 撤销栈

    // 删除最后一条
    undo.push_back(items.back());
    items.pop_back();
    std::cout << "删除后剩 " << items.size() << " 条\n";

    // 撤销
    items.push_back(undo.back());
    undo.pop_back();
    std::cout << "撤销后剩 " << items.size() << " 条\n";
    return 0;
}""",
            "note": "栈的语义正好匹配“撤销”：最后删的最先恢复。",
        },
    ],
}
