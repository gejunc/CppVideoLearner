# -*- coding: utf-8 -*-
"""C++ 视频课程内容 —— 第 1 ~ 4 章。

每个课时 = 一组页面（page）。页面类型：
  cover   封面
  bullets 要点列表（逐条淡入）
  code    代码讲解（打字动画 + 可选运行结果）
  term    终端 / 运行结果
  recap   本课回顾

narration 字段是该页的旁白文字，会被 TTS 合成语音并决定页面时长。
"""

CHAPTERS_A = [
    # ================= 第 1 章 =================
    {
        "id": "ch1",
        "title": "第 1 章 · 起步",
        "desc": "认识 C++，写下第一个程序，搞懂从源码到可执行文件的全过程。",
        "lessons": [
            {
                "id": "l01",
                "title": "C++ 是什么：从第一个程序开始",
                "minutes": 3,
                "tags": ["入门", "hello world"],
                "pages": [
                    {
                        "kind": "cover",
                        "title": "C++ 是什么",
                        "subtitle": "从第一个程序开始",
                        "narration": "欢迎来到 C++ 视频课程。C++ 是一门编译型的静态类型语言，由 Bjarne Stroustrup 在 C 语言的基础上发展而来。它既保留了 C 的高效和对内存的直接控制，又加入了类、模板、异常这些高级抽象能力。今天我们先不纠结语法细节，先把第一个程序跑起来。",
                    },
                    {
                        "kind": "bullets",
                        "title": "C++ 的三个关键词",
                        "items": [
                            ("编译型", "源码先被编译器翻译成机器码，直接跑在 CPU 上"),
                            ("静态类型", "每个变量在编译期就有确定的类型，错误早暴露"),
                            ("零成本抽象", "类、模板、泛型写起来舒服，运行时几乎不额外付费"),
                        ],
                        "narration": "先记住三个关键词。第一，编译型，代码要先经过编译器翻译成机器码；第二，静态类型，变量的类型在编译期就定死了，很多错误在运行前就被抓住；第三，零成本抽象，这是 C++ 的设计哲学，你用类、模板写出来的代码，性能上不会比手写 C 差。",
                    },
                    {
                        "kind": "code",
                        "title": "Hello, C++",
                        "code": """#include <iostream>

int main() {
    std::cout << "Hello, C++!" << std::endl;
    return 0;
}""",
                        "output": "Hello, C++!",
                        "narration": "这就是最小的 C++ 程序。第一行 include iostream，把标准输入输出库引入进来。main 是程序入口，操作系统启动程序后第一个调用的就是它。cout 是标准输出流，两个小于号是流插入运算符，把右边的字符串送进屏幕。endl 表示换行并刷新缓冲区。最后 return 零，告诉系统一切正常。",
                    },
                    {
                        "kind": "code",
                        "title": "逐行拆解",
                        "code": """int main() {          // 入口函数，返回 int
    std::cout << "Hi"; // 打印，不换行
    std::cout << "\\n"; // 换行符
    return 0;          // 0 = 成功
}""",
                        "narration": "再拆一遍。int main 的 int 是返回类型，操作系统靠这个返回值判断程序是否正常结束。std::cout 里的 std 是命名空间，表示这个 cout 来自标准库，避免和你自己的变量重名。两个反斜杠 n 是换行转义字符。",
                    },
                    {
                        "kind": "recap",
                        "title": "本课回顾",
                        "items": [
                            "C++ = 编译型 + 静态类型 + 零成本抽象",
                            "main 是入口，返回 0 表示成功",
                            "std::cout << 把数据送进标准输出",
                        ],
                        "narration": "回顾一下：main 是入口，返回零表示成功；cout 用两个小于号往外送数据；程序是编译型的，所以下一步你需要的是一套编译环境。下一课我们就把编译、链接、运行的完整链路跑通。",
                    },
                ],
            },
            {
                "id": "l02",
                "title": "编译、链接与运行：程序是怎么跑起来的",
                "minutes": 4,
                "tags": ["工具链", "g++", "编译过程"],
                "pages": [
                    {
                        "kind": "cover",
                        "title": "从源码到可执行文件",
                        "subtitle": "预处理 · 编译 · 汇编 · 链接",
                        "narration": "这一课我们搞清楚一件被很多人跳过的事：你敲下回车之后，编译器到底做了什么。理解这条链路，以后遇到未定义引用、头文件找不到这类错误，你就知道该去哪一层找原因。",
                    },
                    {
                        "kind": "bullets",
                        "title": "四个阶段",
                        "items": [
                            ("预处理", "展开 #include、#define、条件编译，得到纯源码"),
                            ("编译", "语法分析 + 语义检查 + 优化，产出汇编代码"),
                            ("汇编", "把汇编翻译成机器码，得到目标文件 .o / .obj"),
                            ("链接", "把多个目标文件和库拼成一个可执行文件"),
                        ],
                        "narration": "整个链路分四步。预处理阶段处理所有井号开头的指令，把头文件内容原地展开；编译阶段做语法和类型检查，优化代码，生成汇编；汇编阶段把汇编变成机器码，得到目标文件；最后链接器把你写的所有目标文件和系统库缝合在一起，生成可执行文件。",
                    },
                    {
                        "kind": "term",
                        "title": "用 g++ 走一遍",
                        "lines": [
                            "$ g++ -std=c++17 hello.cpp -o hello.exe",
                            "",
                            "# 只做到编译，产出目标文件",
                            "$ g++ -c hello.cpp -o hello.o",
                            "",
                            "# 分步：预处理结果看一眼",
                            "$ g++ -E hello.cpp | head -20",
                            "",
                            "# 运行",
                            "$ ./hello.exe",
                            "Hello, C++!",
                        ],
                        "narration": "最常见的命令是一行搞定：g++ 加文件名，减 o 指定输出名。想看中间产物，可以用减 c 只编译不链接，或者用减 E 看预处理展开后的结果。注意标准版本参数，学习阶段建议至少 C++17。",
                    },
                    {
                        "kind": "bullets",
                        "title": "两种常见错误的定位",
                        "items": [
                            ("编译错误", "语法、类型、拼写问题，报错带文件名和行号，逐个修"),
                            ("链接错误", "undefined reference 表示函数只有声明没有定义，或有定义但没参与链接"),
                            ("运行时错误", "编译链接都过了，程序跑起来崩了，多半是指针、数组越界、空指针"),
                        ],
                        "narration": "把错误分三类。编译错误很好办，编译器会告诉你文件行号。链接错误的关键词是 undefined reference，意思是某个符号只有声明，找不到定义，常见原因是忘了把对应的 cpp 文件一起编译，或者忘了链接库。运行时错误最麻烦，因为它发生在你控制不住的时候，后面讲指针和内存时我们会专门处理。",
                    },
                    {
                        "kind": "recap",
                        "title": "本课回顾",
                        "items": [
                            "预处理 → 编译 → 汇编 → 链接",
                            "-c 只编译，-E 只看预处理，-o 指定输出",
                            "undefined reference 属于链接期错误",
                        ],
                        "narration": "记住四个阶段和三个常用参数。下一课进入变量和类型，这是所有 C++ 代码的地基。",
                    },
                ],
            },
        ],
    },
    # ================= 第 2 章 =================
    {
        "id": "ch2",
        "title": "第 2 章 · 基础语法",
        "desc": "变量、常量、运算符、输入输出——写程序最小的四块积木。",
        "lessons": [
            {
                "id": "l03",
                "title": "变量与基本类型",
                "minutes": 4,
                "tags": ["int", "double", "char", "bool"],
                "pages": [
                    {
                        "kind": "cover",
                        "title": "变量与基本类型",
                        "subtitle": "让数据有名字、有家",
                        "narration": "变量就是一块有名字的内存。类型决定这块内存有多大、怎么解释里面的二进制。C++ 的类型系统比很多语言严格，正是这份严格让我们能写出高效的代码。",
                    },
                    {
                        "kind": "bullets",
                        "title": "四种最常用的内置类型",
                        "items": [
                            ("int", "整数，通常 4 字节，范围约 ±21 亿"),
                            ("double", "双精度浮点，8 字节，约 15 位有效数字"),
                            ("char", "单字符，1 字节，本质是小整数"),
                            ("bool", "只有 true / false，1 字节"),
                        ],
                        "narration": "最常用的四个类型。int 是整数，一般四字节，能表示正负二十一亿左右。double 是双精度浮点，八字节，大约十五位有效十进制数字。char 是单个字符，只有一个字节，本质上是小整数。bool 只有真和假两种值。",
                    },
                    {
                        "kind": "code",
                        "title": "定义与初始化",
                        "code": """int    age    = 18;       // 拷贝初始化
double price  = 9.9;      // 浮点
char   grade  = 'A';      // 单引号是字符
bool   passed = true;     // 真 / 假

int a{5};        // 列表初始化（推荐）
int b(5);        // 直接初始化
int c = 5;       // 拷贝初始化

long long big = 1'000'000'000LL;  // 数字分隔符""",
                        "output": "age=18 price=9.9 grade=A passed=1",
                        "narration": "四种初始化写法里，推荐用花括号，也就是列表初始化。它有个好处：不允许窄化转换，比如把 double 塞进 int 会直接编译报错，而不是偷偷截断。另外注意字符用单引号，字符串用双引号。数字之间可以加单引号做千位分隔，只是给人和编译器看的，不改变数值。",
                    },
                    {
                        "kind": "code",
                        "title": "类型转换与溢出",
                        "code": """int  i = 7;
int  j = 2;
double d = i / j;      // 3   整数除法先截断
double e = i / 2.0;    // 3.5 有一个操作数是 double

unsigned char uc = 255;
uc = uc + 1;           // 0：无符号溢出会回绕

int big = 2147483647;
big = big + 1;         // 未定义行为（UB）""",
                        "narration": "这里有两个坑。第一，两个 int 相除，结果还是 int，小数部分直接丢掉，所以七除以二要写七除以二点零。第二，无符号数溢出会回绕，加一会变成零；而有符号数溢出是未定义行为，编译器可以做任何事，包括让整段代码消失。所以永远别依赖溢出。",
                    },
                    {
                        "kind": "recap",
                        "title": "本课回顾",
                        "items": [
                            "int / double / char / bool 是四块地基",
                            "优先用 {} 列表初始化，防止窄化",
                            "整数除法会截断，有符号溢出是 UB",
                        ],
                        "narration": "四块地基记住了，初始化优先用花括号，整数除法要小心，有符号溢出绝对不要碰。",
                    },
                ],
            },
            {
                "id": "l04",
                "title": "常量、auto 与类型别名",
                "minutes": 3,
                "tags": ["const", "constexpr", "auto"],
                "pages": [
                    {
                        "kind": "cover",
                        "title": "常量与类型推导",
                        "subtitle": "const · constexpr · auto",
                        "narration": "这一课解决两个问题：怎么表达一个值不该被改，以及怎么少写那些冗长的类型名。",
                    },
                    {
                        "kind": "code",
                        "title": "const 与 constexpr",
                        "code": """const double PI = 3.14159;      // 运行期常量
constexpr int  kMax = 100;      // 编译期常量

int arr[kMax];                  // 只有 constexpr 能这样用

const int& ref = PI;            // 常量引用，不能通过它修改

void print(const std::string& s);  // 只读参数，避免拷贝""",
                        "narration": "const 表示这个值在初始化后不能被修改，但它可能是运行期才算出来的。constexpr 更严格，要求编译期就能确定，所以可以用来指定数组长度、模板参数。函数参数里加 const 引用，是只读传参的标准写法，既避免拷贝又表明意图。",
                    },
                    {
                        "kind": "code",
                        "title": "auto：让编译器替你写类型",
                        "code": """auto  a = 42;          // int
auto  b = 3.14;        // double
auto  c = "hello";     // const char*
auto  d = std::string("hello");  // std::string

std::vector<int> v{1, 2, 3};
for (auto x : v)       { /* 拷贝一份 */ }
for (auto& x : v)      { x *= 2; }     // 引用，能改
for (const auto& x : v){ /* 只读，零拷贝 */ }""",
                        "narration": "auto 让编译器根据初始化表达式推导类型，注意它不会推导出引用，需要引用就自己加和号。遍历容器时，auto 加和号是修改元素，const auto 加和号是只读零拷贝，这是最常用的两种写法。另外提醒，auto 只能用在有初始化的地方，因为它要靠初始值来推导。",
                    },
                    {
                        "kind": "bullets",
                        "title": "什么时候用哪个",
                        "items": [
                            ("const", "接口参数、成员变量，表达“不该改”"),
                            ("constexpr", "需要在编译期求值的场合：数组长度、模板参数"),
                            ("auto", "类型名字又长又显然的时候，比如迭代器和 lambda"),
                            ("using", "using Price = double; 给类型起别名，比 typedef 好读"),
                        ],
                        "narration": "总结一下选择标准。表达不该被改，用 const。需要编译期求值，用 constexpr。类型名太长又显而易见，用 auto。给类型起别名用 using，比老的 typedef 可读性好得多。",
                    },
                    {
                        "kind": "recap",
                        "title": "本课回顾",
                        "items": [
                            "const 运行期常量，constexpr 编译期常量",
                            "auto 不推导引用，需要引用要显式写 &",
                            "const auto& 是遍历容器的万能写法",
                        ],
                        "narration": "下一课讲运算符，那里面藏着 C++ 最容易写错的一批符号。",
                    },
                ],
            },
            {
                "id": "l05",
                "title": "运算符与表达式",
                "minutes": 4,
                "tags": ["算术", "优先级", "自增"],
                "pages": [
                    {
                        "kind": "cover",
                        "title": "运算符与表达式",
                        "subtitle": "优先级、副作用、和那些容易踩的坑",
                        "narration": "运算符看着简单，但它是笔试题和线上事故的高发区。这一课我们重点看三类：算术、比较逻辑、自增自减。",
                    },
                    {
                        "kind": "code",
                        "title": "算术与取模",
                        "code": """int a = 17, b = 5;

a + b   // 22
a - b   // 12
a * b   // 85
a / b   // 3    整数除法
a % b   // 2    取余

double x = 17.0 / 5;   // 3.4

// 负数取模：结果的符号跟着被除数
-7 % 3    // -1
-7 % -3   // -1""",
                        "narration": "加减乘除取余。整数除法会丢小数，这是初学者最常见的 bug。取模的符号规则要特别注意：C++ 里取模结果的符号跟随被除数，负七模三等于负一，这一点和 Python 不同，写跨语言代码时容易翻车。",
                    },
                    {
                        "kind": "code",
                        "title": "比较、逻辑与短路",
                        "code": """if (0 < x && x < 10) { }        // 不能写成 0 < x < 10

bool ok = ptr && ptr->value;    // 短路：ptr 为空就不求右边

// 三目运算符
int m = (a > b) ? a : b;

// 逗号运算符：从左到右求值，取最后一个
int n = (a++, b++);   // n = b 的旧值""",
                        "narration": "比较和逻辑里最经典的错误是把数学写法搬过来：零小于 x 小于十，在 C++ 里会先算零小于 x 得到一个布尔值，再拿真或假去和十比较，永远成立。正确写法是拆成两个比较用与连接。逻辑与、或都有短路特性，左边能决定结果时右边不执行，所以可以用它做空指针保护。三目运算符适合二选一。",
                    },
                    {
                        "kind": "code",
                        "title": "自增自减：少写一行，多一个坑",
                        "code": """int i = 0;
int a = i++;   // a = 0, i = 1  先取值后加
int b = ++i;   // b = 2, i = 2  先加后取值

// 同一个表达式里多次修改同一变量 = 未定义行为
int n = 0;
int bad = n++ + ++n;   // 不要这么写

// 单独一行用，性能上没区别
for (int k = 0; k < 10; ++k) { }""",
                        "narration": "前置加加和后置加加的区别：后置是先取值再加一，前置是先加一再取值。在同一个表达式里对同一个变量多次修改，是未定义行为，结果取决于编译器，所以千万别写。单独作为一条语句使用时两者完全等价，循环里习惯用前置。",
                    },
                    {
                        "kind": "recap",
                        "title": "本课回顾",
                        "items": [
                            "整数除法截断，负数取模符号跟随被除数",
                            "0 < x < 10 是错的，必须拆成两个比较",
                            "别在同一个表达式里多次修改同一变量",
                        ],
                        "narration": "运算符这课记住三句话：除法小心截断，比较必须拆开写，副作用不要叠加。下一课开始和用户交互，学输入输出。",
                    },
                ],
            },
            {
                "id": "l06",
                "title": "输入输出：cin、cout 与格式化",
                "minutes": 4,
                "tags": ["iostream", "cin", "iomanip"],
                "pages": [
                    {
                        "kind": "cover",
                        "title": "输入输出",
                        "subtitle": "让程序能和人对话",
                        "narration": "一个只能打印固定文字的程序没什么用。这一课我们让程序接受输入、输出格式化的结果，顺便讲清楚 cin 失败之后为什么会陷入死循环。",
                    },
                    {
                        "kind": "code",
                        "title": "最基本的读写",
                        "code": """#include <iostream>
using std::cin;
using std::cout;

int main() {
    int    age;
    double score;
    std::string name;

    cout << "姓名 年龄 成绩: ";
    cin >> name >> age >> score;

    cout << name << " 今年 " << age
         << " 岁，成绩 " << score << '\\n';
}""",
                        "output": "姓名 年龄 成绩: Tom 18 92.5\nTom 今年 18 岁，成绩 92.5",
                        "narration": "cin 用两个大于号从标准输入取数据。注意它按空白分割，所以读名字遇到空格就停了，要读整行得用 getline。三个变量可以连着写，cin 会按顺序依次填充。",
                    },
                    {
                        "kind": "code",
                        "title": "格式化输出",
                        "code": """#include <iomanip>

cout << std::fixed << std::setprecision(2) << 3.14159;
// 3.14

cout << std::setw(8) << 42 << "|" << '\\n';
//      42|

cout << std::hex << 255 << '\\n';     // ff
cout << std::oct << 255 << '\\n';     // 377
cout << std::boolalpha << true;       // true""",
                        "narration": "格式化靠 iomanip 里的一组操纵符。fixed 加 setprecision 控制小数位数；setw 控制字段宽度，但它只对下一次输出生效，所以要每次都写；hex 和 oct 切换进制；boolalpha 把真假打印成单词。这些设置是粘性的，改一次一直有效，除非你再改回来。",
                    },
                    {
                        "kind": "code",
                        "title": "输入失败：那个著名的死循环",
                        "code": """int n;
while (cin >> n) {      // 读失败会退出循环
    // 用 n
}

// 错误示范：期望输入数字，用户输入了 abc
// 此时 cin 进入失败状态，且 abc 还留在缓冲区

if (!cin) {
    cin.clear();                       // 清除错误标志
    cin.ignore(10000, '\\n');          // 丢弃这一行
}""",
                        "narration": "这是新手必踩的坑。如果用户该输数字却输了字母，cin 会进入失败状态，之后所有读取都直接失败，循环体一次不进或者疯狂空转。正确做法是 clear 清掉错误标志，再 ignore 丢掉缓冲区里那行脏数据。把 cin 放在 while 条件里，是在读成功时才继续，这是最简洁的写法。",
                    },
                    {
                        "kind": "recap",
                        "title": "本课回顾",
                        "items": [
                            "cin >> 按空白分词，读整行用 getline",
                            "fixed + setprecision 控制小数位",
                            "读失败要 clear() + ignore() 才能恢复",
                        ],
                        "narration": "输入输出这课的核心是记住 cin 会失败，失败后必须清理。到这里基础语法就齐了，下一章开始让程序做判断和循环。",
                    },
                ],
            },
        ],
    },
    # ================= 第 3 章 =================
    {
        "id": "ch3",
        "title": "第 3 章 · 流程控制",
        "desc": "让程序会分支、会重复、会跳出。",
        "lessons": [
            {
                "id": "l07",
                "title": "if、else 与 switch",
                "minutes": 4,
                "tags": ["if", "switch", "分支"],
                "pages": [
                    {
                        "kind": "cover",
                        "title": "分支：if 与 switch",
                        "subtitle": "让程序学会做选择",
                        "narration": "程序的第一种智能就是判断。这一课讲 if 系列的写法，以及 switch 什么时候比 if 更合适。",
                    },
                    {
                        "kind": "code",
                        "title": "if / else if / else",
                        "code": """int score = 78;

if (score >= 90) {
    std::cout << "A\\n";
} else if (score >= 75) {
    std::cout << "B\\n";
} else if (score >= 60) {
    std::cout << "C\\n";
} else {
    std::cout << "D\\n";
}
// 输出 B""",
                        "narration": "if 从上往下依次判断，一旦命中就执行对应的块并跳过后面所有分支。所以条件的顺序很重要，如果先判断大于等于六十，那九十分也会被分到 C。写这种阶梯判断时，习惯从最严格的条件开始。",
                    },
                    {
                        "kind": "code",
                        "title": "switch：等值判断的清爽写法",
                        "code": """switch (grade) {
    case 'A':
    case 'a':
        std::cout << "优秀\\n";
        break;                 // 忘了它就会贯穿
    case 'B':
        std::cout << "良好\\n";
        break;
    default:
        std::cout << "未知\\n";
        break;
}""",
                        "narration": "switch 专门处理等值判断，比一串 if else 更清晰。两个注意点：第一，case 后面不写 break 会贯穿到下一个分支，有时是故意利用这个特性合并处理，但多数时候是 bug；第二，switch 的条件只能是整型或枚举，不能是浮点和字符串。C++17 里可以在 switch 里面直接定义变量并初始化。",
                    },
                    {
                        "kind": "bullets",
                        "title": "写法建议",
                        "items": [
                            ("总是写 else", "哪怕只是防御性处理，也比静默漏掉分支好"),
                            ("条件从严格到宽松", "阶梯判断先写最难满足的"),
                            ("switch 记得 break", "或者用 C++17 的 [[fallthrough]] 显式声明故意贯穿"),
                            ("复杂条件抽成函数", "if (isValid(x) && inRange(y)) 比堆一大坨可读"),
                        ],
                        "narration": "四条经验：写全 else；阶梯条件从严格到宽松；switch 记得 break，真是故意贯穿就写 fallthrough 显式说明；条件太长就抽成有名字的函数，让代码自己解释自己。",
                    },
                    {
                        "kind": "recap",
                        "title": "本课回顾",
                        "items": [
                            "阶梯 if 从上到下命中即停，顺序决定结果",
                            "switch 只做等值判断，别忘 break",
                            "用函数名代替复杂条件表达式",
                        ],
                        "narration": "下一课讲循环，那是让程序真正干活的地方。",
                    },
                ],
            },
            {
                "id": "l08",
                "title": "for、while 与范围 for",
                "minutes": 4,
                "tags": ["for", "while", "range-for"],
                "pages": [
                    {
                        "kind": "cover",
                        "title": "循环：重复的艺术",
                        "subtitle": "for · while · do-while · 范围 for",
                        "narration": "循环是程序最强大的能力之一。这一课讲四种循环分别适合什么场景，以及怎么避免死循环和边界错误。",
                    },
                    {
                        "kind": "code",
                        "title": "三种经典循环",
                        "code": """// 1. 计数循环：次数已知
for (int i = 0; i < 5; ++i)
    std::cout << i << ' ';        // 0 1 2 3 4

// 2. 条件循环：次数未知
int n = 27;
while (n != 1) {
    n = (n % 2 == 0) ? n / 2 : 3 * n + 1;
}

// 3. 至少执行一次
int x;
do {
    std::cin >> x;
} while (x <= 0);""",
                        "narration": "for 适合次数明确的场景，三个部分依次是初始化、循环条件、每次迭代后的动作。while 适合次数未知、只知道什么时候该停的场景。do while 至少执行一次，适合反复要求用户输入直到合法这种交互。",
                    },
                    {
                        "kind": "code",
                        "title": "范围 for：C++11 之后的首选",
                        "code": """std::vector<std::string> names{"Ann", "Bob", "Cid"};

for (const auto& name : names) {
    std::cout << name << '\\n';
}

// 修改元素
for (auto& name : names) {
    name += "!";
}

// 注意：遍历时增删元素会失效
for (auto& n : names) {
    // names.push_back(...);  // 危险
}""",
                        "narration": "范围 for 是遍历容器的首选写法，意图清晰，不会写错边界。要修改元素就加和号，只读就加 const 引用。有一个重要的坑：遍历过程中往容器里插入或删除元素，迭代器会失效，行为未定义，要改就先收集、遍历完再改。",
                    },
                    {
                        "kind": "code",
                        "title": "常见边界错误",
                        "code": """int arr[5] = {1, 2, 3, 4, 5};

// 错：越界访问，多走了一步
for (int i = 0; i <= 5; ++i) { }

// 对
for (int i = 0; i < 5; ++i) { }

// 错：无符号数和 0 比较，i >= 0 恒为真
for (size_t i = 5; i >= 0; --i) { }

// 对：倒着走用有符号或有技巧
for (int i = 4; i >= 0; --i) { }""",
                        "narration": "边界是最容易错的地方。小于和小于等于差一个等号就可能读越界。还有一个隐蔽的坑：用无符号类型做倒序循环，条件大于等于零永远成立，于是变成死循环或者无限访问。倒序遍历就用有符号 int，或者用迭代器。",
                    },
                    {
                        "kind": "recap",
                        "title": "本课回顾",
                        "items": [
                            "次数已知用 for，未知用 while，至少要跑一次用 do-while",
                            "范围 for + const auto& 是遍历容器的默认选择",
                            "注意边界符号，别用无符号类型做倒序循环",
                        ],
                        "narration": "循环这课记住边界，其他的都好办。下一课讲怎么提前跳出和跳过。",
                    },
                ],
            },
            {
                "id": "l09",
                "title": "break、continue 与循环嵌套",
                "minutes": 3,
                "tags": ["break", "continue", "嵌套"],
                "pages": [
                    {
                        "kind": "cover",
                        "title": "跳出与跳过",
                        "subtitle": "break · continue · 多层跳出",
                        "narration": "有时候我们要提前结束循环，或者跳过某一轮。这一课讲 break 和 continue 的正确用法，还有多层嵌套时怎么优雅地全部跳出。",
                    },
                    {
                        "kind": "code",
                        "title": "break 与 continue",
                        "code": """for (int i = 0; i < 10; ++i) {
    if (i == 5) break;      // 直接结束整个循环
    if (i % 2 == 0) continue; // 跳过本轮剩余部分
    std::cout << i << ' ';   // 1 3
}

// 在 switch 里 break 只跳出 switch
switch (x) {
    case 1: break;           // 不会跳出外层循环
}""",
                        "narration": "break 结束最近的整个循环，continue 跳过这一轮剩下的语句直接进入下一轮。注意 break 在 switch 里只跳出 switch，如果 switch 在循环里，别指望它跳出循环。",
                    },
                    {
                        "kind": "code",
                        "title": "多层循环怎么一次跳出",
                        "code": """// 方法一：标志位
bool found = false;
for (int i = 0; i < n && !found; ++i)
    for (int j = 0; j < m; ++j)
        if (a[i][j] == target) { found = true; break; }

// 方法二：抽出函数，直接 return（推荐）
bool hasTarget(const Matrix& a, int target) {
    for (const auto& row : a)
        for (int v : row)
            if (v == target) return true;
    return false;
}

// 方法三：goto（能不用就不用，但跳出深层是正当用法）""",
                        "narration": "嵌套循环里 break 只能跳出一层，所以出现了那个经典问题：怎么跳出两层。三种办法：用标志位配合条件；把搜索逻辑抽成函数直接 return，这是最推荐的，可读性最好；最后是 goto，虽然被诟病，但跳出多层嵌套恰恰是它少数的正当用途。",
                    },
                    {
                        "kind": "recap",
                        "title": "本课回顾",
                        "items": [
                            "break 结束最近的循环，continue 跳过本轮",
                            "switch 里的 break 不作用于外层循环",
                            "多层跳出优先抽函数 return",
                        ],
                        "narration": "流程控制三课结束，下一章开始写函数。函数是从写脚本到写工程的分界线。",
                    },
                ],
            },
        ],
    },
    # ================= 第 4 章 =================
    {
        "id": "ch4",
        "title": "第 4 章 · 函数",
        "desc": "把代码切成一块块可复用的积木，以及参数怎么传最合适。",
        "lessons": [
            {
                "id": "l10",
                "title": "函数定义、声明与重载",
                "minutes": 4,
                "tags": ["函数", "重载", "声明"],
                "pages": [
                    {
                        "kind": "cover",
                        "title": "函数：代码的积木",
                        "subtitle": "定义 · 声明 · 重载",
                        "narration": "函数是把一段逻辑打包并命名的工具。用函数组织代码，最重要的收益不是少打字，而是每个名字都是一句解释。",
                    },
                    {
                        "kind": "code",
                        "title": "声明与定义",
                        "code": """// 声明：告诉编译器有这个函数，可以先用
int add(int a, int b);

int main() {
    std::cout << add(2, 3);   // 调用时只需要声明
}

// 定义：给出实现
int add(int a, int b) {
    return a + b;
}""",
                        "narration": "函数声明只有签名没有函数体，定义才有实现。C++ 要求调用前必须见过声明，所以常用头文件集中放声明。一个函数只能定义一次，但可以声明多次，这就是为什么头文件里要写 include guard。",
                    },
                    {
                        "kind": "code",
                        "title": "重载：同名不同参",
                        "code": """void print(int x);          // 1
void print(double x);       // 2
void print(const std::string& s);  // 3
void print(int x, int y);   // 4

print(42);          // 选 1
print(3.14);        // 选 2
print("hi");        // 选 3
print(1, 2);        // 选 4

// 只有返回类型不同 —— 不行！编译错误
// int  f(int);
// void f(int);""",
                        "narration": "重载允许同名函数接受不同参数。编译器根据实参的类型和个数决定调用哪个，这叫重载解析。关键限制：不能只靠返回类型区分，因为调用时你根本不知道返回值要什么类型。另外隐式转换会让重载变得很微妙，比如传进来一个 short，可能两个版本都能接受，这时编译器可能报歧义。",
                    },
                    {
                        "kind": "bullets",
                        "title": "好函数的特征",
                        "items": [
                            ("名字说清意图", "calculateAverage 比 calc 好"),
                            ("单一职责", "一个函数只做一件事，好测好复用"),
                            ("参数少", "超过四五个就该考虑封装成结构体"),
                            ("无隐含状态", "尽量不依赖全局变量，输入输出靠参数和返回值"),
                        ],
                        "narration": "什么样的函数算好函数？名字能说清意图；只做一件事，超过一屏就该拆；参数别太多，太多说明你该定义一个结构体；最后尽量别依赖全局状态，输入输出都通过参数和返回值表达。",
                    },
                    {
                        "kind": "recap",
                        "title": "本课回顾",
                        "items": [
                            "声明放头文件，定义放 cpp",
                            "重载靠参数列表区分，不能只改返回类型",
                            "函数名要能代替注释",
                        ],
                        "narration": "下一课是本章最重要的内容：参数到底怎么传。",
                    },
                ],
            },
            {
                "id": "l11",
                "title": "参数传递：值、引用、指针",
                "minutes": 5,
                "tags": ["引用", "指针", "值传递"],
                "pages": [
                    {
                        "kind": "cover",
                        "title": "三种参数传递",
                        "subtitle": "值 · 引用 · 指针",
                        "narration": "这是 C++ 里最影响性能和正确性的一个选择。传值会拷贝，传引用不拷贝但能改，传指针能改还能为空。搞清楚它们的语义，你就理解了 C++ 的一半。",
                    },
                    {
                        "kind": "code",
                        "title": "值传递：安全但会拷贝",
                        "code": """void byValue(int x) {
    x = 999;                 // 改的是副本
}

void byValue(std::string s) {
    s += "!";                // 整个字符串被拷贝了一次
}

int main() {
    int a = 1;
    byValue(a);              // a 仍然是 1
    std::string t = "hi";
    byValue(t);              // 大对象拷贝，有性能代价
}""",
                        "narration": "值传递会把实参复制一份给形参，函数里怎么改都不影响外面，非常安全。代价是拷贝成本，对 int 这种小类型无所谓，但传一个大字符串或大对象就是白白复制。",
                    },
                    {
                        "kind": "code",
                        "title": "引用传递：零拷贝，可修改",
                        "code": """void byRef(int& x) {         // 能改调用方的变量
    x = 999;
}

void byConstRef(const std::string& s) {  // 零拷贝 + 不可改
    std::cout << s.size();
}

int main() {
    int a = 1;
    byRef(a);        // a 变成 999
    std::string t = "hello";
    byConstRef(t);   // 不拷贝，也不能改 t
}""",
                        "narration": "引用就是别名，传引用等于直接操作调用方的变量，没有拷贝。加 const 就变成只读引用，这是传大对象的黄金标准：既不复制，又防止误改。记住这个组合：const 引用。",
                    },
                    {
                        "kind": "code",
                        "title": "指针传递：能改、可为空、能切换",
                        "code": """void byPtr(int* p) {
    if (p == nullptr) return;    // 必须自己判空
    *p = 999;
}

void swap(int* a, int* b) {
    int t = *a; *a = *b; *b = t;
}

int main() {
    int x = 1, y = 2;
    byPtr(&x);        // 传地址
    swap(&x, &y);     // x=2 y=1
    byPtr(nullptr);   // 合法：表示不指向任何东西
}""",
                        "narration": "指针本质是一个地址值，通过星号解引用访问目标。它的独特之处是可以为空，所以可以作为可选参数；它也可以被重新指向别的对象。代价是每次使用都要考虑空指针和生命周期，责任更重。",
                    },
                    {
                        "kind": "bullets",
                        "title": "怎么选",
                        "items": [
                            ("小类型（int / double / 指针）", "直接传值，最简单"),
                            ("大对象只读", "const T&，零拷贝只读，这是最常用的"),
                            ("需要修改调用方", "T&，比指针更安全（引用不能为空）"),
                            ("参数可选 / 需要重指向", "T*，并显式判空"),
                        ],
                        "narration": "选择规则很清晰：小类型直接传值；大对象只读用 const 引用；要修改调用方用引用；参数可选或者需要重指向才用指针。能用引用就别用指针，因为引用不能为空，少一类错误。",
                    },
                    {
                        "kind": "recap",
                        "title": "本课回顾",
                        "items": [
                            "值传递有拷贝，引用传递是别名",
                            "const T& 是传大对象的默认答案",
                            "指针能空能重指向，但要自己判空",
                        ],
                        "narration": "这一课是 C++ 的基本功，反复练。下一课讲默认参数、内联和递归。",
                    },
                ],
            },
            {
                "id": "l12",
                "title": "默认参数、内联与递归",
                "minutes": 4,
                "tags": ["默认参数", "inline", "递归"],
                "pages": [
                    {
                        "kind": "cover",
                        "title": "函数的三个进阶细节",
                        "subtitle": "默认参数 · 内联 · 递归",
                        "narration": "这一课是函数的补充：怎么让参数有默认值，什么时候该内联，以及递归怎么写才不出栈溢出。",
                    },
                    {
                        "kind": "code",
                        "title": "默认参数",
                        "code": """// 默认参数必须从右往左连续给出
void log(const std::string& msg,
         int level = 0,
         bool timestamp = false);

log("start");            // level=0, timestamp=false
log("error", 2);         // timestamp=false
log("dbg", 1, true);     // 全部指定

// 错：中间留空
// void f(int a = 1, int b);""",
                        "narration": "默认参数让调用方可以省略靠右的部分。规则是从右往左连续，不能中间留空。还有一个坑：默认参数在调用点求值，所以别用会变化的全局变量，也别在虚函数里依赖默认参数做多态，因为默认参数是静态绑定的。",
                    },
                    {
                        "kind": "code",
                        "title": "inline：给编译器的建议",
                        "code": """inline int square(int x) { return x * x; }

// 现代实践：
// 1. 小函数定义在头文件里，编译器自己会内联
// 2. inline 关键字主要作用是允许头文件里定义函数而不重定义
// 3. 别为了性能硬加 inline，优化器比你想得聪明

// 类内定义的成员函数天然是内联候选
class Point {
public:
    int getX() const { return x_; }
private:
    int x_ = 0;
};""",
                        "narration": "inline 只是对编译器的建议，不是命令。它真正确定的语义是允许这个函数在多个翻译单元里重复定义，所以头文件里的函数定义要加 inline。性能上，现代编译器对小函数会自动内联，你手写 inline 基本没用。",
                    },
                    {
                        "kind": "code",
                        "title": "递归：前提和陷阱",
                        "code": """int factorial(int n) {
    if (n <= 1) return 1;        // 必须有终止条件
    return n * factorial(n - 1);
}

// 尾递归写法（便于优化）
int fact(int n, int acc = 1) {
    if (n <= 1) return acc;
    return fact(n - 1, acc * n);
}

// 危险：没有终止条件 → 栈溢出
// int boom(int n) { return boom(n + 1); }""",
                        "narration": "递归必须有终止条件，否则会无限调用导致栈溢出。递归适合问题本身是递归定义的场景，比如树遍历、分治。能用尾递归就别用普通递归，但要注意 C++ 标准并不保证尾递归优化。深度可能超过几千层时，改成循环更稳。",
                    },
                    {
                        "kind": "recap",
                        "title": "本课回顾",
                        "items": [
                            "默认参数从右往左连续，调用点求值",
                            "inline 的实质是允许多翻译单元重复定义",
                            "递归必须有终止条件，注意栈深度",
                        ],
                        "narration": "函数这章就讲完了：定义与重载、三种传参、默认参数和递归。下一章进入 C++ 的分水岭：数组、字符串、指针和引用。",
                    },
                ],
            },
        ],
    },
]
