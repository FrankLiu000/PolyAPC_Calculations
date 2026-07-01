# cryo-EM Mg(0002)织构的计算桥接

## 需要解释的实验现象

新的cryo-EM结果显示：poly-APC组沉积Mg主要呈Mg(0002)取向，而bare-APC组Mg晶型更杂乱、结晶度更低。这个现象可以纳入当前“界面组成/氧化还原选择性”主线，但需要分成两层表述：已有计算已经能支持“为什么bare更容易失去有序Mg外延生长”，而直接复现Mg(0002)织构还需要包含新沉积Mg原子的AIMD或MLFF-MD轨迹。

## 当前计算已经能支持什么

已有T13结果表明，在干净Mg(0001)上，Mg吸附原子的fcc/hcp位点在k点收敛后接近简并。因此，单纯用“Mg吸附位点偏好”来解释poly组Mg(0002)取向并不稳健。

更可靠的计算链条仍然是组成效应：

```text
poly-APC -> Si/O-rich, Al-poor interface -> Al-rich随机核更少
bare-APC -> Al阴离子到达/还原于Mg前沿 -> Al0 / Mg-Al异质性
Al / Mg-Al异质性 -> 干扰Mg同质外延 -> 低结晶度与随机取向
poly排Al界面 -> 更干净的Mg-on-Mg生长 -> 更强Mg(0002)取向
```

这与项目约束一致：poly-APC优势来自界面组成和氧化还原选择性，而不是体相离子传输优势。

## 如何在计算中体现

### 层级1：DFT织构倾向

在当前T23优先任务之后，增加一组小规模DFT slab计算：

1. 干净Mg(0001) + Mg adatom / Mg2-Mg4小岛，比较hcp/fcc/bridge位点；
2. Al污染Mg(0001)，模型可用表面替位Al、Al adatom或Mg-Al合金化位点；
3. 在Al污染表面上再放置Mg adatom / Mg小岛；
4. 比较局部畸变、吸附能起伏、fcc/hcp registry splitting以及扩散势垒。

若结果成立，可发表表述为：干净Mg(0001)支持低畸变Mg同质外延；Al/Mg-Al位点则引入异质成核中心和局部结构畸变，破坏Mg(0002)取向生长。这能直接解释bare组低结晶度，同时不需要诉诸传输优势。

### 层级2：MLFF-MD织构类比

待`t16_broad_r8_keyholdout`通过关键holdout验证后，运行配对bare/poly T17 production。若轨迹包含新沉积Mg原子，则量化：

```text
新沉积Mg的hcp/0002 z-order
模拟I0002/I10-10比值
峰宽/无序度proxy
Al-near-deposit相关性
```

新脚本已经实现了保守的第一版分析：

```text
computational_v2/analysis/mg_texture_from_xyz.py
```

默认模式要求显式给出“新沉积Mg”原子索引；若没有索引文件，脚本不会自动把轨迹中的Mg2+或初始Mg slab误判为沉积Mg。这样可以避免把本来已经晶化的Mg基底或溶液中的Mg物种误当成Mg(0002)织构证据。

对现有T17轨迹的空审计结果：

```text
results/T13_nucleation/texture_audit_bare_final.md
results/T13_nucleation/texture_audit_poly_r6.md
```

两者均显示没有显式新沉积Mg群体。因此，当前T17 Al阴离子轨迹可以支持Al排斥/Al接触机会这一机制，但**不能**作为直接Mg(0002)织构证据。

为下一步直接对应cryo-EM，已经准备了一个受控Mg-deposit texture probe：

```text
computational_v2/mlff/v3/t17/build_mgdep_starts.py
computational_v2/mlff/v3/t17/run_r8_mgdep_texture_after_gate.sh
computational_v2/mlff/v3/t17/bare_mgdep_start.xyz
computational_v2/mlff/v3/t17/poly_mgdep_start.xyz
computational_v2/mlff/v3/t17/bare_mgdep_indices0.txt
computational_v2/mlff/v3/t17/poly_mgdep_indices0.txt
```

这组输入在bare和poly中使用同一组表面分数坐标加入4个中性Mg adatom/小岛原子，并用0-based索引文件显式标记“新沉积Mg”。它的用途是测试：在相同初始Mg-deposit probe下，bare中Al-rich接触/脱氯/沉积是否导致Mg小岛失序，而poly中Al排斥是否允许Mg(0002)有序保持。它不是“自发Mg plating”的证据。

起始结构审计已写入：

```text
results/T13_nucleation/mgdep_seed_audit/bare_mgdep_start_texture.md
results/T13_nucleation/mgdep_seed_audit/poly_mgdep_start_texture.md
```

这些初态数值只作为baseline。后续图中应报告末段相对于初态的变化，而不是用初态本身证明poly更好。`run_r8_mgdep_texture_after_gate.sh`默认在r8 key-holdout通过后运行500 ps、两个seed的bare/poly配对轨迹，并用`--nslab 64`保证电极定义与T17 driver一致。

### 层级3：模拟衍射/图形输出

如果要做成论文图，应始终并列报告bare与poly：

```text
bare: 更高Al接触/沉积 + 更低新沉积Mg I0002/I10-10 + 更宽/更无序峰
poly: 更低Al接触/沉积 + 更高新沉积Mg I0002/I10-10 + 更尖锐Mg(0002)层状有序
```

这将形成cryo-EM / SAED / FFT的直接计算对应。

## 当前边界

现有T17轨迹主要追踪Al阴离子靠近/还原前沿，并不等同于完整Mg沉积形貌模拟。因此，现在最稳妥的说法是：

> 当前DFT和MD已经支持bare-APC织构损失的原因：Al-rich共沉积和界面化学异质性干扰Mg同质外延。直接的Mg(0002)模拟织构指标，需要r8验证通过后的MLFF-MD或AIMD，并且轨迹中必须含有新沉积Mg原子。
