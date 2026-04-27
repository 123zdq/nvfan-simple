# RTX 3090 功耗墙 & 温度墙 操作备忘录

## https://github.com/olealgoritme/gddr6
`sudo gddr6` 读取显存温度

## 功耗墙 (Power Limit)

### 查询

```bash
# 完整功耗信息
nvidia-smi -q -d POWER

# 简洁查询（推荐）
nvidia-smi --query-gpu=index,name,power.draw,power.limit,power.max_limit,power.min_limit,power.default_limit --format=csv
```

| 字段 | 说明 |
|------|------|
| `power.draw` | 当前实际功耗 (W) |
| `power.limit` | 当前设定的功耗上限 (W) |
| `power.max_limit` | 允许设置的最大值 (W) |
| `power.min_limit` | 允许设置的最小值 (W) |
| `power.default_limit` | 默认功耗上限 (W) |

### 修改

```bash
# 设置为指定值 (W)，需 sudo
sudo nvidia-smi -i 0 -pl 380
sudo nvidia-smi -i 1 -pl 380

# 两张同时设置
sudo nvidia-smi -i 0,1 -pl 380

# 恢复默认
sudo nvidia-smi -i 0,1 -pl default
```

**注意：** `-pl` 设置是临时的，重启或驱动重载后恢复。永久设置需要写入 initrd 或 nvidia-persistenced 配置。

## 温度墙 (Temperature)

### 查询

```bash
# 完整温度信息
nvidia-smi -q -d TEMPERATURE

# 简洁查询（推荐）
nvidia-smi --query-gpu=index,name,temperature.gpu,temperature.gpu.tlimit,temperature.gpu.max,temperature.gpu.shutdown --format=csv
```

| 字段 | 说明 |
|------|------|
| `temperature.gpu` | 当前 GPU 温度 (°C) |
| `temperature.gpu.tlimit` | GPU T.Limit (°C) |
| `temperature.gpu.max` | 最高运行温度 (°C) |
| `temperature.gpu.shutdown` | 关机温度 (°C) |

### 修改

```bash
# 设置 GPU 目标温度 (°C)，需 sudo
# 影响 boost 算法：GPU 会尝试维持在此温度以下
sudo nvidia-smi -i 0 -gtt 90
sudo nvidia-smi -i 1 -gtt 90

# 两张同时设置
sudo nvidia-smi -i 0,1 -gtt 88
```

**注意：**
- `-gtt` 是临时设置，重启后恢复
- RTX 3090 的 Shutdown/Slowdown/Max Operating 温度是固件锁定的，无法修改
- Target Temperature 仅影响 boost 行为，不改变硬温度墙

## 性能模式 (Performance State)

### PState 说明

| PState | 含义 |
|--------|------|
| P0 | 最高性能 (全速运行) |
| P2 | 中等性能 (当前默认) |
| P8 | 低功耗待机 |
| P12 | 最低功耗 (空闲) |

**注意：** 消费级 RTX 3090 **不支持**强制锁定 P0，时钟频率由驱动动态调节。

### 查询

```bash
# 简洁查询
nvidia-smi --query-gpu=index,pstate,clocks.current.graphics,clocks.current.memory,clocks.max.graphics,clocks.max.memory --format=csv

# 完整时钟信息
nvidia-smi -q -d CLOCK

# 查看降频原因（哪个因素在限制频率）
nvidia-smi -q -d CLOCK | grep -A20 "Clocks Event Reasons"
```

### 保持高性能

消费级卡无法直接锁定 P0，但有以下几种方式让 GPU 保持高频：

**方法1：Persistence Mode（推荐）**
```bash
# 开启：驱动常驻，GPU 响应更快，不会频繁降频
sudo nvidia-smi -pm 1 -i 0,1

# 关闭
sudo nvidia-smi -pm 0 -i 0,1
```

**方法2：设置 Application Clocks**
```bash
# 设置应用时钟上限 (memory,graphics)，单位 MHz
# 让 GPU 在运行应用时保持指定频率
sudo nvidia-smi -ac 9751,2115 -i 0
sudo nvidia-smi -ac 9751,2115 -i 1

# 恢复默认
sudo nvidia-smi -rac -i 0,1
```

**方法3：锁定 GPU Clocks（强制固定频率）**
```bash
# 锁死 GPU 频率在最大值，不随负载变化
sudo nvidia-smi -lgc 2115,2115 -i 0
sudo nvidia-smi -lgc 2115,2115 -i 1

# 恢复默认
sudo nvidia-smi -rgc -i 0,1
```

**方法4：锁定 Memory Clocks**
```bash
# 锁死显存频率
sudo nvidia-smi -lmc 9751,9751 -i 0,1

# 恢复默认
sudo nvidia-smi -rmc -i 0,1
```

### 推荐组合

追求最高性能时，推荐同时设置：
```bash
# 1. 开启 persistence mode
sudo nvidia-smi -pm 1 -i 0,1

# 2. 拉高功耗墙
sudo nvidia-smi -pl 380 -i 0,1

# 3. 提高目标温度
sudo nvidia-smi -gtt 90 -i 0,1

# 4. 设置应用时钟上限
sudo nvidia-smi -ac 9751,2115 -i 0,1
```

恢复默认一键命令：
```bash
sudo nvidia-smi -pm 0 -rac -rgc -rmc -pl default -i 0,1
```

**注意：** 以上所有设置都是临时的，重启或驱动重载后恢复。

## 常用组合命令

```bash
# 一键查看所有关键指标
nvidia-smi --query-gpu=index,pstate,temperature.gpu,power.draw,power.limit,power.max_limit,clocks.current.graphics,clocks.current.memory,clocks.max.graphics,clocks.max.memory --format=csv

# 持续监控（每2秒刷新）
nvidia-smi -l 2

# 查看降频原因
nvidia-smi -q -d CLOCK | grep -A20 "Clocks Event Reasons"
```
