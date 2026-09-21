# 密码学基础 · 12：作业一（OTP 的缺陷、PRG ⇒ OWF、OWF ⇏ PRG）

> 来源：用户提供的课程资料（一份速查表提纲 ＋ 一份按课次记录的课程笔记 Lec1–Lec13；详见 [`00_索引.md`](00_索引.md) §1）
> 整理日期：2026-09-21
> 说明：本节是**作业题的题目 + 解答**整理（题面为英文，答案中英混排，此处**保留英文原句**并补中文解读）。资料自己注明：「这一节作业**没有更新勘误**，因此看个大概就行，懒得改成提交的版本」——所以下面的答案按“参考解法”对待，细处请自行核对。
> 教材对照：Katz & Lindell（Revised 3rd ed.）**§2.1–§2.3**（完美保密与其局限）、**§3.3.1**（PRG）、**§8.1**（OWF 的定义与候选）。

## 0. 本节速览

| 题号 | 主题 | 一句话摘要 |
|---|---|---|
| Q1 | A Flawed One-Time Pad | 把密钥空间限制为“1 的个数为偶数”的串后，**密文 1 的个数的奇偶性泄漏了明文的奇偶性**，完美保密被破坏。 |
| Q2.1 | PRG ⇒ OWF | 若 PRG $G$ 能被求逆，则可用它构造区分 $G(s)$ 与真随机串的判别器 ⇒ 矛盾；故 PRG 一定是强单向函数。 |
| Q2.2 | OWF ⇏ PRG | 构造 $G(r)=\mathrm{concat}(F(r),1)$：$G$ 仍是 OWF（求逆 $G$ 立即给出求逆 $F$），但**末位恒为 1**，一眼可区分 ⇒ 不是 PRG。 |

---

## 1. Q1：A Flawed One-Time Pad

### 1.1 题面（英文原文）

> Consider a variant of the one-time pad with message space $\{0,1\}^{n}$, where $n$ is an **odd** integer, and the secret key space is restricted to all $n$-bit strings with an **even** number of 1’s. Construct an efficient adversary that compromises perfect secrecy.

### 1.2 答案

**Step 1：算出密钥集合的大小。** 记密钥集合为 $K$：

$$|K|=\sum_{i\ \mathrm{even}}\binom{n}{i}=2^{n-1}$$

（资料写成一个求和式并给出结果 $2^{n-1}$；其中组合数的渲染被网页公式搞乱了，上面按“1 的个数为偶数的串”补全。）

**Step 2：比较两条消息的密文分布。** 对任意“1 的个数为奇数”的 $m_1$ 与“1 的个数为偶数”的 $m_2$：

$$\underset{sk}{\Pr}\,[\,m_{1}\oplus sk=c\,]=
\begin{cases}
\dfrac{1}{2^{n-1}}, & \text{若 } \mathrm{pop\_count}(c)\not\equiv 0 \pmod 2\\[4pt]
0, & \text{若 } \mathrm{pop\_count}(c)\equiv 0 \pmod 2
\end{cases}$$

$$\underset{sk}{\Pr}\,[\,m_{2}\oplus sk=c\,]=
\begin{cases}
\dfrac{1}{2^{n-1}}, & \text{若 } \mathrm{pop\_count}(c)\equiv 0 \pmod 2\\[4pt]
0, & \text{若 } \mathrm{pop\_count}(c)\not\equiv 0 \pmod 2
\end{cases}$$

**Step 3：结论。** 于是攻击者只要看密文 $c$ 里 1 的个数的奇偶性，就能判断**原始明文里 1 的个数的奇偶性**——这条额外信息足以破坏完美保密。

### 1.3 思路

- 标准 OTP 的三个算法：

$$M=\{0,1\}^{n}=K,\qquad
\mathrm{Gen}(\cdot)\to sk\ (sk\overset{\$}{\leftarrow}K),\qquad
\mathrm{Enc}(sk,m)=sk\oplus m,\qquad
\mathrm{Dec}(sk,c)=sk\oplus c$$

- 在 $sk$ **均匀随机**的前提下，两条明文被加密成同一密文 $c$ 的概率相等：

$$\underset{sk}{\Pr}\,[m_1\oplus sk=c]=\underset{sk}{\Pr}\,[m_2\oplus sk=c]$$

- 但把 $K$ 的定义改掉之后，一旦两条明文的奇偶性不同：

$$\underset{sk}{\Pr}\,[m_1\oplus sk=c]\neq\underset{sk}{\Pr}\,[m_2\oplus sk=c]\quad\text{若 }\mathrm{pop\_count}(m_1)\not\equiv\mathrm{pop\_count}(m_2)\pmod 2$$

- 对照 [02 篇 §2 的 Perfect 形式](02_完美保密与一次性密码本.md#2-两个形式的安全定义)：**“任意两条明文得到同一密文的概率相同”这一条被直接违反了**，所以不再是完美保密。

### 1.4 整理者核对

- 奇偶性的推理是**模 2 加法**：$\mathrm{pop\_count}(m\oplus sk)\equiv \mathrm{pop\_count}(m)+\mathrm{pop\_count}(sk)\pmod 2$。因为 $sk$ 恒为偶（1 的个数为偶数），所以密文的奇偶性 $\equiv$ 明文的奇偶性——这正是上表两段概率的来源。
- 待确认：资料答案里写了 “**since $n$ is odd**”，但按上面的推导，这个攻击对**任意 $n$** 都成立（偶重密钥集合 $K$ 是 $\mathbb{F}_2^n$ 的一个 $n-1$ 维子空间，$m_1\oplus K$ 与 $m_2\oplus K$ 要么重合、要么不交，恰好由明文奇偶性决定）。“$n$ 为奇数”这个条件的用途资料未说明，**留待课上确认**。

## 2. Q2.1：PRG 一定是（强）单向函数

### 2.1 题面

> Let $G$ be a PRG that maps $n$ bits to $2n$ bits, prove that $G$ is a (strong) one-way function.

### 2.2 解答

**（1）先写出 PRG 的定义（不可区分性）**：对任意算法 $A$，它区分“$G$ 在随机输入下的输出”与“真随机串”的概率可忽略：

$$\Bigl|\ \underset{s\leftarrow\{0,1\}^{n},\,r\leftarrow G(s)}{\Pr}[\mathcal{A}(r)=1]\ -\ \underset{r\overset{\mathbb{R}}{\leftarrow}\{0,1\}^{l(n)}}{\Pr}[\mathcal{A}(r)=1]\ \Bigr|\ \le\ \mathtt{negl}(n)$$

（本题 $l(n)=2n$。）

**（2）反设 $G$ 不是单向函数**：则存在高效算法 $\mathcal{A}_0$ 能求逆，

$$\underset{x}{\Pr}\,[\,G\bigl(\mathcal{A}_{0}(G(x))\bigr)=G(x)\,]\ \ge\ \frac{1}{\mathrm{poly}(n)}$$

**（3）用 $\mathcal{A}_0$ 造一个区分器**：

$$\mathcal{A}'(r)=\bigl[\,G(\mathcal{A}_{0}(r))=r\,\bigr]:\ \{0,1\}^{2n}\to\{0,1\}$$

于是

$$\underset{s\leftarrow\{0,1\}^{n},\,r\leftarrow G(s)}{\Pr}[\mathcal{A}'(r)=1]
=\underset{s\leftarrow\{0,1\}^{n}}{\Pr}[\,G(\mathcal{A}_{0}(G(s)))=G(s)\,]\ \ge\ \frac{1}{\mathrm{poly}(n)}$$

而**当输入是真随机串**时，它落在 $G$ 的像里的概率只有

$$\underset{r\overset{\mathbb{R}}{\leftarrow}\{0,1\}^{2n}}{\Pr}[\mathcal{A}'(r)=1]\ \le\ \underset{r\overset{\mathbb{R}}{\leftarrow}\{0,1\}^{2n}}{\Pr}[\,\exists s\in\{0,1\}^{n},\ G(s)=r\,]=\frac{2^{n}}{2^{2n}}=\frac{1}{2^{n}}$$

**（4）得出矛盾**：

$$\Bigl|\ \underset{s,r\leftarrow G(s)}{\Pr}[\mathcal{A}'(r)=1]-\underset{r\overset{\mathbb{R}}{\leftarrow}\{0,1\}^{2n}}{\Pr}[\mathcal{A}'(r)=1]\ \Bigr|\ \ge\ \Bigl|\frac{1}{\mathrm{poly}(n)}-\frac{1}{2^{n}}\Bigr|\ \ge\ \frac{1}{\mathrm{poly}'(n)}$$

由于 $\dfrac{1}{\mathrm{poly}'(n)}\ne\mathtt{negl}(n)$，这与 $G$ 是 PRG 的假设矛盾。故 **$G$ 是单向函数**。

> 待确认：资料第 (2) 步把括号写错了（写成 $\Pr[f(\mathcal{A}_0(G(x))=G(x)]$），上面已按语义改正为 $\Pr_x[G(\mathcal{A}_0(G(x)))=G(x)]$；资料自己在括号里注明 “$G$ here is essentially the function $f$ in the definition”。

## 3. Q2.2：OWF 不一定是 PRG

### 3.1 题面

> Given that $F$ is a one-way function, construct a function $G$ such that **① $G$ is a one-way function；② $G$ is not a pseudorandom generator (PRG)**。

### 3.2 构造

设 $F:\{0,1\}^{n}\to\{0,1\}^{l(n)}$，令

$$G:\{0,1\}^{n}\to\{0,1\}^{l(n)+1},\qquad G(r)=\mathrm{concat}\bigl(F(r),\,1\bigr)$$

即在 $F$ 的输出后面**补一个 1**（资料注：$\mathrm{concat}$ 表示两个二进制序列的顺序拼接）。

### 3.3 证明一：$G$ 是 OWF

- $F$ 是 OWF，即

$$\forall\mathcal{A}:\{0,1\}^{l(n)}\to\{0,1\}^{n},\quad
\underset{x\overset{\mathbb{R}}{\leftarrow}\{0,1\}^{n}}{\Pr}[\,F(\mathcal{A}(F(x)))=F(x)\,]\ \le\ \mathtt{negl}(x)$$

- **反设 $G$ 不是 OWF**：则存在 $\mathcal{A}_0:\{0,1\}^{l(n)+1}\to\{0,1\}^{n}$ 与多项式，使

$$\underset{x\overset{\mathbb{R}}{\leftarrow}\{0,1\}^{n}}{\Pr}[\,G(\mathcal{A}_{0}(G(x)))=G(x)\,]\ \ge\ \frac{1}{\mathrm{poly}(n)}$$

- **构造** $\mathcal{A}_{0}'(r)=\mathcal{A}_{0}\bigl(\mathrm{concat}(r,1)\bigr)$，它满足

$$\underset{x\overset{\mathbb{R}}{\leftarrow}\{0,1\}^{n}}{\Pr}[\,F(\mathcal{A}_{0}'(F(x)))=F(x)\,]\ \ge\ \frac{1}{\mathrm{poly}(n)}$$

这与 $F$ 是 OWF 矛盾 ⇒ **$G$ 是 OWF**。

### 3.4 证明二：$G$ 不是 PRG

- 构造区分器（只看最后一位）：

$$\mathcal{A}''(r)=
\begin{cases}
1, & r_{l(n)+1}=1\\
0, & r_{l(n)+1}=0
\end{cases}$$

- 则

$$\Bigl|\ \underset{s\leftarrow\{0,1\}^{n},\,r\leftarrow G(s)}{\Pr}[\mathcal{A}(r)=1]\ -\ \underset{r\overset{\mathbb{R}}{\leftarrow}\{0,1\}^{l(n)+1}}{\Pr}[\mathcal{A}(r)=1]\ \Bigr|
=1-\frac12=\frac12$$

- $\frac12$ 显然不是可忽略的 ⇒ 违反 PRG 定义 ⇒ **$G$ 不是 PRG**。

**小结**：所构造的 $G$ **是单向函数但不是伪随机生成器**——说明“单向性”严格弱于“伪随机性”（单向性只要求求逆难，不要求输出看起来随机）。

> 待确认：资料正文末尾遗留一句 “In summary, the constructed $G$ is a One-Way Function but not a PRG.**br**”（`br` 是网页换行残留），已按语义整理。

## 4. 缺失的部分

- 资料有一个小节标题 **「第二次作业：CCA-PRP」**，但正文**只有一个残留的 `>`，没有任何内容**。
- 因此本笔记**不包含第二次作业的任何内容**：题目、答案、涉及的安全模型（CCA / PRP 相关构造）全部待补。
- 已记入 [`00_索引.md`](00_索引.md) 的待确认事项：需要用户提供第二次作业的题面（或等课程讲到 CCA 时再整理，对照教材 §5.1–§5.3）。

## 5. 复习清单

- [ ] 复述 Q1 的攻击：为什么“看密文 1 的个数的奇偶性”能区分明文？（[§1.2](#12-答案)）
- [ ] 用 Perfect 形式的定义一句话说明 Q1 里哪一条被违反。（[§1.3](#13-思路)）
- [ ] 写出 Q2.1 里区分器 $\mathcal{A}'$ 的定义，并说明它对真随机输入的输出概率为什么是 $2^{-n}$ 级别。（[§2.2](#22-解答)）
- [ ] 复述 Q2.2 的两个证明方向，并说出“补一个 1”为什么恰好破坏伪随机性而不破坏单向性。（[§3.3](#33-证明一g-是-owf)、[§3.4](#34-证明二g-不是-prg)）
- [ ] “OWF”与“PRG”哪一个更强？用本题的构造举例说明。（[§3.4](#34-证明二g-不是-prg)）

## 6. 关联知识点

- 完美保密的两个等价定义（Q1 直接用到 Perfect 形式）——见 [`02_完美保密与一次性密码本.md`](02_完美保密与一次性密码本.md#2-两个形式的安全定义)。
- OWF 的三档定义、$g(x,y)=xy$ 的例子（与 Q2.2 的“构造反例”同一种思路）——见 [`03_单向函数与伪随机生成器.md`](03_单向函数与伪随机生成器.md#2-单向函数one-way-function-owf)、[§3.4](03_单向函数与伪随机生成器.md#34-换一个函数gxyxy-显然不是-strong-owf)。
- PRG 的定义与“一半真随机”的归约套路（Q2.1 就是它的反向使用）——见 [`03_单向函数与伪随机生成器.md`](03_单向函数与伪随机生成器.md#62-标准定义)。
- 教材：§2.1–§2.3（完美保密与局限）、§3.3.1（PRG）、§8.1（OWF 定义）。

## 7. 来源与延伸阅读

- 来源：用户提供的课程资料（速查表提纲 ＋ 课程笔记 Lec1–Lec13）；清单见 `密码学基础/readme.md`。原始资料（`数据安全与密码学基础.zip` 及其中的附件）均为**只读引用**，未改动。
- 参考书：Katz & Lindell, *Introduction to Modern Cryptography*（Revised 3rd ed.）。
- 待补充：**第二次作业「CCA-PRP」只有标题、没有正文**；本作业在资料里也**没有答案勘误**（原页自述「看个大概就行」），细节请自行核对。
