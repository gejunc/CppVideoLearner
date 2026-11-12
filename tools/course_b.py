# -*- coding: utf-8 -*-
"""C++ 视频课程内容 —— 第 5 ~ 8 章。"""

CHAPTERS_B = [
    # ================= 第 5 章 =================
    {
        "id": "ch5",
        "title": "第 5 章 · 复合类型与内存",
        "desc": "数组、字符串、指针、引用——C++ 的分水岭，也是面试和事故的重灾区。",
        "lessons": [
            {
                "id": "l13",
                "title": "数组与 std::array",
                "minutes": 4,
                "tags": ["数组", "std::array", "越界"],
                "pages": [
                    {
                        "kind": "cover",
                        "title": "数组：一段连续的内存",
                        "subtitle": "原生数组 vs std::array",
                        "narration": "数组是最基础的数据结构：一段连续的内存，元素类型相同。C++ 有原生数组和 std::array 两种，后者是现代 C++ 的首选。",
                    },
                    {
                        "kind": "code",
                        "title": "原生数组",
                        "code": """int  a[5];                    // 未初始化，值不确定
int  b[5] = {1, 2, 3};        // 其余补 0
int  c[]  = {1, 2, 3, 4};     // 长度自动推导为 4

int n = sizeof(c) / sizeof(c[0]);   // 4

// 二维数组
int grid[3][4] = {};
grid[1][2] = 7;

// 数组名会退化成指针
void f(int* p, int len);
f(c, n);""",
                        "narration": "原生数组的长度在编译期确定。部分初始化时剩下的元素自动补零。求长度用 sizeof 相除，但注意这个技巧只在同一个作用域里有效，数组一旦传进函数就退化成指针，sizeof 拿到的只是指针大小。用二维数组时记住它是行优先存储的。",
                    },
                    {
                        "kind": "code",
                        "title": "std::array：带长度信息的数组",
                        "code": """#include <array>

std::array<int, 5> a{1, 2, 3, 4, 5};

a.size();          // 5，永远知道自己的长度
a.at(10);          // 抛异常，安全
a[10];             // 不检查，未定义行为
a.front(); a.back();

for (int v : a) std::cout << v << ' ';

// 传参时长度信息不丢失
void dump(const std::array<int, 5>& arr);""",
                        "narration": "std::array 就是原生数组加了一层封装，性能完全相同，零额外开销，但它知道自己的长度。size 永远准确，at 会做边界检查，越界抛异常，方括号不检查。传参时长度信息跟着类型走，不会退化。除非要和 C 接口交互，否则优先用 std::array。",
                    },
                    {
                        "kind": "code",
                        "title": "越界是未定义行为",
                        "code": """int a[5] = {0};
a[5]  = 1;      // 越界写：UB，可能不报错，可能改坏别的变量
a[-1] = 1;      // 同样 UB

// 越界的可怕之处：它常常"看起来正常"
// 直到某次编译优化或换个环境才炸

// 排查工具
// - 编译加 -fsanitize=address
// - 用 std::array::at 或 vector::at
// - 用 .at() 在 debug 构建里""",
                        "narration": "C++ 的方括号不检查边界，越界是未定义行为。最坑的是它常常看起来正常，把旁边变量的内存悄悄改掉，等到另一个地方出错你根本找不到源头。排查靠地址检查器，编译时加 sanitize 参数；日常则尽量用 at 或者范围 for。",
                    },
                    {
                        "kind": "recap",
                        "title": "本课回顾",
                        "items": [
                            "原生数组会退化成指针，长度会丢",
                            "std::array 零开销且带长度，优先级更高",
                            "越界是 UB，用 at 或 sanitize 兜底",
                        ],
                        "narration": "下一课讲字符串，它是数组最常用的特例，也是性能陷阱最多的地方。",
                    },
                ],
            },
            {
                "id": "l14",
                "title": "std::string 与字符串处理",
                "minutes": 4,
                "tags": ["string", "getline", "string_view"],
                "pages": [
                    {
                        "kind": "cover",
                        "title": "字符串",
                        "subtitle": "std::string 的正确打开方式",
                        "narration": "C 风格字符串是字符数组加一个零结尾，一不留神就越界。std::string 把它包起来，自动管理内存。这一课讲清楚日常该用哪些操作。",
                    },
                    {
                        "kind": "code",
                        "title": "创建、拼接、比较",
                        "code": """#include <string>
using std::string;

string s1 = "hello";
string s2("world");
string s3(5, 'x');        // "xxxxx"
string s4 = s1 + " " + s2;

s1 += "!";                // 原地追加
s1.size();  s1.empty();   // 长度 / 是否为空
s1[0];                    // 'h'，不检查
s1.at(0);                 // 检查边界

if (s1 == s2) { }         // 内容比较，不是地址
if (s1 < s2)  { }         // 字典序""",
                        "narration": "string 支持加号拼接、加等原地追加，等号比较的是内容而不是地址，这点和 C 风格字符数组完全不同。长度用 size 或 length，都行。方括号不检查越界，at 会检查，日常读单字符用方括号，位置可能不可靠时用 at。",
                    },
                    {
                        "kind": "code",
                        "title": "查找、截取、转换",
                        "code": """string s = "hello world";

s.find("world");        // 6，找不到返回 npos
s.find('x');            // string::npos
s.substr(0, 5);          // "hello"
s.replace(0, 5, "hi");   // "hi world"

s.c_str();               // 转成 const char*，给 C 接口用

// 字符串和数字互转
int    n = std::stoi("42");
double d = std::stod("3.14");
string t = std::to_string(42);

// 读整行（含空格）
std::getline(std::cin, s);""",
                        "narration": "find 找不到时返回 npos，注意它是个很大的无符号数，所以要判断等于 npos 而不是小于零。substr 从指定位置取指定长度。和数字互转用 stoi 系列和 to_string。读带空格的一整行必须用 getline，直接 cin 会在空格处截断。",
                    },
                    {
                        "kind": "bullets",
                        "title": "性能与陷阱",
                        "items": [
                            ("小字符串优化", "短字符串存在栈上，不分配堆内存，所以别怕用 string"),
                            ("s += 比 s = s + 好", "原地追加避免临时对象"),
                            ("c_str() 指针会失效", "string 一旦修改或扩容，之前拿到的指针就悬空了"),
                            ("C++17 用 string_view", "只读传递时零拷贝，但别让它指向已销毁的 string"),
                        ],
                        "narration": "四个要点。短字符串有优化，存在栈上不分配堆，放心用。拼接用加等，比重新赋值少一次临时对象。c_str 拿到的指针在字符串修改后会失效，别存着。C++17 引入的 string_view 在只读传参时可以零拷贝，但它不拥有内存，指向的源必须活得比它久。",
                    },
                    {
                        "kind": "recap",
                        "title": "本课回顾",
                        "items": [
                            "string 比较的是内容，find 失败返回 npos",
                            "读整行用 getline",
                            "string_view 零拷贝但不拥有内存",
                        ],
                        "narration": "字符串这一课的核心是：用 string 而不是字符数组，用 getline 读整行，用 string_view 做只读参数。下一课进入 C++ 最硬核的部分：指针。",
                    },
                ],
            },
            {
                "id": "l15",
                "title": "指针：地址、解引用与空指针",
                "minutes": 5,
                "tags": ["指针", "nullptr", "内存"],
                "pages": [
                    {
                        "kind": "cover",
                        "title": "指针",
                        "subtitle": "变量住在哪，以及怎么找到它",
                        "narration": "指针是 C++ 最让人头疼也最有威力的东西。它本身只是一个整数，存的是另一个变量的地址。理解了地址和解引用的关系，指针就不神秘了。",
                    },
                    {
                        "kind": "code",
                        "title": "取地址与解引用",
                        "code": """int  x = 42;
int* p = &x;      // p 保存 x 的地址

std::cout << p;    // 0x7ffd...  地址
std::cout << *p;   // 42         解引用

*p = 99;           // 通过指针改 x
std::cout << x;    // 99

int** pp = &p;     // 指向指针的指针
std::cout << **pp; // 99""",
                        "narration": "和号取地址，星号解引用，这两个符号在声明和表达式中含义不同，这是初学者混乱的根源。p 存的是地址，星号 p 是这个地址上的值。指针也有自己的地址，所以可以有多级指针，但要记住多一层就多一份复杂度。",
                    },
                    {
                        "kind": "code",
                        "title": "空指针：只用 nullptr",
                        "code": """int* p = nullptr;     // 正确
// int* q = NULL;      // 能编但别用，它是 0 的宏
// int* r = 0;         // 同上

if (p) { }            // 判空，比 p != nullptr 简洁

*p = 1;               // 危险：空指针解引用会崩溃

// 好习惯：定义时初始化，用前判空
void f(int* p) {
    if (!p) return;
    *p = 1;
}""",
                        "narration": "空指针统一用 nullptr，它是真正的指针类型，不会被当成整数重载。自定义 NULL 宏和直接写零都有隐患。指针最大的风险就是空和悬空，所以两个习惯：定义时立刻初始化，使用前必须判空。",
                    },
                    {
                        "kind": "code",
                        "title": "指针与数组的关系",
                        "code": """int a[5] = {10, 20, 30, 40, 50};
int* p = a;             // 数组名退化成首元素地址

p[2];        // 30，等价于 *(p + 2)
*(p + 2);    // 30
p++;         // 移到下一个元素，地址 +4（int 大小）

// 相减得到距离
int* q = &a[4];
q - p;       // 元素个数差

// 一维遍历
for (int* it = a; it != a + 5; ++it)
    std::cout << *it << ' ';""",
                        "narration": "数组名可以当指针用，指向第一个元素。指针算术按元素大小步进，int 指针加一就是前进四个字节。所以 p 加二和 p 方括号二等价。指针相减得到的是元素个数差，不是字节数。这种遍历现在应该用范围 for，但读老代码你得认得出来。",
                    },
                    {
                        "kind": "bullets",
                        "title": "指针的三大风险",
                        "items": [
                            ("空指针", "解引用直接崩溃，用前判空或用引用代替"),
                            ("悬空指针", "指向的对象已经销毁，内存可能被复用"),
                            ("野指针", "未初始化，指向随机地址，比崩溃更可怕"),
                            ("越界指针", "指针算术越界，同样是 UB"),
                        ],
                        "narration": "指针的风险集中在生命周期上：空指针、悬空指针、野指针、越界。现代 C++ 的应对策略是尽量别用裸指针管理所有权，改用智能指针，下一章会讲。现在先记住：裸指针只用来观察，不用来拥有。",
                    },
                    {
                        "kind": "recap",
                        "title": "本课回顾",
                        "items": [
                            "& 取地址，* 解引用，指针算术按元素步进",
                            "空指针只用 nullptr",
                            "裸指针用于观察，不要用来管理所有权",
                        ],
                        "narration": "指针这一课信息量大，建议回去把代码敲一遍。下一课讲引用，它比指针安全得多，是 C++ 的日常主力。",
                    },
                ],
            },
            {
                "id": "l16",
                "title": "引用：别名与生命周期",
                "minutes": 4,
                "tags": ["引用", "const引用", "悬空引用"],
                "pages": [
                    {
                        "kind": "cover",
                        "title": "引用",
                        "subtitle": "必须绑定，终生不变",
                        "narration": "引用是给别人起个别名，从此这个名字和原名指向同一块内存。它比指针更安全，因为有两条铁律：必须初始化，且不能改绑。",
                    },
                    {
                        "kind": "code",
                        "title": "基本用法",
                        "code": """int  x = 10;
int& r = x;        // r 是 x 的别名
r = 20;            // x 也变成 20

// int& bad;       // 错：引用必须初始化
// int& bad2 = 1;  // 错：不能绑定字面量（非 const 引用）

const int& cr = 42;   // 对：常量引用能绑字面量
// cr = 1;            // 错：不能通过常量引用修改

int* p = &r;       // 引用取地址就是取原变量地址
// int& r2 = &x;   // 错：类型不匹配""",
                        "narration": "引用定义时必须绑定，而且绑了就换不了。非 const 引用不能绑字面量，const 引用可以，编译器会为它创建一个临时对象。对引用取地址得到的是原变量的地址，因为引用本身不占存储，它只是个名字。",
                    },
                    {
                        "kind": "code",
                        "title": "引用返回值与悬空引用",
                        "code": """// 危险：返回局部变量的引用
int& bad() {
    int local = 1;
    return local;        // 函数结束，local 已销毁
}

// 安全：返回静态或成员变量的引用
int& good() {
    static int v = 0;
    return v;
}

// 安全：返回引用参数
int& pick(int& a, int& b) {
    return a > b ? a : b;
}""",
                        "narration": "返回引用要非常小心。返回局部变量的引用是典型的悬空引用，函数一结束那块栈内存就失效了，之后读它得到什么全看运气。能返回引用的安全场景只有三种：静态变量、成员变量、通过参数传进来的引用。",
                    },
                    {
                        "kind": "bullets",
                        "title": "引用的实战价值",
                        "items": [
                            ("参数", "const T& 零拷贝只读传参，T& 原地修改"),
                            ("范围 for", "const auto& 遍历容器，不复制元素"),
                            ("返回值", "避免大对象拷贝，但要注意生命周期"),
                            ("别名", "给长表达式起短名字，让代码更好读"),
                        ],
                        "narration": "引用的实战价值就在于这四件事：参数、范围 for、返回值、别名。日常写代码你用得最多的就是 const 引用传参。记住一句话：引用不能为空，所以能用引用就不用指针。",
                    },
                    {
                        "kind": "recap",
                        "title": "本课回顾",
                        "items": [
                            "引用必须初始化，不能改绑",
                            "const 引用能绑定字面量和临时对象",
                            "绝不返回局部变量的引用",
                        ],
                        "narration": "到这里内存基础就讲完了。下一章进入面向对象，C++ 真正区别于 C 的地方。",
                    },
                ],
            },
        ],
    },
    # ================= 第 6 章 =================
    {
        "id": "ch6",
        "title": "第 6 章 · 面向对象",
        "desc": "类、对象、封装、继承——用类型去组织复杂系统。",
        "lessons": [
            {
                "id": "l17",
                "title": "类与对象：从结构体到类型",
                "minutes": 4,
                "tags": ["class", "struct", "成员"],
                "pages": [
                    {
                        "kind": "cover",
                        "title": "类与对象",
                        "subtitle": "把数据和行为绑在一起",
                        "narration": "类是自定义类型，对象是这个类型的变量。相比 C 的结构体，类多了函数成员和访问控制，于是数据和操作数据的方法可以绑在一起，这是抽象的第一步。",
                    },
                    {
                        "kind": "code",
                        "title": "定义一个类",
                        "code": """class Point {
public:                    // 公开接口
    void setX(int x) { x_ = x; }
    int  getX() const { return x_; }

private:                   // 私有数据
    int x_ = 0;            // 命名习惯：成员加下划线
    int y_ = 0;
};

int main() {
    Point p;               // 栈上对象，自动管理
    p.setX(3);
    std::cout << p.getX();
}""",
                        "narration": "class 定义了一个新类型。public 部分是给外面用的接口，private 部分是内部数据，外面碰不到。成员变量加下划线是常见命名约定，一眼能看出它不是局部变量。对象放栈上，离开作用域自动销毁，不需要手动释放。",
                    },
                    {
                        "kind": "code",
                        "title": "class 与 struct 的区别",
                        "code": """struct Vec { int x; int y; };   // 默认 public
class  Vec2 { int x; int y; };  // 默认 private

// 惯例：
// struct  → 简单数据聚合，成员都公开
// class   → 有不变式需要维护，有私有成员

struct Config {
    std::string host;
    int         port = 8080;
};

Config c{"localhost", 3000};""",
                        "narration": "class 和 struct 唯一的语法区别是默认访问级别：struct 默认公开，class 默认私有。惯例上，纯数据聚合用 struct，需要维护内部不变式的用 class。C++ 里 struct 也能有函数成员，所以别把它理解成 C 的结构体。",
                    },
                    {
                        "kind": "bullets",
                        "title": "面向对象四个支柱",
                        "items": [
                            ("封装", "数据私有，只通过接口访问，内部实现可以随时换"),
                            ("抽象", "类的名字和接口表达概念，隐藏细节"),
                            ("继承", "复用已有类型，表达 is-a 关系"),
                            ("多态", "同一个接口，不同实现，运行时决定"),
                        ],
                        "narration": "四个支柱：封装，让内部实现可替换；抽象，用名字表达概念；继承，表达 is a 关系；多态，一个接口多种行为。前两个在类里就体现出来了，后两个需要下一课展开。",
                    },
                    {
                        "kind": "recap",
                        "title": "本课回顾",
                        "items": [
                            "class 默认私有，struct 默认公开",
                            "成员变量加下划线，接口保持公开",
                            "封装的意义是让实现可以替换",
                        ],
                        "narration": "下一课讲对象的生老病死：构造函数和析构函数。这是 C++ 资源管理的核心。",
                    },
                ],
            },
            {
                "id": "l18",
                "title": "构造与析构：对象的出生与死亡",
                "minutes": 5,
                "tags": ["构造函数", "析构函数", "RAII"],
                "pages": [
                    {
                        "kind": "cover",
                        "title": "生命周期",
                        "subtitle": "构造函数 · 析构函数 · RAII",
                        "narration": "C++ 最强大的设计之一就是对象的生命周期是确定的：构造时初始化，离开作用域必定析构。这个特性推出了一整套资源管理哲学，叫 RAII。",
                    },
                    {
                        "kind": "code",
                        "title": "构造函数的几种形式",
                        "code": """class Buffer {
public:
    Buffer() : data_(nullptr), size_(0) {}        // 默认构造
    Buffer(int n) : data_(new char[n]), size_(n) {}  // 带参
    Buffer(const Buffer& o)                       // 拷贝构造
        : data_(new char[o.size_]), size_(o.size_) {
        std::copy(o.data_, o.data_ + size_, data_);
    }
    ~Buffer() { delete[] data_; }                 // 析构

private:
    char* data_;
    int   size_;
};""",
                        "narration": "构造函数和类同名，没有返回类型，用初始化列表给成员赋值，这比在花括号里赋值更高效，因为少了默认构造再赋值的一步。拷贝构造函数参数必须传引用，否则会无限递归。析构函数前面加波浪号，负责释放资源。",
                    },
                    {
                        "kind": "code",
                        "title": "初始化列表的顺序陷阱",
                        "code": """class Bad {
public:
    Bad(int n) : size_(n), data_(new int[n]) {}
private:
    char* data_;   // 先声明
    int   size_;   // 后声明
};

// 实际初始化顺序：data_ 先于 size_！
// 所以 data_(new int[n]) 用的 n 是参数，没问题；
// 但如果写成 data_(new int[size_])，size_ 还是未初始化的！

// 结论：初始化列表顺序应与声明顺序一致
// 编译加 -Wreorder 会警告""",
                        "narration": "初始化列表的执行顺序由成员的声明顺序决定，跟你在列表里写的顺序无关。所以如果 data 声明在前，它会先初始化，这时用到一个还没初始化的 size 就完蛋了。经验法则：初始化列表顺序和声明顺序保持一致，编译器有 reorder 警告就打开它。",
                    },
                    {
                        "kind": "code",
                        "title": "RAII：让生命周期替你干活",
                        "code": """// 手动管理：异常或提前 return 就会泄漏
void risky() {
    FILE* f = fopen("a.txt", "r");
    if (something) return;      // 忘了 fclose！
    fclose(f);
}

// RAII：把资源放进对象，析构自动释放
class File {
public:
    explicit File(const char* name) : f_(fopen(name, "r")) {}
    ~File() { if (f_) fclose(f_); }
private:
    FILE* f_;
};

void safe() {
    File f("a.txt");     // 离开作用域必定关闭
}""",
                        "narration": "看这两个版本。手动管理的版本，只要中间有一次提前 return 或者抛异常，fclose 就被跳过了，资源泄漏。RAII 的版本把资源封装成对象，析构函数里释放，无论怎么离开作用域都会执行。这就是为什么 C++ 里你几乎不需要手动 free，标准库的 vector、string、智能指针全都是这个模式。",
                    },
                    {
                        "kind": "bullets",
                        "title": "规则",
                        "items": [
                            ("资源进对象", "谁申请谁释放，用析构函数保证"),
                            ("explicit 防隐式转换", "单参数构造函数默认加 explicit"),
                            ("三法则", "定义了析构、拷贝构造、拷贝赋值中的任何一个，通常三个都要定义"),
                            ("五法则", "C++11 之后再算上移动构造和移动赋值"),
                        ],
                        "narration": "四条规则：资源交给对象管；单参数构造函数加 explicit，防止意外的隐式转换；如果你手写了析构、拷贝构造、拷贝赋值中的任意一个，通常三个都得写，这是三法则；C++11 之后还要考虑移动构造和移动赋值，合称五法则。当然，更好的办法是不写裸指针，用智能指针，让编译器生成这些函数。",
                    },
                    {
                        "kind": "recap",
                        "title": "本课回顾",
                        "items": [
                            "构造函数初始化列表顺序跟声明顺序走",
                            "析构函数保证离开作用域时释放资源",
                            "RAII 是 C++ 资源管理的根本方法",
                        ],
                        "narration": "这是全课最重要的一课之一，RAII 的思想会贯穿后面所有内容。",
                    },
                ],
            },
            {
                "id": "l19",
                "title": "封装、const 成员与 this 指针",
                "minutes": 4,
                "tags": ["const成员", "this", "封装"],
                "pages": [
                    {
                        "kind": "cover",
                        "title": "封装与 const 成员函数",
                        "subtitle": "this · const · static",
                        "narration": "这一课讲三个细节：this 指针是什么，const 成员函数为什么重要，以及静态成员和普通成员的区别。",
                    },
                    {
                        "kind": "code",
                        "title": "this 与返回自身",
                        "code": """class Counter {
public:
    Counter& inc() {
        ++count_;        // 等价于 ++this->count_
        return *this;    // 返回自己，支持链式调用
    }
    Counter& add(int n) {
        count_ += n;
        return *this;
    }
private:
    int count_ = 0;
};

Counter c;
c.inc().add(5).inc();   // 链式调用""",
                        "narration": "this 是成员函数里隐含的指针，指向当前对象。访问成员变量时编译器会自动加 this 箭头。返回星号 this 可以让函数支持链式调用，这就是流式接口的实现方式，cout 连续输出就是用这个。",
                    },
                    {
                        "kind": "code",
                        "title": "const 成员函数",
                        "code": """class Account {
public:
    int balance() const { return balance_; }   // 承诺不修改
    void deposit(int n)   { balance_ += n; }   // 会修改

private:
    int balance_ = 0;
};

const Account a;
a.balance();     // 可以：const 对象只能调 const 成员函数
// a.deposit(1); // 错：不能修改 const 对象

// const 在重载中也是签名的一部分
int&       get();
const int& get() const;""",
                        "narration": "成员函数后面加 const，是承诺这个函数不修改对象状态。const 对象只能调用 const 成员函数，反过来非 const 对象两个都能调。所以凡是逻辑上只读的成员函数，都应该加 const，否则你的类就没法被 const 引用使用。const 也参与重载，可以写两个版本分别返回可写和只读引用。",
                    },
                    {
                        "kind": "code",
                        "title": "static 成员",
                        "code": """class Id {
public:
    Id() : id_(++counter_) {}
    static int count() { return counter_; }   // 属于类，不属于对象
private:
    int id_;
    static int counter_;   // 类内声明
};

int Id::counter_ = 0;      // 类外定义（C++17 可用 inline static 简化）

// 静态成员函数里没有 this，不能访问非静态成员""",
                        "narration": "静态成员属于类本身，所有对象共享一份。静态成员函数里没有 this，所以不能访问普通成员变量，它只能访问静态成员。C++17 之后可以用 inline static 直接在类内定义，省掉类外定义那一行。静态成员常用来做计数器、单例、常量表。",
                    },
                    {
                        "kind": "recap",
                        "title": "本课回顾",
                        "items": [
                            "this 指向当前对象，返回 *this 支持链式调用",
                            "只读成员函数一定加 const",
                            "static 成员属于类，静态函数里没有 this",
                        ],
                        "narration": "记住一条最实用的：所有只读的成员函数都加 const，这个习惯能让你少写一堆错误。下一课讲继承。",
                    },
                ],
            },
            {
                "id": "l20",
                "title": "继承与 is-a 关系",
                "minutes": 4,
                "tags": ["继承", "访问控制", "构造顺序"],
                "pages": [
                    {
                        "kind": "cover",
                        "title": "继承",
                        "subtitle": "复用与 is-a",
                        "narration": "继承让一个类型获得另一个类型的成员。它表达的是 is a 关系：狗是一种动物。用对了很省事，用错了会变成继承地狱。",
                    },
                    {
                        "kind": "code",
                        "title": "基本写法",
                        "code": """class Animal {
public:
    void eat() { std::cout << "eating\\n"; }
protected:
    int age_ = 0;       // 子类可以访问
private:
    int id_ = 0;        // 子类也不能访问
};

class Dog : public Animal {     // public 继承最常见
public:
    void bark() { std::cout << "woof\\n"; }
};

Dog d;
d.eat();     // 继承来的
d.bark();""",
                        "narration": "冒号后面写继承方式和父类。public 继承表示 is a，最常用。protected 成员子类能访问但外面不能，private 成员谁都别想碰。子类对象里包含一个完整的父类子对象，所以父类的东西它都有。",
                    },
                    {
                        "kind": "code",
                        "title": "构造与析构的顺序",
                        "code": """class Base {
public:
    Base()  { std::cout << "Base 构造\\n"; }
    ~Base() { std::cout << "Base 析构\\n"; }
};

class Derived : public Base {
public:
    Derived()  { std::cout << "Derived 构造\\n"; }
    ~Derived() { std::cout << "Derived 析构\\n"; }
};

Derived d;
// 输出顺序：
// Base 构造
// Derived 构造
// Derived 析构
// Base 析构""",
                        "narration": "构造顺序是基类先、派生类后；析构顺序完全相反，派生类先、基类后。这个顺序是必然的，因为派生类初始化时可能要用基类的东西，析构时反过来。初始化列表里如果要显式调用父类构造，写在列表里。",
                    },
                    {
                        "kind": "bullets",
                        "title": "继承的坑",
                        "items": [
                            ("菱形继承", "多继承导致数据重复，用虚继承解决，但通常说明设计有问题"),
                            ("基类析构非虚", "通过基类指针 delete 派生对象会漏掉派生类析构"),
                            ("is-a 误用", "为了复用代码而继承，往往应该用组合"),
                            ("优先组合", "has-a 关系用成员对象，比继承更灵活"),
                        ],
                        "narration": "四个坑。菱形继承会让同一份数据出现两次，虚继承能解决但这通常意味着设计有问题。基类析构函数不是虚的，通过基类指针删除派生对象时，派生类的析构不会执行，这是经典泄漏。最常见的错误是为了复用代码而继承，其实那种情况应该用组合：has a 用成员对象，is a 才用继承。",
                    },
                    {
                        "kind": "recap",
                        "title": "本课回顾",
                        "items": [
                            "public 继承表达 is-a，protected 子类可见",
                            "构造：基类先；析构：派生类先",
                            "优先用组合，继承要有明确的 is-a 理由",
                        ],
                        "narration": "继承本身不难，难的是判断该不该用。记住：has a 用组合，is a 才继承。下一课讲多态，这是继承真正发挥价值的地方。",
                    },
                ],
            },
        ],
    },
    # ================= 第 7 章 =================
    {
        "id": "ch7",
        "title": "第 7 章 · 多态与现代 C++",
        "desc": "虚函数、智能指针、STL、lambda 与移动语义——现代 C++ 的主力武器。",
        "lessons": [
            {
                "id": "l21",
                "title": "虚函数与多态",
                "minutes": 5,
                "tags": ["virtual", "override", "多态"],
                "pages": [
                    {
                        "kind": "cover",
                        "title": "多态",
                        "subtitle": "一个接口，多种实现",
                        "narration": "多态是整个面向对象设计的核心：你调用同一个函数，实际执行的代码由对象的真实类型决定。C++ 用虚函数实现这一点。",
                    },
                    {
                        "kind": "code",
                        "title": "virtual 与 override",
                        "code": """class Shape {
public:
    virtual double area() const = 0;    // 纯虚函数
    virtual ~Shape() = default;         // 虚析构，必须有
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
};""",
                        "narration": "基类里函数前加 virtual 就变成虚函数，等于零的纯虚函数让基类变成抽象类，不能实例化，必须由子类实现。override 关键字让编译器帮你检查是否真的覆盖了基类的虚函数，写错了会报错，很值得加。虚析构函数是必须的，否则通过基类指针删除对象时，子类析构不执行。",
                    },
                    {
                        "kind": "code",
                        "title": "通过基类指针使用多态",
                        "code": """double total(const std::vector<std::unique_ptr<Shape>>& shapes) {
    double sum = 0;
    for (const auto& s : shapes)
        sum += s->area();      // 动态绑定：调用真实类型的方法
    return sum;
}

std::vector<std::unique_ptr<Shape>> v;
v.push_back(std::make_unique<Circle>(1.0));
v.push_back(std::make_unique<Square>(2.0));

std::cout << total(v);   // 3.14 + 4""",
                        "narration": "这段代码是多态的精髓。容器里存的全是基类指针，但调用 area 时，实际执行的是圆或方的版本，这叫动态绑定。它带来巨大的扩展性：加一种新图形，total 函数一行都不用改。注意用 unique 指针管理生命周期，容器里存裸指针容易泄漏。",
                    },
                    {
                        "kind": "code",
                        "title": "虚函数表：多态怎么实现",
                        "code": """// 概念模型（具体实现由编译器决定）
//          +----------------+
// Circle   | vptr --------->+-------------------+
//          | r_             | Circle::area      |
//          +----------------+-------------------+
//
// 每个有虚函数的类有一张虚函数表
// 每个对象里有一个隐藏指针指向它
// 调用虚函数 = 通过 vptr 查表 → 间接调用

// 代价：每个对象多一个指针，每次调用多一次间接跳转
// 所以不需要多态时别加 virtual""",
                        "narration": "虚函数的实现机制是虚函数表：每个有虚函数的类有一张表，记录各虚函数的实际地址，每个对象里藏一个指针指向这张表。调用虚函数时先查表再跳转，所以比普通函数多一次间接开销，对象也多一个指针的空间。这就是为什么只在需要多态的地方才加 virtual。",
                    },
                    {
                        "kind": "bullets",
                        "title": "实践要点",
                        "items": [
                            ("基类析构必须 virtual", "否则 delete 基类指针会漏掉派生类析构"),
                            ("用 override 和 final", "让编译器检查覆盖关系，避免手误"),
                            ("构造析构函数里别调虚函数", "此时动态类型还是基类，不会多态"),
                            ("优先用组合和模板", "多态有运行时开销，编译期多态往往更快"),
                        ],
                        "narration": "四条实践要点：基类析构一定声明为虚函数；覆盖虚函数时写 override，不想被覆盖就写 final；构造函数和析构函数里不要调用虚函数，因为那时对象还没有完全变成派生类型；最后，如果你需要的是性能，模板的编译期多态往往比虚函数更好。",
                    },
                    {
                        "kind": "recap",
                        "title": "本课回顾",
                        "items": [
                            "virtual 启用动态绑定，= 0 是纯虚函数",
                            "基类析构必须 virtual",
                            "多态的价值是新增类型不改旧代码",
                        ],
                        "narration": "多态讲完了，理解虚表你就真正理解 C++ 的对象模型。下一课讲智能指针，这是现代 C++ 最重要的实践。",
                    },
                ],
            },
            {
                "id": "l22",
                "title": "智能指针：unique_ptr 与 shared_ptr",
                "minutes": 5,
                "tags": ["unique_ptr", "shared_ptr", "RAII"],
                "pages": [
                    {
                        "kind": "cover",
                        "title": "智能指针",
                        "subtitle": "让所有权有明确的归属",
                        "narration": "裸指针最大的问题不是难用，而是没人说得清谁该负责释放。智能指针把所有权变成类型系统的一部分，让编译器帮你管内存。这是现代 C++ 最重要的实践，没有之一。",
                    },
                    {
                        "kind": "code",
                        "title": "unique_ptr：独占所有权",
                        "code": """#include <memory>

auto p = std::make_unique<int>(42);     // 推荐写法
std::cout << *p;                        // 42

auto q = std::move(p);                  // 转移所有权，p 变空
// auto r = p;                          // 错：不能拷贝

auto arr = std::make_unique<int[]>(10); // 数组
arr[0] = 1;

// 离开作用域自动 delete，异常安全""",
                        "narration": "unique 指针表示独占所有权，同一时刻只有一个所有者。它不能拷贝，只能移动，移动之后原来的指针变空。用 make_unique 创建，性能和安全都更好。离开作用域自动释放，即使中途抛异常也会释放，这就是 RAII 的威力。默认情况下，需要堆上对象时首先用 unique。",
                    },
                    {
                        "kind": "code",
                        "title": "shared_ptr：共享所有权",
                        "code": """auto a = std::make_shared<int>(42);
{
    auto b = a;          // 引用计数变 2
    std::cout << a.use_count();   // 2
}                        // b 销毁，计数回到 1

std::cout << a.use_count();       // 1

// 循环引用 → 永远不释放，用 weak_ptr 打破
class Node {
public:
    std::shared_ptr<Node> next;
    std::weak_ptr<Node>   prev;   // 不增加计数
};""",
                        "narration": "shared 指针通过引用计数实现共享所有权，每复制一次计数加一，销毁一次减一，减到零才释放对象。它唯一的经典陷阱是循环引用：两个对象互相持有对方，计数永远不归零，内存泄漏。解决办法是把其中一个方向的持有改成 weak 指针，weak 不增加计数。",
                    },
                    {
                        "kind": "bullets",
                        "title": "选择策略",
                        "items": [
                            ("独占资源", "unique_ptr，默认选择"),
                            ("确实共享", "shared_ptr，但要想清楚谁该活得最久"),
                            ("观察而不拥有", "裸指针或引用，函数参数最常用"),
                            ("打破循环", "weak_ptr"),
                        ],
                        "narration": "选择策略：独占就用 unique，这是绝大多数情况；确实需要共享才用 shared，而且要先想清楚生命周期；只是想看看、不负责销毁，就用裸指针或引用做函数参数；遇到循环引用，用 weak 打破。一个常识：能用 unique 就别用 shared，因为 shared 的计数有原子操作开销，而且所有权不清晰。",
                    },
                    {
                        "kind": "recap",
                        "title": "本课回顾",
                        "items": [
                            "make_unique / make_shared 优于 new",
                            "unique 只能移动，shared 靠引用计数",
                            "循环引用用 weak_ptr 打破",
                        ],
                        "narration": "从这一课开始，你的 C++ 代码里不应该再出现裸 new 和 delete。下一课讲 STL，效率提升最明显的一课。",
                    },
                ],
            },
            {
                "id": "l23",
                "title": "STL 容器与迭代器",
                "minutes": 5,
                "tags": ["vector", "map", "迭代器"],
                "pages": [
                    {
                        "kind": "cover",
                        "title": "STL 容器",
                        "subtitle": "别自己造轮子",
                        "narration": "标准模板库提供了一整套数据结构，性能经过极致打磨。这一课讲清楚什么时候该用哪个容器，这是工程能力的分水岭。",
                    },
                    {
                        "kind": "code",
                        "title": "vector：动态数组",
                        "code": """#include <vector>

std::vector<int> v{1, 2, 3};
v.push_back(4);          // 尾部追加，摊销 O(1)
v.emplace_back(5);       // 原地构造，少一次拷贝

v.size();  v.empty();
v[0];     v.at(0);       // at 做边界检查
v.front(); v.back();

v.pop_back();
v.insert(v.begin() + 1, 99);   // 中间插入 O(n)
v.erase(v.begin());

v.reserve(100);          // 预分配，避免反复扩容
v.clear();               // 清空但保留容量""",
                        "narration": "vector 是连续内存的动态数组，尾部增删是摊销常数时间，中间插入删除是线性时间，因为要挪动后面的元素。emplace back 直接在容器里构造对象，比 push back 少一次拷贝。reserve 预分配容量可以避免反复扩容，在知道规模时很有用。clear 只清元素不释放容量。",
                    },
                    {
                        "kind": "code",
                        "title": "map 与 unordered_map",
                        "code": """#include <map>
#include <unordered_map>

std::map<std::string, int> m;      // 红黑树，有序，O(log n)
m["apple"] = 3;
m.at("apple");                      // 不存在会抛异常
m.count("banana");                  // 0 或 1

// 用 [] 会默认插入！查找请用 find
auto it = m.find("apple");
if (it != m.end()) std::cout << it->second;

std::unordered_map<std::string, int> um;  // 哈希表，无序，均摊 O(1)
um.insert({"a", 1});
um.reserve(100);

for (const auto& [k, v] : m)       // C++17 结构化绑定
    std::cout << k << "=" << v << '\\n';""",
                        "narration": "map 基于红黑树，元素有序，操作对数时间；unordered map 基于哈希表，无序，平均常数时间。选择标准很简单：需要按 key 排序遍历就用 map，只要查找快就用 unordered map。一个必须知道的坑：用方括号访问时，如果 key 不存在会自动插入一个默认值，所以纯查找一定要用 find。C++17 的结构化绑定让遍历键值对很舒服。",
                    },
                    {
                        "kind": "bullets",
                        "title": "容器选择速查",
                        "items": [
                            ("vector", "默认选择，随机访问，尾部增删快"),
                            ("deque", "两端增删都要快，但内存不连续"),
                            ("list", "频繁在中间插入删除，但不支持随机访问，缓存不友好"),
                            ("map / set", "需要有序或按 key 查找"),
                            ("unordered_map / set", "只要查找快，不需要顺序"),
                            ("array", "编译期长度固定"),
                        ],
                        "narration": "速查表：vector 是默认选择，除非有明确理由；deque 适合两端操作；list 只在频繁中间插入删除时才考虑，它缓存不友好，实测常常输给 vector；map 和 set 提供有序性；unordered 系列提供最快的查找；长度编译期已知用 array。",
                    },
                    {
                        "kind": "code",
                        "title": "迭代器与失效",
                        "code": """std::vector<int> v{1, 2, 3};

for (auto it = v.begin(); it != v.end(); ++it)
    std::cout << *it << ' ';

// 删除元素的正确姿势
for (auto it = v.begin(); it != v.end(); ) {
    if (*it % 2 == 0) it = v.erase(it);   // erase 返回下一个
    else              ++it;
}

// 危险：一边遍历一边 push_back
// 扩容会让所有迭代器失效 → UB

// 删除-擦除惯用法
v.erase(std::remove_if(v.begin(), v.end(),
        [](int x) { return x % 2 == 0; }), v.end());""",
                        "narration": "迭代器是容器的通用游标。删除元素时要用 erase 的返回值接住下一个有效位置，否则迭代器失效。更危险的是遍历中插入导致扩容，所有迭代器全部失效。删除满足条件的元素，标准写法是删除擦除惯用法：先 remove if 把要留的元素挪到前面，再一次性 erase 尾部。",
                    },
                    {
                        "kind": "recap",
                        "title": "本课回顾",
                        "items": [
                            "vector 是默认选择，注意扩容与迭代器失效",
                            "查找用 find，别用 [] 造成意外插入",
                            "删除-擦除惯用法处理批量删除",
                        ],
                        "narration": "容器选择是工程经验，多写多感受。下一课讲算法、lambda 和移动语义，把现代 C++ 的拼图补齐。",
                    },
                ],
            },
            {
                "id": "l24",
                "title": "算法、lambda 与移动语义",
                "minutes": 5,
                "tags": ["algorithm", "lambda", "std::move"],
                "pages": [
                    {
                        "kind": "cover",
                        "title": "现代 C++ 三件套",
                        "subtitle": "算法 · lambda · 移动语义",
                        "narration": "这一课把三样东西合起来讲，因为它们经常一起出现：标准算法让你少写循环，lambda 让算法能定制，移动语义让大对象传递不再昂贵。",
                    },
                    {
                        "kind": "code",
                        "title": "标准算法：别手写循环",
                        "code": """#include <algorithm>

std::vector<int> v{5, 2, 8, 1, 9};

std::sort(v.begin(), v.end());              // 升序
std::sort(v.begin(), v.end(), std::greater<>{});  // 降序

std::find(v.begin(), v.end(), 8);           // 返回迭代器
std::count_if(v.begin(), v.end(),
              [](int x) { return x > 3; }); // 2

std::any_of(v.begin(), v.end(), [](int x){ return x > 8; });
std::accumulate(v.begin(), v.end(), 0);     // 求和
std::max_element(v.begin(), v.end());       // 最大值""",
                        "narration": "标准算法把常见操作都写好了，经过高度优化。排序、查找、统计、累积、求极值，几乎你能想到的都有。写算法比手写循环好在三点：意图更清楚、不容易写出边界错误、实现通常更快。",
                    },
                    {
                        "kind": "code",
                        "title": "lambda：就地定义的函数",
                        "code": """// [捕获列表](参数) -> 返回类型 { 函数体 }

int threshold = 5;
auto isBig = [threshold](int x) { return x > threshold; };

auto isBig2 = [&](int x) { return x > threshold; };  // 引用捕获

// 捕获方式
// []      不捕获
// [=]     按值捕获所有用到的变量
// [&]     按引用捕获所有用到的变量
// [a, &b] 混用：a 按值，b 按引用

std::sort(v.begin(), v.end(),
          [](int a, int b) { return a > b; });""",
                        "narration": "lambda 的语法是方括号捕获列表、圆括号参数、花括号函数体。捕获列表决定它能看见外面的哪些变量：方括号空表示不捕获，等号按值捕获，和号按引用捕获，也可以混着写。按值捕获是拷贝，安全但有代价；按引用捕获不拷贝，但 lambda 活得比变量久就悬空了。泛型 lambda 可以在参数里写 auto。",
                    },
                    {
                        "kind": "code",
                        "title": "移动语义：把资源搬走而不是复制",
                        "code": """class Buffer {
public:
    Buffer(Buffer&& other) noexcept              // 移动构造
        : data_(other.data_), size_(other.size_) {
        other.data_ = nullptr;                   // 抢走资源
        other.size_ = 0;
    }

    Buffer& operator=(Buffer&& other) noexcept { // 移动赋值
        if (this != &other) {
            delete[] data_;
            data_ = other.data_;
            size_ = other.size_;
            other.data_ = nullptr;
            other.size_ = 0;
        }
        return *this;
    }
private:
    char* data_ = nullptr;
    int   size_ = 0;
};

std::vector<Buffer> v;
v.push_back(Buffer(100));                       // 移动，不拷贝
auto b = std::move(v[0]);                       // 显式移动""",
                        "narration": "移动构造接收一个右值引用，它不是复制资源，而是把指针抢过来，再把源对象置空。这样传递大对象时成本从 O(n) 降到 O(1)。标准库的容器扩容、返回大对象都靠这个。std::move 本身不移动任何东西，它只是把左值强制转换成右值引用，真正干活的是移动构造。注意移动构造要标 noexcept，否则容器扩容时可能退回去用拷贝。",
                    },
                    {
                        "kind": "bullets",
                        "title": "要点",
                        "items": [
                            ("算法优先", "能用标准算法就别手写循环"),
                            ("lambda 按值捕获更安全", "按引用捕获要注意生命周期"),
                            ("move 只是类型转换", "对已 move 的对象只有赋新值和销毁是安全的"),
                            ("返回值天然优化", "返回局部对象无需 std::move，编译器会做 RVO"),
                        ],
                        "narration": "四个要点：优先用标准算法；lambda 按值捕获更安全，按引用捕获要确认生命周期；std::move 只是类型转换，被移动过的对象只剩两种情况安全，赋值和销毁；最后，返回局部变量不需要手动 move，编译器有返回值优化，你手写反而可能阻止优化。",
                    },
                    {
                        "kind": "recap",
                        "title": "本课回顾",
                        "items": [
                            "algorithm 头文件覆盖绝大多数常见操作",
                            "lambda = 捕获列表 + 参数 + 函数体",
                            "移动语义把 O(n) 拷贝变成 O(1) 指针转移",
                        ],
                        "narration": "现代 C++ 的拼图到这里基本齐了。最后两课我们做实战：异常处理、文件读写和一个综合项目。",
                    },
                ],
            },
        ],
    },
    # ================= 第 8 章 =================
    {
        "id": "ch8",
        "title": "第 8 章 · 实战",
        "desc": "异常、文件 IO，以及把前面所有知识拼成一个完整项目。",
        "lessons": [
            {
                "id": "l25",
                "title": "异常处理与文件读写",
                "minutes": 5,
                "tags": ["try", "catch", "fstream"],
                "pages": [
                    {
                        "kind": "cover",
                        "title": "异常与文件",
                        "subtitle": "错误也要有类型",
                        "narration": "程序总会遇到意外：文件不存在、内存不够、输入格式错误。异常机制让错误处理与正常逻辑分开。这一课同时讲文件读写，因为这两件事经常一起出现。",
                    },
                    {
                        "kind": "code",
                        "title": "try / catch / throw",
                        "code": """#include <stdexcept>

double divide(double a, double b) {
    if (b == 0.0)
        throw std::invalid_argument("除数不能为 0");
    return a / b;
}

int main() {
    try {
        std::cout << divide(1, 0);
    } catch (const std::invalid_argument& e) {
        std::cerr << "参数错误: " << e.what() << '\\n';
    } catch (const std::exception& e) {       // 兜底
        std::cerr << "未知错误: " << e.what() << '\\n';
    }
}""",
                        "narration": "throw 抛出一个对象，catch 按类型捕获。捕获时用 const 引用，避免拷贝和切片。标准异常都继承自 exception，what 方法给出描述。catch 的匹配是自上而下的，所以具体类型写前面，exception 兜底写最后。注意别在析构函数里抛异常。",
                    },
                    {
                        "kind": "code",
                        "title": "自定义异常",
                        "code": """class NetworkError : public std::runtime_error {
public:
    explicit NetworkError(const std::string& msg)
        : std::runtime_error(msg) {}
};

// 使用
throw NetworkError("连接超时");

// RAII + 异常：资源一定被释放
void work() {
    std::lock_guard<std::mutex> lock(mtx);  // 析构时解锁
    std::vector<int> v(1000000);            // 异常也会释放
    mayThrow();
}   // 即使抛异常，锁和内存都正确释放""",
                        "narration": "自定义异常继承标准异常，这样所有异常都能用统一方式处理。这里再次体现 RAII 的价值：锁和容器都是自动管理的，即使中途抛异常，栈展开时析构函数照样执行，资源不会泄漏。这也反过来解释了一个原则：不要在析构函数里抛异常，因为栈展开过程中再抛一个异常，程序会直接终止。",
                    },
                    {
                        "kind": "code",
                        "title": "文件读写",
                        "code": """#include <fstream>
#include <sstream>

// 写
std::ofstream out("data.txt");
if (!out) { /* 打开失败 */ }
out << "hello " << 42 << '\\n';
out.close();

// 读：逐行
std::ifstream in("data.txt");
std::string line;
while (std::getline(in, line)) {
    std::cout << line << '\\n';
}

// 读：按字段解析
std::istringstream iss(line);
std::string name;
int score;
iss >> name >> score;

// 一次性读全部
std::string all((std::istreambuf_iterator<char>(in)),
                 std::istreambuf_iterator<char>());""",
                        "narration": "文件流用法和 cin cout 几乎一样。ofstream 写，ifstream 读，打开后一定要检查流对象是否有效，因为文件可能不存在。逐行读用 getline 配 while，这是最稳的模式。要解析一行里的多个字段，用 istringstream 当内存流来切分。注意流对象离开作用域会自动关闭，不需要手动 close。",
                    },
                    {
                        "kind": "recap",
                        "title": "本课回顾",
                        "items": [
                            "throw 抛对象，catch 按类型匹配，用 const 引用",
                            "自定义异常继承 std::runtime_error",
                            "文件打开后必须检查，逐行读用 getline + while",
                        ],
                        "narration": "异常和文件是工程代码的日常。最后一课我们把这些全部拼起来，写一个完整的项目。",
                    },
                ],
            },
            {
                "id": "l26",
                "title": "综合项目：学生成绩管理系统",
                "minutes": 6,
                "tags": ["项目", "综合", "STL"],
                "pages": [
                    {
                        "kind": "cover",
                        "title": "综合项目",
                        "subtitle": "学生成绩管理系统",
                        "narration": "最后一课，我们把二十六课学的东西全部用上，写一个完整的命令行程序：能增删查改学生成绩，能统计平均分，能存盘和读盘。",
                    },
                    {
                        "kind": "bullets",
                        "title": "先设计，再动手",
                        "items": [
                            ("Student", "结构体：学号、姓名、三门课成绩"),
                            ("ScoreBook", "类：用 vector 存所有学生，提供增删查改"),
                            ("文件层", "存盘和读盘，纯文本格式"),
                            ("主循环", "菜单 + 输入分发，处理非法输入"),
                        ],
                        "narration": "写程序先设计。四个部分：Student 用简单结构体聚合数据；ScoreBook 类用 vector 管理集合，维护功能；文件层负责持久化；主循环做菜单和输入分发。分层的好处是每层都很短，改一个功能不用碰别的层。",
                    },
                    {
                        "kind": "code",
                        "title": "数据与核心类",
                        "code": """struct Student {
    std::string id;
    std::string name;
    std::array<double, 3> scores{};

    double average() const {
        return (scores[0] + scores[1] + scores[2]) / 3.0;
    }
};

class ScoreBook {
public:
    void add(const Student& s) { students_.push_back(s); }

    bool remove(const std::string& id) {
        auto it = std::find_if(students_.begin(), students_.end(),
            [&](const Student& s) { return s.id == id; });
        if (it == students_.end()) return false;
        students_.erase(it);
        return true;
    }

    const Student* find(const std::string& id) const {
        auto it = std::find_if(students_.begin(), students_.end(),
            [&](const Student& s) { return s.id == id; });
        return it == students_.end() ? nullptr : &*it;
    }

    double classAverage() const {
        if (students_.empty()) return 0.0;
        double sum = 0;
        for (const auto& s : students_) sum += s.average();
        return sum / students_.size();
    }

    const std::vector<Student>& all() const { return students_; }

private:
    std::vector<Student> students_;
};""",
                        "narration": "Student 用 struct 加 array，平均分直接成员函数算。ScoreBook 提供增删查。注意 remove 和 find 都用 find if 配 lambda 按学号匹配。find 返回指针，找不到返回空指针，这样调用方可以判空，比返回迭代器更不容易误用。每个函数都尽量小，逻辑一眼能读完。",
                    },
                    {
                        "kind": "code",
                        "title": "存盘、读盘与主循环",
                        "code": """void save(const ScoreBook& book, const std::string& path) {
    std::ofstream out(path);
    if (!out) throw std::runtime_error("无法写入 " + path);
    for (const auto& s : book.all())
        out << s.id << ' ' << s.name << ' '
            << s.scores[0] << ' ' << s.scores[1] << ' '
            << s.scores[2] << '\\n';
}

void load(ScoreBook& book, const std::string& path) {
    std::ifstream in(path);
    if (!in) return;                    // 首次运行，文件不存在
    Student s;
    while (in >> s.id >> s.name
              >> s.scores[0] >> s.scores[1] >> s.scores[2])
        book.add(s);
}

int main() {
    ScoreBook book;
    try {
        load(book, "scores.txt");
    } catch (const std::exception& e) {
        std::cerr << "读取失败: " << e.what() << '\\n';
    }

    // 菜单循环，整体逻辑：
    while (true) {
        printMenu();
        int choice = readInt();     // 内部处理非法输入
        if (choice == 0) break;
        dispatch(choice, book);     // 增删查改、统计、存盘
    }
    save(book, "scores.txt");
}""",
                        "narration": "存盘用空格分隔的纯文本，简单可靠，人也能看懂。读盘时如果文件不存在就直接返回，因为首次运行本来就该是空的。主循环先读盘，再进入菜单循环，退出时存盘。每个操作都检查失败，读整数失败时清理输入缓冲，这就是我们在输入输出那一课学的内容。",
                    },
                    {
                        "kind": "bullets",
                        "title": "把这个项目继续做深",
                        "items": [
                            ("排序与查询", "按平均分排序，用 std::sort + lambda 比较器"),
                            ("统计", "最高分、最低分、及格率、分数段分布"),
                            ("健壮性", "所有输入都要校验，绝不假设用户输入正确"),
                            ("扩展", "换成 std::map 按学号索引，查询变 O(log n)"),
                        ],
                        "narration": "这个骨架已经能跑，接下来是进阶方向：加排序和统计；把输入校验做扎实；把 vector 换成 map 按学号索引，查找变对数时间。这几步做完，你就有了一个能写进简历的项目。",
                    },
                    {
                        "kind": "recap",
                        "title": "课程回顾",
                        "items": [
                            "基础：类型、控制流、函数、输入输出",
                            "内存：数组、字符串、指针、引用",
                            "面向对象：类、生命周期、继承、多态",
                            "现代 C++：智能指针、STL、lambda、移动语义",
                            "下一步：多写代码，多读标准库源码，多用 sanitizer",
                        ],
                        "narration": "二十六课到这里结束。从基础语法到内存模型，从面向对象到现代 C++，你已经有了完整的知识地图。真正的进步靠写：找一个小项目，从零写起，遇到问题就查文档。祝你写出漂亮又可靠的 C++ 代码。",
                    },
                ],
            },
        ],
    },
]
