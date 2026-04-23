# Python 版本兼容性说明

## 推荐版本

**Python 3.9+**

## 详细说明

### 依赖分析

| 组件 | 版本要求 | 备注 |
|------|----------|------|
| pynvml (nvidia-ml-py) | 无明确限制 | 官方文档称 Python 2.5+，实际已默认 Python 3 |
| 本项目代码 | Python 3.6+ | 使用 f-string |
| 实际推荐 | Python 3.9-3.12 | 主流 LTS 版本 |

### Ubuntu 版本对应

| Ubuntu LTS | 默认 Python | 推荐度 |
|------------|-------------|--------|
| 22.04 | 3.10 | ✅ 推荐 |
| 24.04 | 3.12 | ✅ 推荐 |
| 20.04 | 3.8 | ⚠️ 最低可用 |

### 安装建议

```toml
# pyproject.toml 或 requirements.txt
python>=3.9
nvidia-ml-py>=12.535
```

### 已验证版本

- ✅ Python 3.12 (当前环境)
- ✅ Python 3.10 (Ubuntu 22.04)
- ⚠️ Python 3.8 (理论上可用，未实测)

### 注意事项

1. pynvml 是纯 Python 绑定，无 C 扩展，版本兼容性良好
2. 代码仅使用基础特性（f-string、class、signal），无高级语法
3. 作为 systemd 服务运行，建议使用 LTS 版本的 Python
