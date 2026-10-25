# Pipelined CPU Assignment

> 来源：原 `sys2/计算机组合作业/下载*.png`（18 张连续截图，原始图片已按用户要求删除）
> 整理日期：2026-10-23
> 说明：本文按截图逐题还原，仅包含题目，不含解答。原始截图中的英文拼写与措辞保持原样；换行位置按阅读需要调整。

> 还原注记：第 6.4 题在较早的原截图中写作 `load 35%`，后续原截图写作 `load 25%`。按后续版本及四项占比合计为 100%（52% + 25% + 11% + 12%）判断，正文采用 `load 25%`。

## 1

Problems in this exercise assume that individual stages of the datapath have the following latencies:

| IF | ID | EX | MEM | WB |
|---|---:|---:|---:|---:|
| 250ps | 350ps | 150ps | 300ps | 200ps |

Also, assume that instructions executed by the processor are broken down as follows:

| ALU/Logic | Jump/Branch | Load | Store |
|---|---:|---:|---:|
| 45% | 20% | 20% | 15% |

1.1 What is the clock cycle time in a pipelined and non-pipelined processor?

1.2 What is the total latency of an `ld` instruction in a pipelined and non-pipelined processor?

1.3 If we can split one stage of the pipelined datapath into two new stages, each with half the latency of the original stage, which stage would you split and what is the new clock cycle time of the processor?

1.4 Assuming there are no stalls or hazards, what is the utilization of the data memory?

1.5 Assuming there are no stalls or hazards, what is the utilization of the write-register port of the “Registers” unit?

## 2

What is the minimum number of cycles needed to completely execute n instructions on a CPU with a k stage pipeline?

## 3

Assume that x11 is initialized to 11 and x12 is initialized to 22. Suppose you executed the code below on a version of the 5 stage pipeline that does not handle data hazards (i.e., the programmer is responsible for addressing data hazards by inserting NOP instructions where necessary). What would the final values of registers x13 and x14 be?

```asm
addi x11, x12, 5
add x13, x11, x12
addi x14, x11, 15
```

## 4

Assume that x11 is initialized to 11 and x12 is initialized to 22. Suppose you executed the code below on a version of the pipeline that does not handle data hazards (i.e., the programmer is responsible for addressing data hazards by inserting NOP instructions where necessary). What would the final values of register x15 be? Assume the register file is written at the beginning of the cycle and read at the end of a cycle. Therefore, an ID stage will return the results of a WB state occurring during the same cycle.

```asm
addi x11, x12, 5
add x13, x11, x12
addi x14, x11, 15
add x15, x11, x11
```

## 5

Add NOP instructions to the code below so that it will run correctly on a pipeline that does not handle data hazards.

```asm
addi x11, x12, 5
add x13, x11, x12
addi x14, x11, 15
add x15, x13, x12
```

## 6

Consider the fragment of RISC-V assembly below. Suppose we modify the pipeline so that it has only one memory (that handles both instructions and data). In this case, there will be a structural hazard every time a program needs to fetch an instruction during the same cycle in which another instruction accesses data.

```asm
sd x29, 12(x16)
ld x29, 8(x16)
sub x17, x15, x14
beqz x17, label
add x15, x11, x14
sub x15, x30, x14
```

6.1 Draw a pipeline diagram to show where the code above will stall.

6.2 In general, is it possible to reduce the number of stalls resulting from this structural hazard by reordering code?

6.3 Must this structural hazard be handled in hardware? We have seen that data hazards can be eliminated by adding NOPs to the code. Can you do the same with this structural hazard? If so, explain how. If not, explain why not.

6.4 Approximately how many stalls would you expect this structural hazard to generate in a typical program? (Assume ALU/Logic 52%, load 25%, store 11%, branch 12%)

## 7

Consider the following loop.

```asm
LOOP:   ld x10, 0(x13)
        ld x11, 8(x13)
        add x12, x10, x11
        subi x13, x13, 16
        bnez x12, LOOP
```

Assume that perfect branch prediction is used (no stalls due to control hazards), that there are no delay slots, that the pipeline has full forwarding support, and that branches are resolved in the EX (as opposed to the ID) stage.

7.1 Show a pipeline execution diagram for the first two iterations of this loop.

7.2 Mark pipeline stages that do not perform useful work. How often while the pipeline is full do we have a cycle in which all five pipeline stages are doing useful work? (Begin with the cycle during which the `subi` is in the IF stage. End with the cycle during which the `bnez` is in the IF stage.)

## 8

Problems in this exercise refer to the following sequence of instructions, and assume that it is executed on a five-stage pipelined datapath:

```asm
add x15, x12, x11
ld x13, 4(x15)
ld x12, 0(x2)
or x13, x15, x13
sd x13, 0(x15)
```

8.1 If there is no forwarding or hazard detection, insert NOPs to ensure correct execution.

8.2 Now, change and/or rearrange the code to minimize the number of NOPs needed. You can assume register x17 can be used to hold temporary values in your modified code.

8.3 If the processor has forwarding, but we forgot to implement the hazard detection unit, what happens when the original code executes?

8.4 If there is forwarding, for the first seven cycles during the execution of this code, specify which signals are asserted in each cycle by hazard detection and forwarding units

8.5 If there is no forwarding, what new input and output signals do we need for the hazard detection unit in Figure 4.59? Using this instruction sequence as an example, explain why each signal is needed.

8.6 For the new hazard detection unit from 8.5, specify which output signals it asserts in each of the first five cycles during the execution of this code.

## 9

The importance of having a good branch predictor depends on how often conditional branches are executed. Together with branch predictor accuracy, this will determine how much time is spent stalling due to mispredicted branches. In this exercise, assume that the breakdown of dynamic instructions into various instruction categories is as follows:

| R-type | beqz/bnez | jal | ld | sd |
|---|---:|---:|---:|---:|
| 40% | 25% | 5% | 25% | 5% |

Also, assume the following branch predictor accuracies:

| Always-Taken | Always-Not-Taken | 2-Bit |
|---|---:|---:|
| 45% | 55% | 85% |

9.1 Stall cycles due to mispredicted branches increase the CPI. What is the extra CPI due to mispredicted branches with the always-taken predictor? Assume that branch outcomes are determined in the ID stage and applied in the EX stage that there are no data hazards, and that no delay slots are used.

9.2 Repeat 9.1 for the “always-not-taken” predictor.

9.3 Repeat 9.1 for the 2-bit predictor.

9.4 With the 2-bit predictor, what speedup would be achieved if we could convert half of the branch instructions to some ALU instruction? Assume that correctly and incorrectly predicted instructions have the same chance of being replaced.

9.5 With the 2-bit predictor, what speedup would be achieved if we could convert half of the branch instructions in a way that replaced each branch instruction with two ALU instructions? Assume that correctly and incorrectly predicted instructions have the same chance of being replaced.

9.6 Some branch instructions are much more predictable than others. If we know that 80% of all executed branch instructions are easy-to-predict loop-back branches that are always predicted correctly, what is the accuracy of the 2-bit predictor on the remaining 20% of the branch instructions?

---

## 参考答案（点击展开）

> 约定：五级流水线为 IF → ID → EX → MEM → WB；理想 CPI 取 1；分支在 EX 阶段生效时误预测惩罚取 2 个周期。第 6.4 题按 `load 25%` 计算。Q8 的“有转发”按包含 store-data 转发通路的标准五级数据通路理解；若课程图中没有该通路，见第 8.3 题备注。

<details>
<summary><b>第 1 题：流水线时钟、延迟与部件利用率</b></summary>

**1.1** 流水线时钟周期取最长一级：

$$
T_{\text{pipe}}=\max(250,350,150,300,200)=350\ \text{ps}
$$

非流水线时钟周期为各级延迟之和：

$$
T_{\text{non-pipe}}=250+350+150+300+200=1250\ \text{ps}
$$

**1.2** `ld` 在流水线中经过 5 级：

$$
T_{\text{pipe}}=5\times350=1750\ \text{ps}
$$

非流水线中：

$$
T_{\text{non-pipe}}=1250\ \text{ps}
$$

所以流水线提高了吞吐率，但单条 `ld` 的延迟反而更大。

**1.3** 应拆分 ID 级。ID 原为 350 ps，拆成两个 175 ps 的新级后，最长级变为 MEM 的 300 ps：

$$
T_{\text{new}}=\max(250,175,175,150,300,200)=300\ \text{ps}
$$

拆分其他级不能把最长的 350 ps 降下来。

**1.4** 数据存储器只被 load 和 store 使用：

$$
U_{\text{data,pipe}}=20\%+15\%=35\%
$$

若也问非流水线：一个周期 1250 ps 中，数据存储器只在 load/store 的 MEM 段工作 300 ps：

$$
U_{\text{data,non-pipe}}=35\%\times\frac{300}{1250}=8.4\%
$$

**1.5** 按经典分类，Jump/Branch 不写寄存器，写寄存器端口被 ALU 和 load 使用：

$$
U_{\text{write,pipe}}=45\%+20\%=65\%
$$

非流水线：

$$
U_{\text{write,non-pipe}}=65\%\times\frac{200}{1250}=10.4\%
$$

> 若把 `jal` 单独计入写寄存器指令，需要把 `jal` 的比例加到 65% 中；题面没有拆分 Jump/Branch，故这里采用经典 MIPS 分类。

</details>

<details>
<summary><b>第 2 题：n 条指令的流水线周期数</b></summary>

第一条指令需要 k 个周期填满流水线，之后每条指令再用 1 个周期：

$$
N=k+(n-1)=n+k-1
$$

因此最少需要 **n + k − 1 个周期**（n ≥ 1）。

</details>

<details>
<summary><b>第 3 题：无冲突检测时的 x13、x14</b></summary>

指令时序：

- `addi x11, x12, 5` 在第 5 周期写回 x11；
- `add x13, x11, x12` 在第 3 周期读 x11，读到旧值 11；
- `addi x14, x11, 15` 在第 4 周期读 x11，仍读到旧值 11。

所以：

$$
x13=11+22=33
$$

$$
x14=11+15=26
$$

最终：

$$
\boxed{x13=33,\quad x14=26}
$$

此时 x11 最终会变成 27，但两条后续指令没有读到它。

</details>

<details>
<summary><b>第 4 题：写口在前、读口在后时的 x15</b></summary>

`add x15, x11, x11` 在第 5 周期进入 ID。与此同时，第一条 `addi x11, x12, 5` 正好在第 5 周期进入 WB。题面规定寄存器文件在周期开始写、周期结束读，因此 ID 能读到同一周期 WB 写入的新值：

$$
x11=22+5=27
$$

于是：

$$
x15=x11+x11=27+27=54
$$

$$
\boxed{x15=54}
$$

</details>

<details>
<summary><b>第 5 题：插入 NOP</b></summary>

采用“写口在前半周期、读口在后半周期”，相隔两条指令时，消费者的 ID 可与生产者的 WB 同周期，因此每组真依赖之间需要 2 个 NOP；`addi x14, ...` 与 `add x15, ...` 之间只需处理 `add x13` 到 `add x15` 的依赖。

```asm
addi x11, x12, 5
nop
nop
add x13, x11, x12
addi x14, x11, 15
nop
add x15, x13, x12
```

共需要 **3 个 NOP**。

</details>

<details>
<summary><b>第 6 题：单存储器结构冲突</b></summary>

**6.1** 数据访问优先，发生冲突时阻塞取指。前两条指令 `sd`、`ld` 的 MEM 段分别在第 4、5 周期访问数据存储器，因此第 4、5 周期都不能同时取 I4，取指被阻塞两次。

| 周期 | IF | ID | EX | MEM | WB |
|---:|---|---|---|---|---|
| 1 | I1 `sd` | — | — | — | — |
| 2 | I2 `ld` | I1 | — | — | — |
| 3 | I3 `sub` | I2 | I1 | — | — |
| 4 | I4（阻塞） | I3 | I2 | I1 | — |
| 5 | I4（阻塞） | — | I3 | I2 | I1 |
| 6 | I4 | — | — | I3 | I2 |
| 7 | I5 | I4 | — | — | I3 |
| 8 | I6 | I5 | I4 | — | — |
| 9 | — | I6 | I5 | I4 | — |
| 10 | — | — | I6 | I5 | I4 |
| 11 | — | — | — | I6 | I5 |
| 12 | — | — | — | — | I6 |

表中第 4、5 周期是两次结构冲突造成的取指停顿；I4 直到第 6 周期才成功取指，之后流水线重新填充。总执行时间由无冲突时的 10 个周期变为 **12 个周期**。

**6.2** 一般不能靠重排消除。只要程序还要在每个周期取指，任何一条 load/store 的 MEM 数据访问都会与同周期的取指竞争同一个存储器。重排最多改变“哪一条指令被挡住”，不能改变每条数据访问都需要占用一个存储器周期的本质。

**6.3** 必须由硬件处理。插入 NOP 不能解决问题，因为 NOP 本身也要取指，仍然要占用统一存储器；NOP 只会增加指令数，不会消除数据访问与取指之间的资源冲突。可行办法是硬件仲裁并阻塞取指，或改用分离的指令/数据存储器、增加 cache/双端口等。

**6.4** 需要访问数据存储器的指令比例为：

$$
25\%\ (\text{load})+11\%\ (\text{store})=36\%
$$

每条这样的指令大约造成 1 个取指停顿，因此：

$$
\text{额外 CPI}\approx 0.36
$$

即平均每 100 条指令约 **36 个停顿周期**，大约每 2.78 条指令停顿一次。

</details>

<details>
<summary><b>第 7 题：循环流水线图与有用工作</b></summary>

**7.1** 第二轮 `ld x11` 与 `add x12` 之间存在 load-use 冒险。虽然有转发，但 load 数据在 MEM 末才可用，`add` 需要停顿 1 个周期。记第一轮为 I1–I5，第二轮为 I1′–I5′，时序如下：

| 周期 | IF | ID | EX | MEM | WB |
|---:|---|---|---|---|---|
| 1 | I1 `ld x10` | — | — | — | — |
| 2 | I2 `ld x11` | I1 | — | — | — |
| 3 | I3 `add` | I2 | I1 | — | — |
| 4 | I4 `subi` | I3（停顿） | I2 | I1 | — |
| 5 | I4（保持） | I3（保持） | 气泡 | I2 | I1 |
| 6 | I5 `bnez` | I4 | I3 | — | I2 |
| 7 | I1′ | I5 | I4 | I3 | — |
| 8 | I2′ | I1′ | I5 | I4 | I3 |
| 9 | I3′ | I2′ | I1′ | I5 | I4 |
| 10 | I4′ | I3′（停顿） | I2′ | I1′ | I5 |
| 11 | I4′（保持） | I3′（保持） | 气泡 | I2′ | I1′ |
| 12 | I5′ | I4′ | I3′ | — | I2′ |
| 13 | I1″ | I5′ | I4′ | I3′ | — |
| 14 | I2″ | I1″ | I5′ | I4′ | I3′ |
| 15 | I3″ | I2″ | I1″ | I5′ | I4′ |
| 16 | I4″ | I3″ | I2″ | I1″ | I5′ |

每轮 5 条指令实际需要 **6 个周期**：

$$
\text{CPI}_{\text{loop}}=\frac{6}{5}=1.2
$$

**7.2** 不做有用工作的阶段包括：

- 第 4、10 周期：`add` 在 ID 停顿；
- 第 5、11 周期：`subi` 在 IF 保持，ID 继续保持，EX 为气泡；
- `add` 的 MEM 段：第 7、13 周期；
- `subi` 的 MEM 段：第 8、14 周期；
- `bnez` 的 MEM 段：第 9、15 周期；
- `bnez` 的 WB 段：第 10、16 周期。

因此，虽然某些周期五个流水级都有指令占用，但总有一级或少一级没有做实际有用工作；**五级全部做有用工作的周期数为 0，频率为 0**。

> 若采用“连 load-use 也不需要停顿”的简化模型，则每轮 5 个周期中会有 1 个周期五级全部有用，即 20%；但标准五级流水线通常需要这 1 个 load-use 停顿。

</details>

<details>
<summary><b>第 8 题：冒险检测与转发</b></summary>

**8.1** 无转发、无冒险检测时，每条真依赖之间需要 2 个 NOP。关键依赖链为：

$$
\text{add }x15 \rightarrow \text{ld }x13 \rightarrow \text{or }x13 \rightarrow \text{sd }x13
$$

其中 `ld x12` 可作为中间的一条独立指令，因此一种正确写法是：

```asm
add x15, x12, x11
nop
nop
ld x13, 4(x15)
ld x12, 0(x2)
nop
or x13, x15, x13
nop
nop
sd x13, 0(x15)
```

共 **5 个 NOP**。

**8.2** 仍假设无转发。四个关键指令 `add → ld → or → sd` 构成真依赖链，每段至少需要 3 条指令的间隔；`ld x12` 只能填充其中一个空位，因此至少仍需 5 个 NOP，不能更少。例如：

```asm
add x15, x12, x11
ld x12, 0(x2)
nop
ld x13, 4(x15)
nop
nop
or x13, x15, x13
nop
nop
sd x13, 0(x15)
```

这里 `ld x12` 放在 I1 之后、I2 之前，既保持了“I1 读取旧 x12”的语义，也充当一个延迟槽。x17 只能存放临时值，不能打破 `add → ld → or → sd` 的真数据依赖，所以不能把 5 个 NOP 再降下来。

**8.3** 在有完整转发（包括 store-data 转发）的标准五级流水线中，原代码可以正确执行，不需要额外的 load-use 停顿：

- I1 的 x15 在第 4 周期转发给 I2 计算地址；
- I2 的 load 结果在第 6 周期转发给 I4；
- I4 的 OR 结果在第 7 周期转发给 I5 的 store 数据端。

这里 `ld x13` 与 `or` 之间隔了一条 `ld x12`，所以不构成“load 后立即使用”的 load-use 停顿。若课程数据通路没有 store-data 转发，则 I5 在 ID 阶段读到的是 I2 装入的旧 x13，最终会写入错误的旧值；这种情况下就需要额外的停顿/转发通路。

**8.4** 前 7 个周期的流水线占用与转发信号如下（`ForwardA/ForwardB`：`10` 表示 EX/MEM，`01` 表示 MEM/WB，`00` 表示寄存器文件）：

| 周期 | IF | ID | EX | MEM | WB | 转发/阻塞 |
|---:|---|---|---|---|---|---|
| 1 | I1 | — | — | — | — | 无 |
| 2 | I2 | I1 | — | — | — | 无 |
| 3 | I3 | I2 | I1 | — | — | 无 |
| 4 | I4 | I3 | I2 | I1 | — | `ForwardA=10`（I2 的 x15 来自 I1） |
| 5 | I5 | I4 | I3 | I2 | I1 | 无 |
| 6 | — | I5 | I4 | I3 | I2 | `ForwardB=01`（I4 的 x13 来自 I2 的 load） |
| 7 | — | — | I5 | I4 | I3 | `ForwardB=10`（I5 的 store 数据 x13 来自 I4） |

结论：无停顿；冒险检测单元不置位任何 `Stall/Flush` 信号。

**8.5** 无转发时，冒险检测不能只检测“EX 段是否为 load”，而要检测 ID 段源寄存器与所有尚未写回的写寄存器指令是否相同。需要增加/使用这些输入信号：

- `IF/ID.Rs1`、`IF/ID.Rs2`：消费者要读的源寄存器；
- `ID/EX.RegWrite`、`ID/EX.Rd`：EX 段指令是否写寄存器及写哪个寄存器；
- `EX/MEM.RegWrite`、`EX/MEM.Rd`：MEM 段指令是否写寄存器及写哪个寄存器；
- 必要时再加 `MEM/WB.RegWrite`、`MEM/WB.Rd`（若写回与读口不在同一周期完成）；
- `ID/EX.MemRead`：可用于识别 load-use 特殊情况。

输出信号仍为：

- `PCWrite = 0`：暂停 PC，停止取新指令；
- `IF/IDWrite = 0`：保持 ID 段指令，不让它进入 EX；
- `FlushE = 1`（或 `ControlMux = 0`）：把进入 EX 的控制信号清零，插入气泡。

例如 I1 `add x15` 在 EX、I2 `ld x13,4(x15)` 在 ID 时，必须比较 I2 的 `Rs1=x15` 与 I1 的 `Rd=x15`，并连续停顿两拍，直到 I1 的 WB 完成；同理 I2→I4 需要停顿一拍，I4→I5 需要停顿两拍。

**8.6** 前 5 个周期的输出如下（无转发）：

| 周期 | 正在检测的依赖 | `PCWrite` | `IF/IDWrite` | `FlushE` |
|---:|---|---:|---:|---:|
| 1 | 无 | 1 | 1 | 0 |
| 2 | 无 | 1 | 1 | 0 |
| 3 | I2 读 x15，I1 在 EX | 0 | 0 | 1 |
| 4 | I2 仍在 ID，I1 在 MEM | 0 | 0 | 1 |
| 5 | I1 已到 WB，I2 可读新值 | 1 | 1 | 0 |

因此第 3、4 周期停顿，第 5 周期恢复；这与 8.1 中 I1 与 I2 之间插入 2 个 NOP 的效果一致。

</details>

<details>
<summary><b>第 9 题：分支预测与 CPI</b></summary>

条件分支只占动态指令的 25%（`beqz/bnez`）；`jal` 是无条件跳转，按“总是正确”处理，不产生误预测。取分支在 EX 阶段生效，误预测惩罚为 2 个周期。

**9.1** Always-Taken 的误预测率为：

$$
1-45\%=55\%
$$

额外 CPI：

$$
\Delta\text{CPI}=25\%\times55\%\times2=0.275
$$

**9.2** Always-Not-Taken：

$$
\Delta\text{CPI}=25\%\times(1-55\%)\times2
=25\%\times45\%\times2=0.225
$$

**9.3** 2-Bit：

$$
\Delta\text{CPI}=25\%\times(1-85\%)\times2
=25\%\times15\%\times2=0.075
$$

**9.4** 基准 CPI 取 1。2-Bit 时：

$$
\text{CPI}_{\text{old}}=1+0.075=1.075
$$

把一半条件分支改成一条 ALU 指令后，条件分支比例变为 12.5%，指令总数不变：

$$
\text{CPI}_{\text{new}}=1+12.5\%\times15\%\times2
=1+0.0375=1.0375
$$

速度提升：

$$
\text{Speedup}=\frac{1.075}{1.0375}\approx1.036
$$

约为 **3.6% 的提升**。

**9.5** 把一半条件分支各替换成两条 ALU 指令。以 100 条原指令为基准：

- 原条件分支 25 条，转换 12.5 条；
- 转换后新增 25 条 ALU，剩余条件分支 12.5 条；
- 新指令总数：

$$
100+12.5=112.5
$$

新代码中条件分支比例为：

$$
\frac{12.5}{112.5}=\frac19
$$

新 CPI：

$$
1+\frac19\times15\%\times2
=1+\frac{0.3}{9}
\approx1.0333
$$

原总周期：

$$
100\times1.075=107.5
$$

新总周期：

$$
112.5\times1.0333\approx116.25
$$

速度提升：

$$
\text{Speedup}=\frac{107.5}{116.25}\approx0.925
$$

因此不是加速，而是约 **7.5% 的减速**（约 0.925 倍速度）。

**9.6** 设剩余 20% 分支的预测准确率为 q。总体准确率为 85%：

$$
80\%\times1+20\%\times q=85\%
$$

$$
0.8+0.2q=0.85
$$

$$
q=\frac{0.05}{0.2}=0.25
$$

所以剩余 20% 分支的 2-Bit 预测准确率为：

$$
\boxed{25\%}
$$

> 若老师把“分支结果在 ID 阶段确定”解释为 ID 阶段即可完成重定向（惩罚为 1 而不是 2），则 9.1–9.3 的额外 CPI 分别改为 0.1375、0.1125、0.0375；9.4 的速度提升约为 1.018，9.5 约为 0.907 倍速度。

</details>
