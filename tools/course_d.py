# -*- coding: utf-8 -*-
"""第 14 章 · 完整项目实战：命令行记账本。

四节课把前面 13 章的知识串成一个真实程序：
设计 → 核心实现 → 持久化 → 收尾交付。
完整源码在 assets/samples/account_book.cpp，约 270 行，可直接编译运行。
"""

CHAPTERS_D = [
    {
        "id": "ch14",
        "title": "第 14 章 · 项目实战",
        "desc": "从零写一个 270 行的命令行记账本：设计、实现、持久化、收尾。",
        "lessons": [
            {
                "id": "l47",
                "title": "项目设计：先想清楚再动手",
                "minutes": 5,
                "tags": ["项目", "设计", "数据结构"],
                "pages": [
                    {
                        "kind": "cover",
                        "title": "项目实战：命令行记账本",
                        "subtitle": "需求 · 结构 · 数据模型",
                        "narration": "接下来四节课，我们从零写一个真实能用的程序：一个命令行记账本。它只有两百多行，但用到了前面讲的所有核心知识。这一课先不写代码，先把设计想清楚。",
                    },
                    {
                        "kind": "bullets",
                        "title": "需求拆解",
                        "items": [
                            ("记一笔", "日期、分类、金额、备注，支出填负数"),
                            ("看明细", "列表展示，中文字符要能对齐"),
                            ("删除一笔", "按编号删除"),
                            ("统计", "收入、支出、结余，按分类和按月汇总"),
                            ("存盘", "退出时写入文件，启动时读回"),
                        ],
                        "narration": "先把需求列清楚。五个功能：记一笔、看明细、删一笔、看统计、存盘。注意需求里藏着一个容易被忽略的细节：金额用负数表示支出，这样一个数字就能同时表达方向和大小，统计时只要相加就行。",
                    },
                    {
                        "kind": "code",
                        "title": "数据模型：一个结构体",
                        "code": """struct Transaction {
    std::string date;       // 2024-05-01
    std::string category;   // 餐饮 / 交通 / 工资
    double      amount = 0; // 正数收入，负数支出
    std::string note;
};

// 为什么不拆成 Income / Expense 两个类型？
// 因为它们的字段完全一样，唯一区别是 amount 的正负。
// 用符号表达方向，比多一个枚举字段更省事，统计也更简单。""",
                        "narration": "整个程序的数据模型就这一个结构体。为什么不用两个类型区分收入和支出？因为字段完全一样，唯一区别就是金额正负。用符号表达方向，统计时直接累加即可，省掉了一堆分支判断。这就是数据模型设计的价值：选对了，后面的代码都很短。",
                    },
                    {
                        "kind": "code",
                        "title": "职责划分：谁管什么",
                        "code": """class Ledger {
public:
    void add(const Transaction& t);
    bool remove(std::size_t no);
    double total() const;
    double sumOf(bool income) const;
    std::vector<std::pair<std::string, double>> byCategory() const;
    std::vector<std::pair<std::string, double>> byMonth() const;
    bool save(const std::string& path) const;
    bool load(const std::string& path);

private:
    std::vector<Transaction> items_;   // 唯一的成员
};

// 界面层（main 里的菜单循环）只负责输入输出，
// 所有业务逻辑都在 Ledger 里 —— 这样以后换界面不用改逻辑。""",
                        "narration": "只有一个类：Ledger，内部就一个 vector。所有业务逻辑都放这里：增删查、统计、存取。菜单循环只负责读输入、打印输出。这种分层的好处是显而易见的：以后你想加个图形界面，Ledger 一行都不用改。",
                    },
                    {
                        "kind": "recap",
                        "title": "本课回顾",
                        "items": [
                            "需求先拆到能一条条实现的程度",
                            "数据模型用正负号表达收支方向",
                            "业务逻辑集中在 Ledger，界面层只管 IO",
                        ],
                        "narration": "设计定下来了，下一课开始写核心逻辑。",
                    },
                ],
            },
            {
                "id": "l48",
                "title": "核心实现：增删查与汇总",
                "minutes": 6,
                "tags": ["vector", "lambda", "聚合"],
                "pages": [
                    {
                        "kind": "cover",
                        "title": "核心实现",
                        "subtitle": "增删查 · 分组汇总",
                        "narration": "这一课写 Ledger 的实现。你会发现，前面学的 vector、lambda、algorithm，在这里全都用上了。",
                    },
                    {
                        "kind": "code",
                        "title": "增与删",
                        "code": """void add(const Transaction& t) { items_.push_back(t); }

bool remove(std::size_t no) {        // 界面上的编号从 1 开始
    if (no == 0 || no > items_.size()) return false;
    items_.erase(items_.begin() + static_cast<long>(no - 1));
    return true;
}

// 两个注意点：
// 1. 编号从 1 开始是给人看的，内部下标从 0 开始，转换一下
// 2. 删除前必须校验范围，否则 erase 传越界迭代器是 UB""",
                        "narration": "增加就是 push back。删除要注意两件事：界面上的编号从 1 开始，内部下标从 0 开始，要转一次；还有必须先校验范围，因为 erase 传一个越界迭代器是未定义行为，不会给你报错。返回 bool 表示成不成功，让界面层决定怎么提示。",
                    },
                    {
                        "kind": "code",
                        "title": "统计：一个 lambda 搞定方向",
                        "code": """double total() const {
    double sum = 0;
    for (const auto& t : items_) sum += t.amount;
    return sum;
}

double sumOf(bool income) const {
    double sum = 0;
    for (const auto& t : items_)
        if ((t.amount >= 0) == income) sum += t.amount;
    return sum;
}

// 收入 = 8000.00   支出 = -32.50   结余 = 7967.50
// 注意支出是负数，所以“支出合计”为负是符合直觉的""",
                        "narration": "结余就是全部相加。收入合计和支出合计用一个布尔参数区分方向：拿金额是否大于等于零，和你要的 income 标志比较。因为支出本身是负数，所以支出合计显示为负数，这是对的，不是 bug。",
                    },
                    {
                        "kind": "code",
                        "title": "按分类汇总：分组 + 排序",
                        "code": """std::vector<std::pair<std::string, double>> byCategory() const {
    std::vector<std::pair<std::string, double>> out;
    for (const auto& t : items_) {
        auto it = std::find_if(out.begin(), out.end(),
            [&](const auto& p) { return p.first == t.category; });
        if (it == out.end()) out.emplace_back(t.category, t.amount);
        else                 it->second += t.amount;
    }
    std::sort(out.begin(), out.end(),
              [](const auto& a, const auto& b) { return a.second > b.second; });
    return out;
}""",
                        "narration": "分组汇总的思路：遍历每一笔，在结果里找有没有同类，有就累加，没有就新建一条。这里用 find if 配 lambda 按分类名查找。最后按金额从大到小排序，这样最花钱的类别排在最前面，一眼就能看出钱花哪了。数据量大的话应该改用 map，但几百条记录线性查找完全够用。",
                    },
                    {
                        "kind": "code",
                        "title": "按月汇总：key 的构造",
                        "code": """std::vector<std::pair<std::string, double>> byMonth() const {
    std::vector<std::pair<std::string, double>> out;
    for (const auto& t : items_) {
        if (t.date.size() < 7) continue;          // 日期不完整就跳过
        std::string key = t.date.substr(0, 7);    // "2024-05"
        auto it = std::find_if(out.begin(), out.end(),
            [&](const auto& p) { return p.first == key; });
        if (it == out.end()) out.emplace_back(key, t.amount);
        else                 it->second += t.amount;
    }
    std::sort(out.begin(), out.end(),
              [](const auto& a, const auto& b) { return a.first < b.first; });
    return out;
}""",
                        "narration": "按月汇总的套路和按分类几乎一样，唯一区别是 key 的构造：取日期前七个字符，也就是年月。这里提前做了长度检查，否则日期格式不对时 substr 会抛异常。这类防御在真实程序里是必须的，因为你的数据文件可能是手工改过的。",
                    },
                    {
                        "kind": "recap",
                        "title": "本课回顾",
                        "items": [
                            "删除要校验范围，界面编号和内部下标差 1",
                            "用正负号统一收支，统计逻辑极简",
                            "分组汇总 = 线性查找累加，再按金额排序",
                        ],
                        "narration": "核心逻辑写完了，现在数据只存在内存里，程序一退出就没了。下一课解决持久化。",
                    },
                ],
            },
            {
                "id": "l49",
                "title": "持久化：读写 CSV 与容错",
                "minutes": 5,
                "tags": ["文件", "CSV", "容错"],
                "pages": [
                    {
                        "kind": "cover",
                        "title": "持久化",
                        "subtitle": "存取 · 容错 · 格式选择",
                        "narration": "数据要能存下来。这一课用最朴素的 CSV 格式，同时把“文件可能不存在、可能被手改坏”这些真实情况都处理掉。",
                    },
                    {
                        "kind": "code",
                        "title": "为什么选 CSV",
                        "code": """// 存盘格式：日期,分类,金额,备注
2024-05-01,餐饮,-32.5,午餐
2024-05-02,工资,8000,五月工资

// 对比其他选择：
// - 二进制：省空间但人看不懂，格式一改就全废
// - JSON： 通用，但要引入第三方库
// - CSV：  人可读、可手工编辑、十行代码就能读写

// 结论：小工具优先选"人能看懂"的格式，
//       出了问题你自己就能用记事本查""",
                        "narration": "为什么选 CSV 而不是二进制或 JSON？二进制的坏处是格式一改旧数据全废，而且你没法直接看。JSON 虽然通用，但标准库没有解析器，得引第三方库。CSV 人可读、可手工改、读写只要十行代码。小工具优先选人能看懂的格式，出问题时你自己用记事本就能排查。",
                    },
                    {
                        "kind": "code",
                        "title": "写",
                        "code": """bool save(const std::string& path) const {
    std::ofstream out(path);
    if (!out) return false;              // 打开失败要告诉调用方

    for (const auto& t : items_) {
        out << t.date << ',' << t.category << ','
            << t.amount << ',' << t.note << '\\n';
    }
    return true;                          // 析构自动关闭文件
}

// 注意：如果备注里有逗号，这个格式就崩了。
// 真实项目要么做转义，要么换更严谨的格式。
// 这里为了简单，约定备注不写逗号。""",
                        "narration": "写很简单：打开文件流，逐行输出，用逗号分隔。打开失败要返回 false，让界面层能提示用户。文件不需要手动关闭，流对象析构时会关。这里有个众所周知的局限：如果备注里有逗号，读回来就会错位。真实项目要做转义，我们为了简单约定备注不写逗号，但你要知道这个坑在哪。",
                    },
                    {
                        "kind": "code",
                        "title": "读：坏数据要跳过而不是崩",
                        "code": """bool load(const std::string& path) {
    std::ifstream in(path);
    if (!in) return false;               // 首次运行没有文件，正常

    items_.clear();
    std::string line;
    while (std::getline(in, line)) {
        if (line.empty()) continue;
        std::istringstream ss(line);
        Transaction t;
        std::string amount;

        std::getline(ss, t.date, ',');
        std::getline(ss, t.category, ',');
        std::getline(ss, amount, ',');
        std::getline(ss, t.note, ',');

        try {
            t.amount = std::stod(amount);
        } catch (const std::exception&) {
            continue;                    // 这一行坏了，跳过
        }
        items_.push_back(t);
    }
    return true;
}""",
                        "narration": "读盘的关键是容错。文件不存在直接返回，因为第一次运行本来就该是空的。逐行读，用 istringstream 按逗号切分。最关键的是一处 try catch：金额解析失败就跳过这一行，而不是让整个程序崩掉。真实世界的数据文件经常被人手工编辑坏，能跳过坏行继续读，比直接崩溃友好得多。",
                    },
                    {
                        "kind": "recap",
                        "title": "本课回顾",
                        "items": [
                            "小工具优先选人可读的格式（CSV）",
                            "打开失败要返回错误，让上层提示",
                            "读盘必须容错：坏行跳过，别让程序崩",
                        ],
                        "narration": "数据能存能读了。最后一课把界面和校验补上，让它真正好用。",
                    },
                ],
            },
            {
                "id": "l50",
                "title": "收尾：主循环、输入校验与交付",
                "minutes": 6,
                "tags": ["主循环", "输入校验", "交付"],
                "pages": [
                    {
                        "kind": "cover",
                        "title": "收尾与交付",
                        "subtitle": "主循环 · 校验 · 中文字宽",
                        "narration": "最后一块拼图是界面层。程序好不好用，一半取决于这里：输入错了能不能重新输入，输出能不能对齐。",
                    },
                    {
                        "kind": "code",
                        "title": "输入校验：绝不相信用户",
                        "code": """int readInt(const std::string& prompt, int lo, int hi) {
    while (true) {
        std::string s = readLine(prompt);
        try {
            int v = std::stoi(s);
            if (v >= lo && v <= hi) return v;
        } catch (const std::exception&) {
            // 解析失败，继续问
        }
        std::cout << "  请输入 " << lo << " 到 " << hi
                  << " 之间的数字\\n";
    }
}

double readAmount(const std::string& prompt) {
    while (true) {
        std::string s = readLine(prompt);
        try { return std::stod(s); }
        catch (const std::exception&) {
            std::cout << "  金额格式不对，例如 12.5 或 -30\\n";
        }
    }
}""",
                        "narration": "输入校验的唯一原则是：永远不相信用户输入。readInt 一直循环，直到拿到范围内的合法整数；失败时给出具体的提示，告诉用户正确格式长什么样。注意这里用的是 getline 加 stoi，而不是直接 cin 读整数，因为 cin 失败后会进入错误状态，后面的读取全部失效，我们在输入输出那课专门讲过。",
                    },
                    {
                        "kind": "code",
                        "title": "中文字符串的列对齐",
                        "code": """// 终端里一个汉字占两格宽，用 string::size() 算宽度会错位
int displayWidth(const std::string& s) {
    int w = 0;
    for (unsigned char c : s) {
        if (c < 0x80) w += 1;              // ASCII 一格
        else if ((c & 0xC0) != 0x80) w += 2; // UTF-8 首字节，汉字两格
    }
    return w;
}

std::string pad(const std::string& s, int width) {
    std::string out = s;
    int w = displayWidth(s);
    if (w > width) {
        while (!out.empty() && displayWidth(out) > width) out.pop_back();
        return out;
    }
    out.append(static_cast<std::size_t>(width - w), ' ');
    return out;
}""",
                        "narration": "这个细节很多人栽过：终端里一个汉字占两格，但 string 的 size 返回的是字节数，一个汉字占三字节。直接用它算宽度，表格必然错位。解决办法是自己数显示宽度：ASCII 算一格，UTF-8 的多字节字符算两格。这个函数只有十来行，但能让输出立刻显得专业。",
                    },
                    {
                        "kind": "term",
                        "title": "跑起来的样子",
                        "lines": [
                            "$ g++ -std=c++20 -O2 -Wall account_book.cpp -o account_book.exe",
                            "$ ./account_book.exe",
                            "",
                            "  1. 记一笔        2. 看明细",
                            "请选择: 2",
                            "  No  日期         分类        金额        备注",
                            "  ------------------------------------------------",
                            "  1   2024-05-01   餐饮        -32.50      午餐",
                            "  2   2024-05-02   工资        8000.00     五月工资",
                            "",
                            "请选择: 4",
                            "  收入 8000.00   支出 -32.50   结余 7967.50",
                        ],
                        "narration": "这是程序跑起来的样子。编译只要一行命令，注意要加 W all 打开警告，我们这个程序是零警告通过的。表格对齐、金额两位小数、收支分开显示，这些细节决定了它看起来像一个正经工具，还是一个课后作业。",
                    },
                    {
                        "kind": "bullets",
                        "title": "交付前再检查一遍",
                        "items": [
                            ("零警告编译", "-Wall -Wextra 一条警告都没有"),
                            ("边界情况", "空账本、删除不存在的编号、金额输入字母"),
                            ("数据损坏", "手工把 CSV 改坏，程序还能启动"),
                            ("写清楚用法", "README 里说明编译命令和数据文件格式"),
                        ],
                        "narration": "交付前自查四件事：打开全部警告编译一遍，确保零警告；测边界情况，空账本、删不存在的编号、金额输入字母这些都不能崩；故意把 CSV 改坏，看程序还能不能启动；最后写一个简短的 README，说明怎么编译、数据文件长什么样。这四件事做完，它就从练习变成了作品。",
                    },
                    {
                        "kind": "recap",
                        "title": "全课回顾",
                        "items": [
                            "前面 13 章的知识，在这个项目里全部用上了",
                            "类型与容器：Transaction + vector",
                            "引用与 const：所有只读方法",
                            "异常容错：坏行跳过、输入重试",
                            "下一步：给它加月预算、导出 CSV 报表、做图形界面",
                        ],
                        "narration": "到这里，五十节课全部结束。你从写第一个 Hello World，走到了一个能真实使用的程序。接下来最重要的不是继续看课，而是动手改它：加个月度预算，加个导出报表，或者把界面换成图形化的。改着改着，你就真的会 C++ 了。",
                    },
                ],
            },
        ],
    },
]
