# 密码学基础 · 笔记

「密码学基础」复习笔记的 Markdown 原件与配图。站点构建时会把本目录复制到生成目录，修改内容请改这里的文件，不要改生成副本。

## 目录内容

| 文件 | 主题 |
|---|---|
| `00_索引.md` | 入口：覆盖范围、教材映射、文件列表、阅读顺序、维护记录 |
| `01_导论与密码学原则.md` | 密码学问题、Kerckhoffs 原则、密码系统要素、可证明安全、MPC 与 ZKP |
| `02_完美保密与一次性密码本.md` | 香农安全、完美安全、等价证明、Shannon 定理、OTP |
| `03_单向函数与伪随机生成器.md` | PPT、OWF 三档、大数分解、EAV、计算不可区分、PRG |
| `04_多消息安全与IND-CPA.md` | reuse、确定性加密的缺陷、IND-CPA、LR-CPA、hybrid argument |
| `05_伪随机函数与伪随机置换.md` | PRF、PRP、GGM 树、CBC / OFB / CTR |
| `06_消息认证码MAC.md` | MAC、EUF-CMA、CBC-MAC、ECBC-MAC、HMAC |
| `07_哈希函数与Merkle-Damgård结构.md` | 抗碰撞、MD 结构、生日攻击 |
| `08_CCA安全与认证加密.md` | CCA、认证加密、组合方式 |
| `09_数论基础与密码学硬假设.md` | 数论、Miller–Rabin、Factoring / RSA / DL / DDH |
| `10_密钥交换与Diffie-Hellman.md` | 密钥分发、KDC、DH、MITM |
| `11_公钥加密与ElGamal.md` | 公钥加密、RSA、Padded RSA、ElGamal |
| `12_习题一_OTP缺陷与OWF-PRG关系.md` | 作业一与解答 |
| `13_考试范围与复习要点.md` | 期末范围、复习大纲、历年卷回忆 |
| `14_期中试卷_25秋冬.md` | 25 秋冬期中卷转录与考点对照 |
| `assets/` | 配图，相对路径引用 |

## 资料来源

1. **课堂记录（主要来源）**：`../class_documentation/class_documentation.md`。`01`–`04` 按它重写；需要查原话时看 `../class_documentation/origin/` 中对应日期的拆分文件。
2. **教材（核对用）**：Katz & Lindell, *Introduction to Modern Cryptography*（2007 年第 1 版），即 `../Introduction_to_Modern_Cryptography.pdf`。用于核对定义、定理编号和课堂没有展开的构造。
3. **早前整理的 05–14 篇**：仍保留原来的课程资料说明与教材对照，暂未按 `class_documentation.md` 重写。引用时先看该篇页首的来源说明。

## 写作约定

- 每篇结构：速览 → 定义与直觉 → 构造与证明 → 公式汇总 → 易混点 → 复习清单 → 关联知识点 → 来源。
- 公式用 LaTeX：行内 `$...$`，块级 `$$...$$`。
- 图片用相对路径引用，放在 `assets/`。
- 课堂记录没有说清的地方标「待确认」；整理者补的推导标「整理者补充 / 整理者核对」。
- 修改标题、文件名或拆分小节后，同步更新 `00_索引.md` 和相关链接。
