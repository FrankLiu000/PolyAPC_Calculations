# T5 v3.7：cathode 侧 Al-center / 分子接触复核

日期：2026-07-01  
脚本：`results/T5_anion_interface/scripts/field_alcenter_molecule_check.py`  
输出：`field_alcenter_molecule_check.csv`、`field_alcenter_molecule_check_raw.csv`

## 目的

v3.6 的 fixed-face 分析显示：在外加场 classical-MD 中，poly 体系 cathode 侧 ANI atom density 明显低于 bare。这里进一步拆分为：

- all ANI atoms；
- ANI 分子是否有任意原子进入界面层；
- Al center；
- Al/Cl reactive atoms；
- ANI 分子是否有 Al/Cl 进入界面层。

这样可以回答一个更关键的问题：poly 的 cathode 侧 ANI 降低，是否也对应更少 Al-center / Al-Cl 反应位点接近 Mg 还原前沿。

## 运行与内存安全

脚本按体系流式读取轨迹，并在一次 pass 中累计 0.6、1.0、1.5 nm 三个 layer 和 50-200 ns、130-200 ns 两个窗口，避免把轨迹载入内存。

实际运行资源：

```text
wall time = 45.3 s
max RSS = 156,912 kB
swap = 0
WSL MemAvailable after run = 27 GiB
```

## 关键结果

最适合作为主文支撑的是 1.0 nm cathode layer，因为 0.6 nm 是最内层接触，Al center 事件过稀疏；1.5 nm 则更接近宽界面浓度而不是电子转移前沿。

### 130-200 ns，1.0 nm cathode layer

| metric | bare cathode /nm2 | poly cathode /nm2 | bare/poly |
|---|---:|---:|---:|
| all ANI atoms | 5.861 | 3.115 | 1.88 |
| ANI molecule, any atom | 0.393 | 0.259 | 1.52 |
| Al center | 0.310 | 0.0895 | 3.46 |
| Al+Cl reactive atoms | 0.959 | 0.221 | 4.35 |
| ANI molecule, Al/Cl in layer | 0.358 | 0.124 | 2.90 |

### 50-200 ns，1.0 nm cathode layer

| metric | bare cathode /nm2 | poly cathode /nm2 | bare/poly |
|---|---:|---:|---:|
| all ANI atoms | 5.641 | 3.291 | 1.71 |
| ANI molecule, any atom | 0.382 | 0.271 | 1.41 |
| Al center | 0.301 | 0.0909 | 3.32 |
| Al+Cl reactive atoms | 0.925 | 0.221 | 4.20 |
| ANI molecule, Al/Cl in layer | 0.343 | 0.126 | 2.73 |

### 0.6 nm 最内层

在 130-200 ns 最内层，poly cathode 侧 Al center 和 Al/Cl reactive atoms 都为 0；bare 也只有极稀疏 Al/Cl 事件。因此 0.6 nm 只能说明“最内层直接 Al-center 接触在 classical-MD 中罕见”，不能用来直接证明 Al0 形成。

## 解释边界

这个复核加强了 v3.6 的结构结论：**poly 不只是降低 cathode 侧 ANI all-atom density，也显著降低 cathode 侧 Al center 和 Al/Cl reactive-site 接触机会**。这与 poly-APC 的 Al-poor interphase 主线一致：POSS 网络/界面组成使可还原 Al 阴离子更少进入 Mg 电子转移前沿。

但 classical-MD 没有电子自由度，不能证明 Al0、Mg-Al alloy 或还原反应。它的角色是提供 contact-opportunity / concentration-gating 证据；真正的还原选择性仍需由 AIMD/DFT 的 qAl、Al-Cl、Al-Mg coordination 和 XPS/ToF-SIMS 闭环证明。
