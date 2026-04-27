# pynvml 风扇速度相关 API 参考

## 风扇控制策略常量

| 常量 | 值 | 说明 |
|------|-----|------|
| `NVML_FAN_POLICY_TEMPERATURE_CONTINOUS_SW` | 0 | 温度控制策略（默认，由驱动自动调节风扇） |
| `NVML_FAN_POLICY_MANUAL` | 1 | 手动控制策略（用户自定义风扇转速） |

## 风扇状态常量

| 常量 | 值 | 说明 |
|------|-----|------|
| `NVML_FAN_NORMAL` | 0 | 风扇运行正常 |
| `NVML_FAN_FAILED` | 1 | 风扇故障 |

## 数据结构

### `c_nvmlFanSpeedInfo_t`

用于 `nvmlDeviceGetFanSpeedRPM` 的返回值结构体：

| 字段 | 类型 | 说明 |
|------|------|------|
| `version` | `c_uint` | 结构体版本号，设置为 `nvmlFanSpeedInfo_v1` |
| `fan` | `c_uint` | 风扇索引（通常为 0） |
| `speed` | `c_uint` | 风扇转速（RPM） |

### `nvmlFanSpeedInfo_v1`

结构体版本号常量，值 `0x100000C`（`16777228`）。

---

## API 函数

### 1. 获取风扇数量

```python
def nvmlDeviceGetNumFans(device)
```

- **参数**:
  - `device`: GPU 设备句柄
- **返回**: 风扇数量（`int`）
- **说明**: 返回 GPU 上的风扇总数

**示例**:
```python
fan_count = nvmlDeviceGetNumFans(handle)
print(f"风扇数量: {fan_count}")
```

### 2. 获取风扇转速（v1，已弃用）

```python
def nvmlDeviceGetFanSpeed(handle)
```

- **参数**:
  - `handle`: GPU 设备句柄
- **返回**: 风扇转速百分比（`int`，范围 0-100）
- **说明**: 仅适用于单风扇 GPU，已弃用，推荐使用 v2

**示例**:
```python
speed = nvmlDeviceGetFanSpeed(handle)
print(f"风扇转速: {speed}%")
```

### 3. 获取指定风扇转速（v2）

```python
def nvmlDeviceGetFanSpeed_v2(handle, fan)
```

- **参数**:
  - `handle`: GPU 设备句柄
  - `fan`: 风扇索引，从 0 开始
- **返回**: 风扇转速百分比（`int`，范围 0-100）
- **说明**: 适用于多风扇 GPU，0% 表示停止，100% 表示全速

**示例**:
```python
for i in range(fan_count):
    speed = nvmlDeviceGetFanSpeed_v2(handle, i)
    print(f"风扇 {i} 转速: {speed}%")
```

### 4. 获取风扇目标转速

```python
def nvmlDeviceGetTargetFanSpeed(handle, fan)
```

- **参数**:
  - `handle`: GPU 设备句柄
  - `fan`: 风扇索引，从 0 开始
- **返回**: 目标风扇转速百分比（`int`，范围 0-100）
- **说明**: 返回驱动当前的目标风扇转速，可能与实际转速有差异

**示例**:
```python
target = nvmlDeviceGetTargetFanSpeed(handle, 0)
print(f"风扇 0 目标转速: {target}%")
```

### 5. 获取风扇转速（RPM）

```python
def nvmlDeviceGetFanSpeedRPM(handle)
```

- **参数**:
  - `handle`: GPU 设备句柄
- **返回**: 风扇转速（`int`，单位 RPM）
- **说明**: 内部使用 `c_nvmlFanSpeedInfo_t` 结构体，当前仅查询风扇 0；并非所有 GPU 都支持此 API

**示例**:
```python
rpm = nvmlDeviceGetFanSpeedRPM(handle)
print(f"风扇转速: {rpm} RPM")
```

### 6. 获取风扇转速范围

```python
def nvmlDeviceGetMinMaxFanSpeed(handle, minSpeed=c_uint(), maxSpeed=c_uint())
```

- **参数**:
  - `handle`: GPU 设备句柄
  - `minSpeed`: 可选，传入 `c_uint` 引用以获取最小值（默认 `c_uint()`）
  - `maxSpeed`: 可选，传入 `c_uint` 引用以获取最大值（默认 `c_uint()`）
- **返回**:
  - 默认调用返回 `[minSpeed, maxSpeed]` 列表（两个 `int` 值，单位百分比）
  - 传入引用时返回 `NVML_SUCCESS`
- **说明**: 返回风扇可设置的最小和最大转速百分比

**示例**:
```python
# 默认用法
min_spd, max_spd = nvmlDeviceGetMinMaxFanSpeed(handle)
print(f"风扇转速范围: {min_spd}% - {max_spd}%")
```

### 7. 获取风扇控制策略（v2）

```python
def nvmlDeviceGetFanControlPolicy_v2(handle, fan, fanControlPolicy=c_uint())
```

- **参数**:
  - `handle`: GPU 设备句柄
  - `fan`: 风扇索引，从 0 开始
  - `fanControlPolicy`: 可选，传入 `c_uint` 引用以获取策略值（默认 `c_uint()`）
- **返回**:
  - 默认调用返回策略值（`int`）：0 = 温度控制，1 = 手动控制
  - 传入引用时返回 `NVML_SUCCESS`
- **说明**: 适用于 Maxwell 或更新架构的 GPU

**示例**:
```python
policy = nvmlDeviceGetFanControlPolicy_v2(handle, 0)
if policy == NVML_FAN_POLICY_MANUAL:
    print("手动控制模式")
else:
    print("温度控制模式")
```

### 8. 设置风扇控制策略

```python
def nvmlDeviceSetFanControlPolicy(handle, fan, fanControlPolicy)
```

- **参数**:
  - `handle`: GPU 设备句柄
  - `fan`: 风扇索引，从 0 开始
  - `fanControlPolicy`: 控制策略，`NVML_FAN_POLICY_MANUAL` 或 `NVML_FAN_POLICY_TEMPERATURE_CONTINOUS_SW`
- **返回**: `NVML_SUCCESS`
- **说明**: 设置风扇控制策略；适用于 Maxwell 或更新架构的 GPU

**示例**:
```python
# 切换为手动控制
nvmlDeviceSetFanControlPolicy(handle, 0, NVML_FAN_POLICY_MANUAL)

# 切换为温度控制
nvmlDeviceSetFanControlPolicy(handle, 0, NVML_FAN_POLICY_TEMPERATURE_CONTINOUS_SW)
```

### 9. 设置风扇转速（v2）

```python
def nvmlDeviceSetFanSpeed_v2(handle, index, speed)
```

- **参数**:
  - `handle`: GPU 设备句柄
  - `index`: 风扇索引，从 0 开始
  - `speed`: 目标转速百分比（`int`，范围 0-100）
- **返回**: `NVML_SUCCESS`
- **说明**:
  - **调用此函数会自动将风扇控制策略切换为手动模式**
  - 需要自行监控温度并调整风扇转速，设置过低可能导致 GPU 过热
  - 适用于 Maxwell 或更新架构的 GPU
  - 使用 `nvmlDeviceSetDefaultFanSpeed_v2` 恢复默认控制策略

**示例**:
```python
# 设置风扇 0 为 70% 转速
nvmlDeviceSetFanSpeed_v2(handle, 0, 70)

# 设置所有风扇为 50% 转速
for i in range(fan_count):
    nvmlDeviceSetFanSpeed_v2(handle, i, 50)
```

### 10. 恢复默认风扇控制

```python
def nvmlDeviceSetDefaultFanSpeed_v2(handle, index)
```

- **参数**:
  - `handle`: GPU 设备句柄
  - `index`: 风扇索引，从 0 开始
- **返回**: `NVML_SUCCESS`
- **说明**: 恢复风扇的默认控制策略（温度自动控制）

**示例**:
```python
# 恢复风扇 0 为自动模式
nvmlDeviceSetDefaultFanSpeed_v2(handle, 0)

# 恢复所有风扇为自动模式
for i in range(fan_count):
    nvmlDeviceSetDefaultFanSpeed_v2(handle, i)
```

---

## 实用函数封装

```python
from pynvml import *

def get_all_fan_speeds(handle):
    """获取 GPU 所有风扇的转速信息"""
    fan_count = nvmlDeviceGetNumFans(handle)
    fans = []
    for i in range(fan_count):
        speed = nvmlDeviceGetFanSpeed_v2(handle, i)
        target = nvmlDeviceGetTargetFanSpeed(handle, i)
        policy = nvmlDeviceGetFanControlPolicy_v2(handle, i)
        fans.append({
            'index': i,
            'speed': speed,
            'target': target,
            'policy': 'manual' if policy == NVML_FAN_POLICY_MANUAL else 'auto',
        })
    return fans

def set_all_fan_speed(handle, speed):
    """设置所有风扇到指定转速"""
    fan_count = nvmlDeviceGetNumFans(handle)
    for i in range(fan_count):
        nvmlDeviceSetFanSpeed_v2(handle, i, speed)

def reset_all_fan_speed(handle):
    """恢复所有风扇为自动控制"""
    fan_count = nvmlDeviceGetNumFans(handle)
    for i in range(fan_count):
        nvmlDeviceSetDefaultFanSpeed_v2(handle, i)

# 使用示例
nvmlInit()
handle = nvmlDeviceGetHandleByIndex(0)

# 获取风扇信息
fans = get_all_fan_speeds(handle)
for f in fans:
    print(f"风扇 {f['index']}: {f['speed']}% (目标: {f['target']}%, 策略: {f['policy']})")

# 设置风扇转速
set_all_fan_speed(handle, 70)

# 使用完后恢复
reset_all_fan_speed(handle)

nvmlShutdown()
```

## 重要注意事项

1. **速度单位**: `nvmlDeviceGetFanSpeed_v2` / `nvmlDeviceSetFanSpeed_v2` 使用百分比（0-100），`nvmlDeviceGetFanSpeedRPM` 使用 RPM
2. **v1 vs v2**: `nvmlDeviceGetFanSpeed`（无 _v2）仅适用于单风扇 GPU，多风扇 GPU 应使用 `nvmlDeviceGetFanSpeed_v2`
3. **无 v1 设置 API**: pynvml 中不存在 `nvmlDeviceSetFanSpeed`（无 _v2），设置风扇转速只能使用 v2 版本
4. **自动切换策略**: 调用 `nvmlDeviceSetFanSpeed_v2` 会自动将控制策略切换为手动模式，退出时需调用 `nvmlDeviceSetDefaultFanSpeed_v2` 恢复
5. **GPU 架构要求**: `nvmlDeviceSetFanSpeed_v2`、`nvmlDeviceSetDefaultFanSpeed_v2`、`nvmlDeviceSetFanControlPolicy` 要求 GPU 为 Maxwell 或更新架构
6. **多风扇 GPU**: 设置/恢复风扇时，需要对每个风扇单独调用 API（索引从 0 到 `fan_count - 1`）
7. **权限要求**: 设置风扇转速和策略需要 root 权限
8. **RPM API 限制**: `nvmlDeviceGetFanSpeedRPM` 当前仅支持查询风扇 0，且不是所有 GPU 都支持
9. **nvmlDeviceGetFanSpeedRPM 返回值**: 该函数内部硬编码 `fan = 0`，仅返回 0 号风扇的 RPM

## 与 NVIDIA NVML C API 的差异

| 特性 | NVML C API | pynvml 包装 |
|------|-----------|------------|
| `nvmlDeviceGetFanSpeed` | 需要传入 `unsigned int*` 指针 | 直接返回 `int` |
| `nvmlDeviceGetFanSpeed_v2` | 需要传入 `unsigned int*` 指针 | 直接返回 `int` |
| `nvmlDeviceGetFanSpeedRPM` | 需要传入 `nvmlFanSpeedInfo_t*` 指针 | 直接返回 RPM（`int`） |
| `nvmlDeviceGetMinMaxFanSpeed` | 需要传入两个 `unsigned int*` 指针 | 默认返回 `[min, max]` 列表 |
| `nvmlDeviceGetFanControlPolicy_v2` | 需要传入 `nvmlFanControlPolicy_t*` 指针 | 默认返回策略值（`int`） |
| 返回值 | 返回 `nvmlReturn_t` 错误码 | 直接返回结果值；异常用 `NVMLError` 抛出 |
