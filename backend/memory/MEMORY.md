# Long-term Memory

## 项目背景

## 经验教训

### 2026-03-10：网络请求工具的可靠性

- 问题：`fetch_url` 工具和 `terminal curl` 在当前环境下多次超时或失败
- 有效方案：`python_repl` + `requests` 库是最可靠的网络请求方式
- 下次提示：遇到网络请求任务时，优先使用 `python_repl` + `requests`，设置 timeout 参数（10-15秒）

### 2026-03-10：天气查询 API 选择

- 问题：wttr.in 接口不稳定，多次超时
- 有效方案：Open-Meteo API 响应更快、更稳定
- 下次提示：天气查询优先使用 Open-Meteo API（需提供经纬度坐标）

## 用户偏好

- 用户希望 Agent 在遇到失败时尝试多种方式，而不是轻易放弃
- 用户希望 Agent 总结经验教训，避免重复踩坑
