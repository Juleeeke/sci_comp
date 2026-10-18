# R 语言学习指南

> 面向第一次学习 R 的读者。本文以 **Base R**（R 自带的功能）为主，不依赖额外安装的包。建议打开 R 控制台，按章节亲自运行代码；代码块中的对象通常在本块内创建。文中涉及文件读写的示例会在当前工作目录生成文件。

## 目录

1. [开始使用 R](#1-开始使用-r)
2. [语法、变量与运算符](#2-语法变量与运算符)
3. [数据类型与类型转换](#3-数据类型与类型转换)
4. [向量：R 的基本单位](#4-向量r-的基本单位)
5. [索引与子集](#5-索引与子集)
6. [矩阵、数组、列表与因子](#6-矩阵数组列表与因子)
7. [数据框与数据整理](#7-数据框与数据整理)
8. [缺失值、特殊值与逻辑判断](#8-缺失值特殊值与逻辑判断)
9. [字符串、日期和时间](#9-字符串日期和时间)
10. [流程控制与函数](#10-流程控制与函数)
11. [apply 家族与分组计算](#11-apply-家族与分组计算)
12. [数据导入、导出与工作目录](#12-数据导入导出与工作目录)
13. [常用统计与数学函数](#13-常用统计与数学函数)
14. [基础绘图](#14-基础绘图)
15. [公式、线性回归与模型对象](#15-公式线性回归与模型对象)
16. [包、帮助与调试](#16-包帮助与调试)
17. [常见错误与良好习惯](#17-常见错误与良好习惯)
18. [函数速查表与练习](#18-函数速查表与练习)

## 1. 开始使用 R

R 是用于数据处理、统计分析、绘图和编程的语言。你可以在 R 控制台逐行输入，也可以将代码写入 `.R` 文件后运行。`.Rmd`/Quarto 文档适合将代码、结果和文字放在同一份报告中；本指南先学习 `.R` 脚本。

```r
1 + 2                 # 在控制台直接得到 3
x <- 10               # 赋值，常用 <-
print(x)              # 明确打印对象
cat("x =", x, "\n")  # 拼接文字并换行
```

- `#` 后面到行末是注释；R 区分大小写：`score` 和 `Score` 是不同名字。
- 一行可以写一个表达式；多行语句由括号、花括号等连接。
- 在控制台运行 `?mean` 查看帮助；`help.start()` 打开帮助首页。
- 用 `Rscript 文件名.R` 在终端运行脚本。运行脚本时，想看到中间结果，显式调用 `print()` 或 `cat()`。
- `sessionInfo()` 查看 R 版本、平台和已加载的包；`getwd()` 查看当前工作目录。

**第一个完整脚本：**

```r
scores <- c(76, 85, 91, 88)
avg <- mean(scores)
cat("平均分：", avg, "\n")
cat("高于平均分的人数：", sum(scores > avg), "\n")
```

## 2. 语法、变量与运算符

### 2.1 命名与赋值

```r
student_score <- 88
student_score = 90   # 在简单赋值中也可以使用 =；函数传参通常用 =
100 -> total         # 右赋值可以用，但通常不推荐混用写法
```

变量名通常以字母或 `.` 开头，可包含字母、数字、`.`、`_`；不能以数字开头。尽量使用有意义的名称，如 `mean_height`。不要给变量取 `mean`、`data` 等常用函数名，以免阅读和调用时混淆。

常量：`TRUE`/`FALSE`、`NULL`、`NA`、`Inf`、`NaN`。`T`、`F` 虽然通常可用，但能被重新赋值，建议始终写全称。

### 2.2 常用运算符

| 类别 | 运算符 | 示例与含义 |
| --- | --- | --- |
| 算术 | `+` `-` `*` `/` `^` | `2 ^ 3` 是 8 |
| 整除与取余 | `%/%` `%%` | `7 %/% 3` 是 2；`7 %% 3` 是 1 |
| 比较 | `==` `!=` `<` `<=` `>` `>=` | `3 == 3` 是 `TRUE` |
| 向量逻辑 | `&` `\|` `!` | 对每个元素分别计算；`!TRUE` 是 `FALSE` |
| 单值短路逻辑 | `&&` `\|\|` | 常用于 `if` 条件，右侧可能不执行 |
| 成员判断 | `%in%` | `2 %in% c(1, 2, 3)` 是 `TRUE` |
| 序列 | `:` | `1:5` 生成 1 到 5 |
| 矩阵乘法 | `%*%` | 与逐元素 `*` 不同 |
| 原生管道 | `\|>` | `x \|> mean()` 把 `x` 传给函数 |

```r
v <- c(2, 4, 6)
v + 1                 # 3 5 7：逐元素计算
v > 3                 # FALSE TRUE TRUE
v > 3 & v < 6         # FALSE TRUE FALSE
2 %in% v             # TRUE
sum(v > 3)           # TRUE 在求和时按 1 计，结果为 2
v |> mean()           # 等价于 mean(v)；原生管道需要 R 4.1.0 或更新版本
```

比较小数时，浮点误差可能导致 `0.1 + 0.2 == 0.3` 为 `FALSE`，可用 `isTRUE(all.equal(0.1 + 0.2, 0.3))` 判断是否在容差内接近。

## 3. 数据类型与类型转换

### 3.1 常见基本类型

| 类型 | 示例 | 检查函数 |
| --- | --- | --- |
| 逻辑值 `logical` | `TRUE`、`FALSE` | `is.logical()` |
| 整数 `integer` | `3L` | `is.integer()` |
| 双精度数 `double` | `3`、`3.14` | `is.double()` |
| 字符串 `character` | `"R"` | `is.character()` |
| 复数 `complex` | `1 + 2i` | `is.complex()` |

```r
typeof(3)       # "double"；未加 L 的普通数字通常是 double
typeof(3L)      # "integer"
class(3L)       # "integer"；class 描述对象行为，typeof 描述底层类型
str(list(a = 3, b = "R")) # 快速查看对象结构
```

`class()` 和 `typeof()` 可能不同，例如因子的底层类型是整数，但类是 `factor`。用 `str()` 看复杂对象最方便。

### 3.2 类型转换与混合类型

```r
as.numeric("12.5")   # 12.5
as.character(12.5)   # "12.5"
as.integer(3.9)      # 3：截去小数部分，不是四舍五入
round(3.9)           # 4
c(1, TRUE, "3")      # 全部转为字符："1" "TRUE" "3"
```

同一个**原子向量**只能存一种基本类型；混合时通常按 `logical → integer → double → character` 方向转换。不能转换的文本会得到 `NA` 并常伴随警告：

```r
suppressWarnings(as.numeric("abc"))  # NA；实际分析中应检查为何无法转换
```

## 4. 向量：R 的基本单位

### 4.1 创建向量和序列

```r
x <- c(2, 4, 6)                  # c() 拼接
1:5                              # 1 2 3 4 5
seq(from = 0, to = 1, by = 0.25) # 0 0.25 0.5 0.75 1
seq_len(5)                       # 安全地生成 1 到 5
rep(c("A", "B"), times = 3)       # A B A B A B
rep(c("A", "B"), each = 3)        # A A A B B B
numeric(4)                       # 长度为 4、初始值为 0 的数值向量
length(x)                        # 元素个数
```

`1:n` 在 `n = 0` 时会得到 `c(1, 0)`；循环索引更适合用 `seq_len(n)`。`seq_along(x)` 根据对象长度生成索引。

### 4.2 向量化与回收

```r
x <- c(2, 4, 6)
x * 2                # 4 8 12
x + c(10, 20, 30)    # 12 24 36
sqrt(x)              # 对每个元素开方
pmax(x, 5)           # 逐元素取较大值：5 5 6
```

长度不同的向量运算会按较短向量循环使用元素。若长向量长度不是短向量长度的整数倍，通常会有警告。分析时尽量确保长度相同，或明确只使用长度为 1 的标量。

### 4.3 名称与常用汇总

```r
scores <- c(Alice = 82, Bob = 91, Chen = 76)
names(scores)             # 元素名称
scores["Bob"]            # 按名字选取
sum(scores)               # 总和
mean(scores)              # 均值
min(scores); max(scores)  # 最小值、最大值
range(scores)             # 最小值和最大值
sort(scores)              # 排序后的值
order(scores)             # 排序后的原位置
unique(c(1, 2, 2, 3))    # 去重
table(c("A", "B", "A"))  # 频数表
```

## 5. 索引与子集

R 的位置索引从 **1** 开始。`[` 通常返回子集；`[[` 从列表/数据框中取单个元素；`$` 按名称取列表元素或数据框列。

```r
x <- c(2, 4, 6, 8, 10)
x[1]                     # 第一个元素：2
x[c(2, 4)]               # 位置 2、4：4 8
x[-c(1, 3, 5)]           # 排除位置 1、3、5：4 8
x[c(FALSE, TRUE, FALSE, TRUE, FALSE)]  # 逻辑筛选：4 8
x[x > 5]                 # 满足条件的值：6 8 10
x[2] <- 40               # 修改第二个元素
```

**注意：**正位置和负位置不能混合在同一索引中（0 例外）。逻辑索引长度不足时也可能被回收，所以应检查条件向量长度。找位置用 `which(x > 5)`；判断是否存在用 `any(x > 5)`，是否全部满足用 `all(x > 5)`。

```r
people <- list(name = "李华", scores = c(80, 90))
people["scores"]     # 子列表，类型仍是 list
people[["scores"]]   # 内部向量，类型是 numeric
people$scores        # 与上行效果相近；动态列名优先用 [[ ]]

field <- "scores"
people[[field]]      # 根据变量 field 中的字符串取元素
```

二维对象使用 `[行, 列]`；留空表示全部行或列：

```r
m <- matrix(1:6, nrow = 2)
m[1, 2]                    # 第 1 行第 2 列
m[, 2]                     # 第 2 列，默认会简化成向量
m[, 2, drop = FALSE]       # 保持矩阵形状
```

## 6. 矩阵、数组、列表与因子

### 6.1 矩阵和数组

矩阵是二维、元素同类型的对象；R 默认**按列**填充矩阵。

```r
m <- matrix(1:6, nrow = 2, ncol = 3)
dim(m)              # 2 3
nrow(m); ncol(m)    # 行数、列数
rownames(m) <- c("甲", "乙")
colnames(m) <- c("A", "B", "C")
rowSums(m)          # 每行求和
colMeans(m)         # 每列求平均
t(m)                # 转置
m * 2               # 逐元素乘法
t(m) %*% m          # 矩阵乘法
```

```r
a <- array(1:24, dim = c(2, 3, 4)) # 2×3×4 三维数组
dim(a)
a[1, 2, 3]
```

### 6.2 列表

列表可装不同类型、不同长度的对象，也能嵌套。

```r
record <- list(id = 101, name = "小王", scores = c(85, 92))
names(record)
record$scores
length(record)       # 顶层元素数：3
record[["name"]] <- "小李"
record$passed <- TRUE # 新增元素
record$passed <- NULL # 删除元素
```

### 6.3 因子

因子表示类别及其允许的水平（`levels`），有序因子还表示类别顺序。

```r
group <- factor(c("对照", "实验", "对照"), levels = c("对照", "实验"))
levels(group)
table(group)

grade <- factor(c("中", "高", "低"),
                levels = c("低", "中", "高"), ordered = TRUE)
grade[1] < grade[2]  # TRUE，因为中 < 高
```

**易错点：**因子底层是整数编码。`as.numeric(factor(c("10", "20")))` 得到的是编码 `1 2`；若要数值 `10 20`，用 `as.numeric(as.character(f))`，并检查原始值是否真的都是数字。

### 6.4 结构比较

| 结构 | 维度 | 元素类型 | 常见用途 |
| --- | --- | --- | --- |
| 原子向量 | 一维 | 同一类型 | 一组数值、字符或逻辑值 |
| 矩阵/数组 | 二维/多维 | 同一类型 | 数值计算、图像或多维数据 |
| 列表 | 一维、可嵌套 | 可不同 | 混合结果、模型输出 |
| 数据框 | 二维 | 每列内部同一类型，列之间可不同 | 表格数据 |
| 因子 | 一维 | 分类水平及编码 | 类别变量、统计建模 |

## 7. 数据框与数据整理

### 7.1 建立与查看数据框

```r
students <- data.frame(
  name = c("甲", "乙", "丙", "丁"),
  group = c("A", "B", "A", "B"),
  score = c(85, 92, NA, 76),
  passed = c(TRUE, TRUE, NA, FALSE)
)

head(students)       # 前几行
tail(students)       # 后几行
str(students)        # 各列结构
summary(students)    # 各列摘要
dim(students)        # 行数、列数
names(students)      # 列名
```

同一列应尽量保持一种语义和类型。`data.frame()` 中各列必须具有兼容的行数；不要依赖隐式回收来补齐数据。

### 7.2 选列、筛行、新增列

```r
students$score                 # 一列向量
students[["score"]]           # 一列向量，适合动态列名
students[, "score", drop = FALSE] # 一列数据框
students[1:2, c("name", "score")]

students[!is.na(students$score) & students$score >= 80, ]
students$bonus_score <- students$score + 5
```

在数据框里筛选含 `NA` 的条件时，应先用 `!is.na()`，否则条件中的 `NA` 可能让结果出现一行全 `NA` 的占位。`subset(students, !is.na(score) & score >= 80, select = c(name, score))` 写起来方便，但在可复用函数里，显式的 `[` 更易控制变量来源。

### 7.3 排序、合并、分组汇总

```r
students <- data.frame(
  id = 1:4, group = c("A", "B", "A", "B"),
  score = c(85, 92, 88, 76)
)

students[order(students$score), ]                 # 分数升序
students[order(students$score, decreasing = TRUE), ] # 降序

aggregate(score ~ group, data = students, FUN = mean) # 按组均值
table(students$group)                            # 按组计数

info <- data.frame(id = c(1, 2, 4), city = c("北京", "上海", "广州"))
merge(students, info, by = "id", all.x = TRUE)  # 以学生表为主表连接
```

`aggregate(score ~ group, ...)` 默认忽略公式中涉及的缺失行；汇总前要想清楚缺失值如何处理。`merge()` 依赖键列，先检查键是否重复，否则一对多/多对多会扩增行数。

### 7.4 添加行、列与改名

```r
df <- data.frame(id = 1:2, score = c(80, 90))
df$status <- c("合格", "优秀")
names(df)[names(df) == "score"] <- "exam_score"
df <- rbind(df, data.frame(id = 3, exam_score = 75, status = "合格"))
df2 <- cbind(df, rank = c(2, 1, 3))
```

`rbind()` 通常要求列名和类型兼容；`cbind()` 按当前行顺序拼接，不会依据 `id` 自动对齐。按键对齐请用 `merge()`。

## 8. 缺失值、特殊值与逻辑判断

- `NA`：缺失或未知；`NaN`：不是一个有效数值，例如 `0/0`；`Inf`/`-Inf`：正/负无穷，例如 `1/0`。`NULL` 表示对象不存在或空对象，与长度为 1 的 `NA` 不同。
- 不要用 `x == NA` 判断缺失；因为与未知值比较得到的仍是未知。用 `is.na(x)`。

```r
x <- c(2, NA, 6)
is.na(x)                 # FALSE TRUE FALSE
sum(is.na(x))            # 缺失个数：1
x[!is.na(x)]            # 非缺失值
mean(x)                 # NA
mean(x, na.rm = TRUE)   # 4
is.nan(0/0)             # TRUE
is.finite(c(1, Inf, NA, NaN)) # TRUE FALSE FALSE FALSE
```

```r
df <- data.frame(a = c(1, NA, 3), b = c(4, 5, NA))
complete.cases(df)       # 哪些行全部非缺失
na.omit(df)              # 删除含缺失的行；可能丢失大量样本
ifelse(is.na(df$a), 0, df$a) # 按条件替换成 0；仅当 0 在业务上有意义时使用
```

`is.na(NaN)` 也是 `TRUE`；如果需要单独识别 `NaN`，用 `is.nan()`。`all.equal()` 返回近似比较的描述或 `TRUE`，因此常搭配 `isTRUE()`。

## 9. 字符串、日期和时间

### 9.1 字符串

```r
txt <- c(" R语言 ", "数据分析")
nchar(txt)                    # 字符数
trimws(txt)                   # 去除首尾空白
toupper("abc")               # "ABC"
paste("R", "语言")            # "R 语言"
paste0("R", "语言")           # "R语言"
sprintf("分数：%.1f", 88.25) # "分数：88.2"（显示精度受格式影响）
strsplit("A,B,C", ",")[[1]] # 拆分后取向量
substr("abcdef", 2, 4)      # "bcd"
```

```r
x <- c("cat", "car", "dog")
grepl("^ca", x)              # 是否匹配：TRUE TRUE FALSE
grep("^ca", x)               # 匹配位置：1 2
sub("a", "A", "banana")     # 替换第一个："bAnana"
gsub("a", "A", "banana")    # 替换全部："bAnAnA"
```

`grepl()` 等函数默认使用正则表达式，`.`、`*` 等字符有特殊含义。若要按字面文本匹配，可考虑 `fixed = TRUE`，例如 `grepl("a.b", x, fixed = TRUE)`。

### 9.2 日期与时间

```r
d <- as.Date("2026-10-08")
d + 7                         # 七天后
as.Date("08/10/2026", format = "%d/%m/%Y")
format(d, "%Y年%m月%d日")
as.integer(as.Date("2026-10-15") - d) # 日期差，按天

now <- Sys.time()              # 当前日期时间，带时区信息
format(now, "%Y-%m-%d %H:%M:%S")
```

`Date` 表示日期；`POSIXct`/`POSIXlt` 表示日期时间。处理跨时区数据时应明确时区，解析时可以使用 `as.POSIXct("2026-10-08 09:00:00", tz = "Asia/Shanghai")`。

## 10. 流程控制与函数

### 10.1 条件分支

`if` 需要一个长度为 1、且不是 `NA` 的逻辑值。

```r
score <- 82
if (score >= 90) {
  level <- "优秀"
} else if (score >= 60) {
  level <- "合格"
} else {
  level <- "不合格"
}
print(level)

scores <- c(55, 82, 96)
ifelse(scores >= 60, "合格", "不合格") # 向量化选择
```

`ifelse()` 适合简单的逐元素选择；复杂分支、严格保留日期/类等属性时，使用普通 `if` 或先创建结果向量再按条件赋值。

### 10.2 循环

```r
x <- c(2, 4, 6)
out <- numeric(length(x))       # 预先分配，避免循环中不断增长
for (i in seq_along(x)) {
  out[i] <- x[i]^2
}
print(out)

n <- 1
while (n < 5) {
  n <- n + 1
}
```

`break` 退出循环；`next` 跳到下一次迭代。R 也有 `repeat { ... }`，必须在适当条件下 `break`，否则会一直执行。

### 10.3 自定义函数

```r
safe_mean <- function(x, remove_missing = TRUE) {
  if (!is.numeric(x)) stop("x 必须是数值向量")
  if (length(x) == 0L) return(NA_real_)
  mean(x, na.rm = remove_missing)
}

safe_mean(c(1, NA, 3))  # 2
```

- `function(参数) { ... }` 定义函数；可给参数提供默认值。
- 函数返回最后一个表达式的值，或用 `return()` 提前返回。
- 参数匹配可以按名称、位置或部分名称；为减少歧义，优先用完整名称。
- `...` 接受并转交额外参数，例如 `my_sum <- function(...) sum(...)`。
- 函数默认按**词法作用域**查找外层对象；为可复用和可测试，尽量通过参数传入依赖。

```r
make_adder <- function(n) {
  function(x) x + n
}
add_5 <- make_adder(5)
add_5(10) # 15：内层函数记住了定义时的 n
```

## 11. apply 家族与分组计算

这组函数对元素、行列或分组重复调用函数。它们不一定比循环快，主要价值是表达意图清楚。

```r
m <- matrix(1:6, nrow = 2)
apply(m, 1, sum)    # 按行；MARGIN = 1
apply(m, 2, mean)   # 按列；MARGIN = 2
rowSums(m)          # 常见行汇总的专用函数
colMeans(m)         # 常见列汇总的专用函数
```

`apply()` 用在混合类型数据框上可能先把数据框转成矩阵，导致所有列转成同一类型。混合列宜用 `lapply()` 或明确选数值列。

```r
items <- list(a = 1:3, b = c(4, 5))
lapply(items, sum)           # 结果始终是列表
sapply(items, sum)           # 尝试简化为向量/矩阵
vapply(items, sum, numeric(1)) # 明确要求每次返回一个数值，更稳定

group <- c("A", "B", "A", "B")
score <- c(80, 90, 100, 70)
tapply(score, group, mean)   # 按组汇总
split(score, group)          # 按组拆分为列表
```

`mapply()` 把函数并行作用于多个输入：

```r
mapply(function(a, b) a + b, c(1, 2), c(10, 20)) # 11 22
```

## 12. 数据导入、导出与工作目录

### 12.1 路径

```r
getwd()                          # 当前工作目录
file.path("data", "scores.csv") # 按操作系统规则拼接路径
file.exists("scores.csv")       # 检查文件是否存在
list.files(".")                 # 列出当前目录内容
```

相对路径以**运行时工作目录**为起点，而不一定以脚本所在目录为起点。最好在项目中保持固定目录结构，运行前确认 `getwd()`；不要在共享脚本里硬编码别人的绝对路径。

### 12.2 CSV 与文本文件

```r
sample_data <- data.frame(id = 1:2, score = c(88, 92))
write.csv(sample_data, "scores.csv", row.names = FALSE, fileEncoding = "UTF-8")
read_back <- read.csv("scores.csv", stringsAsFactors = FALSE,
                      fileEncoding = "UTF-8", check.names = FALSE)
str(read_back)
```

`read.csv()` 默认第一行为列名、逗号分隔。制表符文件可用 `read.delim()`；更通用的 `read.table()` 需要明确 `header`、`sep` 等参数。检查导入结果时先看 `dim()`、`names()`、`str()`、`head()` 和缺失数量。CSV 不保存因子水平、日期类等完整 R 对象属性，读回后可能需要重新指定类型。

```r
writeLines(c("第一行", "第二行"), "note.txt", useBytes = TRUE)
readLines("note.txt", warn = FALSE)
```

### 12.3 保存 R 对象

```r
model_data <- data.frame(x = 1:3, y = c(2, 4, 6))
saveRDS(model_data, "model_data.rds")
restored <- readRDS("model_data.rds")
identical(model_data, restored) # TRUE
```

`saveRDS()`/`readRDS()` 适合保存、读取单个对象，并让调用者决定读回后的变量名。`save()`/`load()` 可以处理多个具名对象；`load()` 会把原变量名放进目标环境，使用前应了解文件内容。

## 13. 常用统计与数学函数

```r
x <- c(2, 4, 4, 6, 9)
sum(x)             # 总和
prod(x)            # 乘积
mean(x)            # 均值
median(x)          # 中位数
var(x)             # 样本方差，分母 n - 1
sd(x)              # 样本标准差
quantile(x, probs = c(0.25, 0.5, 0.75)) # 分位数
summary(x)         # 综合摘要
```

```r
sqrt(9); abs(-3); log(exp(1)); exp(1)
floor(3.8); ceiling(3.2); round(3.14159, 2)
cumsum(c(1, 2, 3))              # 累积和：1 3 6
diff(c(2, 5, 9))                # 相邻差：3 4
which.max(c(4, 8, 6))          # 最大值的位置：2
```

### 13.1 随机数与可复现

```r
set.seed(42)                   # 固定随机种子，便于复现
sample(1:10, size = 3)         # 不放回抽样
runif(5, min = 0, max = 1)     # 均匀分布
rnorm(5, mean = 0, sd = 1)     # 正态分布
dnorm(0)                      # 标准正态在 0 处的密度
pnorm(1.96)                   # 标准正态累计概率
qnorm(0.975)                  # 97.5% 分位数
```

`d*` 通常为密度/概率质量，`p*` 为累计概率，`q*` 为分位数，`r*` 为随机抽样，例如正态分布对应 `dnorm`、`pnorm`、`qnorm`、`rnorm`。随机模拟应记录种子、R 版本和关键参数。

### 13.2 相关与列联表

```r
x <- c(1, 2, 3, 4)
y <- c(2, 3, 5, 7)
cor(x, y)                 # 皮尔逊相关系数
cov(x, y)                 # 协方差
table(c("男", "女", "男")) # 单变量频数
```

`cor()` 计算的是相关程度，不代表因果关系。真实数据有缺失时需明确 `use` 参数，例如 `use = "complete.obs"`，并检查实际参与计算的样本数。

## 14. 基础绘图

Base R 的绘图函数会在图形设备上绘制；在交互环境中通常显示在绘图窗口。

```r
x <- 1:10
y <- x^2
plot(x, y, main = "Square relationship", xlab = "x", ylab = "x^2",
     col = "steelblue", pch = 19)
lines(x, y, col = "tomato", lwd = 2)
abline(h = 50, lty = 2, col = "gray50")
legend("topleft", legend = "y = x²", col = "steelblue", pch = 19, bty = "n")
```

```r
v <- c(2, 4, 4, 6, 9, 10)
hist(v, breaks = 4, main = "Histogram", xlab = "Value")
boxplot(v, main = "Boxplot")
barplot(table(c("A", "B", "A", "C")), main = "Category counts")
```

图形保存时先打开设备、绘图，最后关闭设备：

```r
png("scatter.png", width = 800, height = 500)
plot(1:5, (1:5)^2, pch = 19, xlab = "x", ylab = "y")
dev.off()
```

矢量图可用 `pdf("plot.pdf")` 打开设备。中文字体显示取决于操作系统和图形设备，导出后要实际打开检查文字。

## 15. 公式、线性回归与模型对象

R 中的公式 `y ~ x` 表示用 `x` 解释或预测 `y`；`y ~ x1 + x2` 表示两个自变量。下面用内置数据集演示，重点是代码流程，不代表因果结论。

```r
fit <- lm(mpg ~ wt + hp, data = mtcars)
summary(fit)                         # 系数、拟合指标等
coef(fit)                            # 回归系数
fitted(fit)[1:3]                     # 前 3 个拟合值
residuals(fit)[1:3]                  # 前 3 个残差

new_cars <- data.frame(wt = c(2.5, 3.0), hp = c(100, 120))
predict(fit, newdata = new_cars)     # 对新数据预测
```

对系数与预测的解释需检查模型假设、变量单位、异常值和数据范围。`summary(fit)` 的显著性结果本身不能证明因果关系。二分类等其他模型可学习 `glm()`，但要先弄清 `family` 与响应变量含义。

## 16. 包、帮助与调试

### 16.1 包

```r
installed.packages()[, "Package"]  # 已安装包名称
# install.packages("包名")          # 首次安装或需要更新时运行，需要网络
# library(包名)                     # 每个新会话需要加载
stats::median(c(1, 3, 5))          # 包名::函数名，明确调用来源
```

`install.packages()` 安装到本机，`library()` 在当前会话加载。不同包可能有同名函数；`包名::函数名` 可以指定来源。长期项目应记录包版本，尤其是需要复现分析结果时。

### 16.2 查帮助

```r
?mean                # 函数帮助
help("mean")
help.search("regression") # 搜索主题
args(mean)          # 查看参数
example(mean)       # 运行帮助页示例
```

阅读帮助页可按 **Description → Usage → Arguments → Value → Examples** 的顺序；先确认函数返回什么类型，再把它接入自己的代码。

### 16.3 处理错误与调试

```r
sqrt("abc")          # 示例：会报错，提示输入类型不对
traceback()          # 出错后查看调用路径
```

上面第一行是**故意演示错误**，不要放入需要顺序运行的正式脚本。可以用 `stop()` 明确拒绝非法输入，用 `warning()` 提示非致命问题，用 `message()` 给出进度信息。`tryCatch()` 可捕获预期错误：

```r
result <- tryCatch(
  as.numeric("12"),
  error = function(e) NA_real_
)
```

不过 `as.numeric("abc")` 是警告加 `NA`，并非错误；调试时应先读懂错误/警告，而不是统一忽略。`browser()` 可在函数内设置交互断点。

## 17. 常见错误与良好习惯

| 情况 | 原因 | 建议 |
| --- | --- | --- |
| `object 'x' not found` | 对象尚未创建或拼写/大小写不同 | 从脚本开头运行，检查 `ls()` 与变量名 |
| `subscript out of bounds` | 索引超出范围 | 先检查 `length()`、`dim()`、`names()` |
| `mean(x)` 得到 `NA` | `x` 中有缺失 | 用 `is.na()` 检查；按分析目的决定是否 `na.rm = TRUE` |
| `if` 条件报长度或缺失错误 | 条件不是单个确定的 TRUE/FALSE | 用 `any()`、`all()`，或先处理 `NA` |
| 数值列变成字符列 | `c()`/矩阵混入字符，或导入识别错误 | 用 `str()` 检查，修正原始数据和导入参数 |
| 数据框筛选多出 `NA` 行 | 逻辑条件含 `NA` | 条件中明确加入 `!is.na()` |
| 合并后行数变多 | 键列重复导致一对多/多对多 | 合并前用 `anyDuplicated()`/`table()` 检查键 |
| 找不到 CSV 文件 | 工作目录与预期不同 | 检查 `getwd()`、`file.exists()`、路径拼写 |

建议养成以下习惯：

1. 把原始数据保留在单独目录，不手动覆盖；把清洗步骤写在脚本中。
2. 在脚本开头写明输入、输出、运行方法和关键参数；使用可读的变量名。
3. 每次导入后检查行列数、列类型、缺失、重复键和合理取值范围。
4. 随机过程使用 `set.seed()`；记录 `sessionInfo()` 和依赖包版本。
5. 不依赖控制台里临时残留的对象；从空会话运行整份脚本检验可复现性。
6. 不把警告一概屏蔽。先判断警告是否意味着数据丢失、类型变化或不可靠结果。

## 18. 函数速查表与练习

### 18.1 按任务查函数

| 任务 | 常用函数 |
| --- | --- |
| 创建和查看 | `c()`、`seq()`、`rep()`、`length()`、`str()`、`class()`、`typeof()` |
| 索引和筛选 | `[`、`[[`、`$`、`which()`、`%in%`、`subset()` |
| 判断缺失 | `is.na()`、`complete.cases()`、`anyNA()`、`na.omit()` |
| 排序去重 | `sort()`、`order()`、`unique()`、`duplicated()`、`anyDuplicated()` |
| 汇总统计 | `sum()`、`mean()`、`median()`、`sd()`、`var()`、`quantile()`、`summary()` |
| 表格操作 | `data.frame()`、`head()`、`names()`、`rbind()`、`cbind()`、`merge()` |
| 分组/批量 | `table()`、`aggregate()`、`split()`、`apply()`、`lapply()`、`sapply()`、`vapply()`、`tapply()` |
| 字符串 | `paste()`、`paste0()`、`sprintf()`、`grepl()`、`gsub()`、`strsplit()` |
| 日期时间 | `as.Date()`、`as.POSIXct()`、`format()`、`Sys.time()` |
| 读写文件 | `read.csv()`、`write.csv()`、`readLines()`、`writeLines()`、`readRDS()`、`saveRDS()` |
| 绘图建模 | `plot()`、`hist()`、`boxplot()`、`lm()`、`predict()` |
| 求助排错 | `?`、`help.search()`、`args()`、`example()`、`traceback()`、`sessionInfo()` |

### 18.2 动手练习

先自己写，再展开下面的参考答案。

1. 创建向量 `c(3, 5, NA, 9, 12)`，计算非缺失值的均值、缺失个数和大于 6 的非缺失值。
2. 创建包含姓名、组别、成绩的数据框，筛选 A 组且成绩不低于 80 的行，并计算各组平均成绩。
3. 写函数 `normalize01(x)`，把非恒定数值向量缩放到 0～1；对空向量、缺失值和所有值相同的情况作出明确处理。
4. 使用内置 `mtcars`，画出 `wt` 与 `mpg` 的散点图，并拟合 `mpg ~ wt` 线性模型。

<details>
<summary>参考答案</summary>

```r
# 练习 1
x <- c(3, 5, NA, 9, 12)
mean(x, na.rm = TRUE)
sum(is.na(x))
x[!is.na(x) & x > 6]

# 练习 2
df <- data.frame(
  name = c("甲", "乙", "丙", "丁"),
  group = c("A", "B", "A", "B"),
  score = c(85, 72, 91, 88)
)
df[df$group == "A" & df$score >= 80, ]
aggregate(score ~ group, data = df, FUN = mean)

# 练习 3：保留 NA；恒定向量的非缺失位置返回 0
normalize01 <- function(x) {
  if (!is.numeric(x)) stop("x 必须是数值向量")
  if (length(x) == 0L) return(numeric(0))
  if (all(is.na(x))) return(rep(NA_real_, length(x)))
  lo <- min(x, na.rm = TRUE)
  hi <- max(x, na.rm = TRUE)
  if (lo == hi) return(ifelse(is.na(x), NA_real_, 0))
  (x - lo) / (hi - lo)
}
normalize01(c(2, 4, NA, 6))

# 练习 4
plot(mtcars$wt, mtcars$mpg, xlab = "Weight", ylab = "Miles per gallon", pch = 19)
fit <- lm(mpg ~ wt, data = mtcars)
abline(fit, col = "red")
summary(fit)
```

</details>

## 继续学习的官方资料

- [An Introduction to R](https://stat.ethz.ch/CRAN/doc/manuals/r-release/R-intro.html)：从对象、索引、数据框到统计建模的系统教程。
- [The R Language Definition](https://stat.ethz.ch/CRAN/doc/manuals/R-lang.html)：语法、求值和作用域等语言细节。
- [R Data Import/Export](https://stat.ethz.ch/CRAN/doc/manuals/r-release/R-data.html)：数据文件的导入导出。
- 在 R 中运行 `help.start()`、`?函数名`、`example(函数名)`，查询当前安装版本对应的帮助。

---

**推荐学习顺序：**先掌握向量、索引、缺失值和数据框；再练习函数、文件读写与绘图；最后用一份真实但规模较小的数据，从导入、检查、清洗到分析和图表完整做一遍。
