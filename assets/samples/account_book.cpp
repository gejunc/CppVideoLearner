// account_book.cpp —— 命令行记账程序
// 编译：g++ -std=c++20 -O2 -Wall -Wextra account_book.cpp -o account_book.exe
//
// 功能：记一笔账、列出明细、删除、按分类统计、按月汇总、存盘读盘
// 数据文件：ledger.csv，格式为  日期,分类,金额,备注

#include <algorithm>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <sstream>
#include <string>
#include <vector>

// ---------------------------------------------------------------- 数据
struct Transaction {
    std::string date;       // 2024-05-01
    std::string category;   // 餐饮 / 交通 / 工资
    double      amount = 0; // 正数收入，负数支出
    std::string note;
};

// ---------------------------------------------------------------- 账本
class Ledger {
public:
    void add(const Transaction& t) { items_.push_back(t); }

    bool remove(std::size_t no) {           // no 从 1 开始
        if (no == 0 || no > items_.size()) return false;
        items_.erase(items_.begin() + static_cast<long>(no - 1));
        return true;
    }

    double total() const {
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

    // 按分类汇总，金额从多到少
    std::vector<std::pair<std::string, double>> byCategory() const {
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
    }

    // 按月汇总：key 是 "2024-05"
    std::vector<std::pair<std::string, double>> byMonth() const {
        std::vector<std::pair<std::string, double>> out;
        for (const auto& t : items_) {
            if (t.date.size() < 7) continue;
            std::string key = t.date.substr(0, 7);
            auto it = std::find_if(out.begin(), out.end(),
                [&](const auto& p) { return p.first == key; });
            if (it == out.end()) out.emplace_back(key, t.amount);
            else                 it->second += t.amount;
        }
        std::sort(out.begin(), out.end(),
                  [](const auto& a, const auto& b) { return a.first < b.first; });
        return out;
    }

    const std::vector<Transaction>& items() const { return items_; }

    // ------------------------------------------------------------ 持久化
    bool save(const std::string& path) const {
        std::ofstream out(path);
        if (!out) return false;
        for (const auto& t : items_) {
            out << t.date << ',' << t.category << ','
                << t.amount << ',' << t.note << '\n';
        }
        return true;
    }

    bool load(const std::string& path) {
        std::ifstream in(path);
        if (!in) return false;              // 首次运行没有文件，很正常
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
                continue;                   // 坏行直接跳过
            }
            items_.push_back(t);
        }
        return true;
    }

private:
    std::vector<Transaction> items_;
};

// ---------------------------------------------------------------- 显示
namespace {

// 终端里中文占两个字符宽，用它把列对齐
int displayWidth(const std::string& s) {
    int w = 0;
    for (unsigned char c : s) {
        if (c < 0x80) w += 1;
        else if ((c & 0xC0) != 0x80) w += 2;   // 非 ASCII 按两格宽算
    }
    return w;
}

std::string pad(const std::string& s, int width) {
    std::string out = s;
    int w = displayWidth(s);
    if (w > width) {
        // 截断到宽度以内（按字节截，够用即可）
        while (!out.empty() && displayWidth(out) > width) out.pop_back();
        return out;
    }
    out.append(static_cast<std::size_t>(width - w), ' ');
    return out;
}

void printList(const Ledger& ledger) {
    const auto& items = ledger.items();
    if (items.empty()) {
        std::cout << "  （还没有记录）\n";
        return;
    }
    std::cout << "  " << pad("No", 4) << pad("日期", 13)
              << pad("分类", 12) << pad("金额", 12) << "备注\n";
    std::cout << "  " << std::string(56, '-') << '\n';
    for (std::size_t i = 0; i < items.size(); ++i) {
        const auto& t = items[i];
        std::ostringstream amt;
        amt << std::fixed << std::setprecision(2) << t.amount;
        std::cout << "  " << pad(std::to_string(i + 1), 4)
                  << pad(t.date, 13) << pad(t.category, 12)
                  << pad(amt.str(), 12) << t.note << '\n';
    }
    std::cout << "  " << std::string(56, '-') << '\n';
}

void printSummary(const Ledger& ledger) {
    std::cout << std::fixed << std::setprecision(2);
    std::cout << "  收入 " << ledger.sumOf(true)
              << "   支出 " << ledger.sumOf(false)
              << "   结余 " << ledger.total() << "\n";

    auto cats = ledger.byCategory();
    if (!cats.empty()) {
        std::cout << "  —— 按分类 ——\n";
        for (const auto& [name, sum] : cats)
            std::cout << "  " << pad(name, 14) << sum << '\n';
    }

    auto months = ledger.byMonth();
    if (!months.empty()) {
        std::cout << "  —— 按月 ——\n";
        for (const auto& [m, sum] : months)
            std::cout << "  " << pad(m, 14) << sum << '\n';
    }
}

// 读一行并去掉首尾空白
std::string readLine(const std::string& prompt) {
    std::cout << prompt;
    std::string line;
    if (!std::getline(std::cin, line)) return {};
    const auto b = line.find_first_not_of(" \t\r");
    if (b == std::string::npos) return {};
    const auto e = line.find_last_not_of(" \t\r");
    return line.substr(b, e - b + 1);
}

int readInt(const std::string& prompt, int lo, int hi) {
    while (true) {
        std::string s = readLine(prompt);
        try {
            int v = std::stoi(s);
            if (v >= lo && v <= hi) return v;
        } catch (const std::exception&) {
            // 继续问
        }
        std::cout << "  请输入 " << lo << " 到 " << hi << " 之间的数字\n";
    }
}

double readAmount(const std::string& prompt) {
    while (true) {
        std::string s = readLine(prompt);
        try {
            return std::stod(s);
        } catch (const std::exception&) {
            std::cout << "  金额格式不对，例如 12.5 或 -30\n";
        }
    }
}

}  // namespace

// ---------------------------------------------------------------- 主循环
int main() {
    const std::string dataFile = "ledger.csv";
    Ledger ledger;
    ledger.load(dataFile);

    const char* menu =
        "\n================ 记账本 ================\n"
        "  1. 记一笔        2. 看明细\n"
        "  3. 删除一笔      4. 统计\n"
        "  5. 保存          0. 退出\n"
        "========================================\n";

    while (true) {
        std::cout << menu;
        int choice = readInt("请选择: ", 0, 5);

        if (choice == 0) break;

        if (choice == 1) {
            Transaction t;
            t.date = readLine("日期 (2024-05-01): ");
            if (t.date.empty()) t.date = "----/--/--";
            t.category = readLine("分类 (餐饮/交通/工资): ");
            if (t.category.empty()) t.category = "未分类";
            t.amount = readAmount("金额 (支出填负数): ");
            t.note = readLine("备注: ");
            ledger.add(t);
            std::cout << "  已记一笔\n";
        } else if (choice == 2) {
            printList(ledger);
        } else if (choice == 3) {
            printList(ledger);
            int no = readInt("删除第几笔（0 取消）: ", 0,
                             static_cast<int>(ledger.items().size()));
            if (no == 0) continue;
            std::cout << (ledger.remove(static_cast<std::size_t>(no))
                          ? "  已删除\n" : "  没有这一笔\n");
        } else if (choice == 4) {
            printSummary(ledger);
        } else if (choice == 5) {
            std::cout << (ledger.save(dataFile)
                          ? "  已保存到 ledger.csv\n" : "  保存失败\n");
        }
    }

    if (ledger.save(dataFile)) std::cout << "已保存，再见。\n";
    return 0;
}
