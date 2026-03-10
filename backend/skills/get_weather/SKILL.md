---
name: 天气查询
description: 查询指定城市的天气情况，并整理成适合直接回复用户的简洁结果。
---

## 经验教训

[重要提示] wttr.in 接口可能不稳定或无法访问（已在 2026-03-10 遇到多次失败）。
优先使用 Open-Meteo API，更稳定可靠。

[2026-03-10] 当 `fetch_url` 或 `terminal curl` 出现超时/失败时，优先使用 `python_repl` + `requests` 库。不要重复尝试同一路径。

## 执行步骤

### 方案一（优先）：Open-Meteo API + python_repl

使用 `python_repl` 执行：

```python
import requests
# 北京坐标
lat, lon = 39.9042, 116.4074
url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true"
resp = requests.get(url, timeout=10)
data = resp.json()
```

### 方案二（备用）：wttr.in + python_repl

```python
import requests
url = "https://wttr.in/Beijing?format=j1"
resp = requests.get(url, timeout=10)
data = resp.json()
```

### 方案三（最后手段）：fetch_url 或 terminal curl

仅在前两者都失败时尝试，但成功率较低。

## 故障排查

如果遇到以下情况：
- `fetch_url` 返回 "Fetch failed" 或超时
- `terminal curl` 超过 30 秒无响应
- `urllib.request` 超时

立即切换到 `python_repl` + `requests` 库，并设置合理的 timeout 参数（建议 10-15 秒）。

## 输出格式

用中文给出简明结果，包括：
- 温度
- 天气状况（需将 weathercode 转换为中文描述）
- 风速
- 数据来源和时间

## 天气代码对照表（Open-Meteo WMO Code）

- 0: 晴朗
- 1-3: 少云/多云
- 45-48: 雾
- 51-67: 雨
- 71-77: 雪
- 80-82: 阵雨
- 95-99: 雷暴
