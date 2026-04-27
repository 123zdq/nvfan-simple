# pynvml 温度相关 API 参考

## 温度传感器类型

| 常量 | 值 | 说明 |
|------|-----|------|
| `NVML_TEMPERATURE_GPU` | 0 | GPU 核心温度传感器 |
| `NVML_TEMPERATURE_COUNT` | 1 | 温度传感器数量 |

## 温度阈值类型

| 常量 | 值 | 说明 |
|------|-----|------|
| `NVML_TEMPERATURE_THRESHOLD_SHUTDOWN` | 0 | 关机温度阈值 |
| `NVML_TEMPERATURE_THRESHOLD_SLOWDOWN` | 1 | 降频温度阈值 |
| `NVML_TEMPERATURE_THRESHOLD_MEM_MAX` | 2 | 显存最大温度阈值 |
| `NVML_TEMPERATURE_THRESHOLD_GPU_MAX` | 3 | GPU 最大温度阈值 |
| `NVML_TEMPERATURE_THRESHOLD_ACOUSTIC_MIN` | 4 | 声学最小温度阈值 |
| `NVML_TEMPERATURE_THRESHOLD_ACOUSTIC_CURR` | 5 | 声学当前温度阈值 |
| `NVML_TEMPERATURE_THRESHOLD_ACOUSTIC_MAX` | 6 | 声学最大温度阈值 |
| `NVML_TEMPERATURE_THRESHOLD_GPS_CURR` | 7 | GPS 当前温度阈值 |
| `NVML_TEMPERATURE_THRESHOLD_COUNT` | 8 | 温度阈值数量 |

## 温度字段 ID (Field API)

| 常量 | 值 | 说明 |
|------|-----|------|
| `NVML_FI_DEV_MEMORY_TEMP` | 82 | 显存温度 |
| `NVML_FI_DEV_TEMPERATURE_SHUTDOWN_TLIMIT` | 193 | 关机温度限制 |
| `NVML_FI_DEV_TEMPERATURE_SLOWDOWN_TLIMIT` | 194 | 降频温度限制 |
| `NVML_FI_DEV_TEMPERATURE_MEM_MAX_TLIMIT` | 195 | 显存最大温度限制 |
| `NVML_FI_DEV_TEMPERATURE_GPU_MAX_TLIMIT` | 196 | GPU 最大温度限制 |

## API 函数

### 1. 获取 GPU 核心温度

```python
def nvmlDeviceGetTemperature(handle, sensor)
```

- **参数**:
  - `handle`: GPU 设备句柄
  - `sensor`: 传感器类型，通常为 `NVML_TEMPERATURE_GPU` (0)
- **返回**: 温度值（摄氏度，整数）

**示例**:
```python
temp = nvmlDeviceGetTemperature(handle, NVML_TEMPERATURE_GPU)
print(f"GPU 核心温度：{temp}°C")
```

### 2. 获取温度阈值

```python
def nvmlDeviceGetTemperatureThreshold(handle, threshold)
```

- **参数**:
  - `handle`: GPU 设备句柄
  - `threshold`: 阈值类型（见"温度阈值类型"表）
- **返回**: 温度阈值（摄氏度，整数）

**示例**:
```python
# 获取 GPU 最大温度阈值
gpu_max = nvmlDeviceGetTemperatureThreshold(handle, NVML_TEMPERATURE_THRESHOLD_GPU_MAX)
print(f"GPU 最大温度阈值：{gpu_max}°C")

# 获取显存最大温度阈值
mem_max = nvmlDeviceGetTemperatureThreshold(handle, NVML_TEMPERATURE_THRESHOLD_MEM_MAX)
print(f"显存最大温度阈值：{mem_max}°C")

# 获取关机温度阈值
shutdown = nvmlDeviceGetTemperatureThreshold(handle, NVML_TEMPERATURE_THRESHOLD_SHUTDOWN)
print(f"关机温度阈值：{shutdown}°C")
```

### 3. 设置温度阈值

```python
def nvmlDeviceSetTemperatureThreshold(handle, threshold, temp)
```

- **参数**:
  - `handle`: GPU 设备句柄
  - `threshold`: 阈值类型
  - `temp`: 温度值（摄氏度）
- **返回**: None

**示例**:
```python
# 设置 GPU 最大温度阈值为 85°C
nvmlDeviceSetTemperatureThreshold(handle, NVML_TEMPERATURE_THRESHOLD_GPU_MAX, 85)
```

### 4. 获取显存温度（Field API）

```python
def nvmlDeviceGetFieldValues(handle, fieldIds)
```

- **参数**:
  - `handle`: GPU 设备句柄
  - `fieldIds`: 字段 ID 列表（长度自动计算，无需额外传参）
- **返回**: `c_nvmlFieldValue_t` 数组

**示例**:
```python
def get_memory_temperature(handle):
    """获取显存温度"""
    field_ids = [NVML_FI_DEV_MEMORY_TEMP]
    values = nvmlDeviceGetFieldValues(handle, field_ids)
    
    # 根据值类型获取温度
    if values[0].valueType == NVML_VALUE_TYPE_UNSIGNED_INT:
        return values[0].value.uiVal
    elif values[0].valueType == NVML_VALUE_TYPE_SIGNED_INT:
        return values[0].value.siVal
    else:
        return values[0].value.dVal

mem_temp = get_memory_temperature(handle)
print(f"显存温度：{mem_temp}°C")
```

### 5. 获取热设置信息

```python
def nvmlDeviceGetThermalSettings(device, sensorindex, c_thermalsettings=c_nvmlGpuThermalSettings_t())
```

- **参数**:
  - `device`: GPU 设备句柄
  - `sensorindex`: 传感器索引
  - `c_thermalsettings`: 可选，传入预分配的 `c_nvmlGpuThermalSettings_t` 结构体（默认自动创建）
- **返回**:
  - 默认调用返回 `c_nvmlGpuThermalSensor_t` 列表（传感器数组）
  - 传入结构体时返回 `NVML_SUCCESS`
- **说明**: `c_nvmlGpuThermalSensor_t` 结构体包含以下字段：
  - `controller`: 温控器 ID
  - `defaultMinTemp`: 默认最小温度
  - `defaultMaxTemp`: 默认最大温度
  - `currentTemp`: 当前温度
  - `target`: 目标值

**示例**:
```python
# 默认用法，返回传感器列表
sensors = nvmlDeviceGetThermalSettings(handle, 0)
for s in sensors:
    print(f"默认温度范围: {s.defaultMinTemp}°C - {s.defaultMaxTemp}°C")
```

### 6. 获取机箱温度（Unit API）

```python
def nvmlUnitGetTemperature(unit, type)
```

- **参数**:
  - `unit`: 单元句柄
  - `type`: 温度类型
- **返回**: 温度值

**说明**: 用于获取机箱/单元级别的温度，不是 GPU 温度

## 值类型常量

用于 Field API 返回值解析：

| 常量 | 值 | 说明 |
|------|-----|------|
| `NVML_VALUE_TYPE_DOUBLE` | 0 | 双精度浮点数 |
| `NVML_VALUE_TYPE_UNSIGNED_INT` | 1 | 无符号整数 |
| `NVML_VALUE_TYPE_SIGNED_INT` | 5 | 有符号整数 |

## 实用函数封装

```python
from pynvml import *

def get_all_temperatures(handle):
    """获取 GPU 所有温度信息"""
    temps = {}
    
    # GPU 核心温度
    temps['gpu_core'] = nvmlDeviceGetTemperature(handle, NVML_TEMPERATURE_GPU)
    
    # 显存温度
    try:
        values = nvmlDeviceGetFieldValues(handle, [NVML_FI_DEV_MEMORY_TEMP])
        if values[0].valueType == NVML_VALUE_TYPE_UNSIGNED_INT:
            temps['memory'] = values[0].value.uiVal
        elif values[0].valueType == NVML_VALUE_TYPE_SIGNED_INT:
            temps['memory'] = values[0].value.siVal
        else:
            temps['memory'] = values[0].value.dVal
    except:
        temps['memory'] = None
    
    # 温度阈值
    temps['threshold_gpu_max'] = nvmlDeviceGetTemperatureThreshold(handle, NVML_TEMPERATURE_THRESHOLD_GPU_MAX)
    temps['threshold_mem_max'] = nvmlDeviceGetTemperatureThreshold(handle, NVML_TEMPERATURE_THRESHOLD_MEM_MAX)
    temps['threshold_shutdown'] = nvmlDeviceGetTemperatureThreshold(handle, NVML_TEMPERATURE_THRESHOLD_SHUTDOWN)
    
    return temps

# 使用示例
nvmlInit()
handle = nvmlDeviceGetHandleByIndex(0)
temps = get_all_temperatures(handle)
for name, value in temps.items():
    print(f"{name}: {value}°C" if value is not None else f"{name}: N/A")
nvmlShutdown()
```

## 注意事项

1. **温度单位**: 所有温度值单位为摄氏度（°C）
2. **GPU 型号差异**: 不同 GPU 型号支持的传感器和阈值可能不同
3. **权限要求**: 需要 root 或 sudo 权限才能访问 NVML
4. **Field API**: 某些 GPU 可能不支持 Field API，需要异常处理
5. **温度墙**: 使用 `NVML_TEMPERATURE_THRESHOLD_GPU_MAX` 获取 GPU 的温度墙，用于动态调整风扇控制上限
