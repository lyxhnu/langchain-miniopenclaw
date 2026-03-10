---
name: 联网搜索
description: 使用 Tavily 联网搜索最新信息、官方文档、新闻动态、实时行情和外部事实来源。适用于用户明确要求搜索、联网、查官网、给链接、核验事实，或任务明显依赖实时外部信息的场景。优先调用本技能目录下的 Tavily 脚本，不要退回抓搜索结果页。
---

## 目标

用 Tavily Search API 返回可追溯的联网结果，并给出带来源链接和时间说明的中文结论。

## 必备前提

- 环境变量 `TAVILY_API_KEY` 必须存在。
- 默认使用这个脚本发起搜索：

```powershell
python skills/web-search/scripts/tavily_search.py --query "查询词"
```

- 如果 `TAVILY_API_KEY` 缺失、鉴权失败、限流或 API 报错，要明确说明失败原因。
- 不要假装联网成功，也不要偷偷切换到其他搜索引擎。

## 查询策略

1. 先把用户问题压缩成 1 个主查询，尽量控制在 400 个字符以内。
2. 复杂问题拆成多个子查询，不要把多个主题塞进一个长 prompt。
3. 按场景选择 `topic`：
   - `general`：官网、文档、常规事实、产品信息
   - `news`：最新消息、今日动态、近期事件
   - `finance`：黄金价格、股票、汇率、财务或市场数据
4. 默认用 `search_depth=basic`；只有在需要更高相关性或更细碎证据时才改 `advanced`。
5. 对明显有时间性的查询，加 `--time-range day|week|month|year`。
6. 对金融查询，优先把中文需求改写成英文 ticker、市场和计价单位。
   - 好于：`今天黄金价格`
   - 更推荐：`XAU USD price today`
   - 或：`spot gold price USD per ounce`
7. 如果金融查询第一次结果为空，先把查询词改成英文 ticker 形式再重试一次。
8. 对官方信息，优先加域名过滤：
   - `--include-domain docs.langchain.com`
   - `--include-domain openai.com`
9. 如果用户要求来源可核验，优先选高分且权威的结果；必要时再用 `fetch_url` 直接抓取 Tavily 返回的 1 到 2 个链接正文。

## 推荐命令

### 官方文档

```powershell
python skills/web-search/scripts/tavily_search.py --query "LangChain create_agent" --topic general --include-domain docs.langchain.com --max-results 3
```

### 最新动态

```powershell
python skills/web-search/scripts/tavily_search.py --query "OpenAI API 最新更新" --topic news --time-range month --max-results 5
```

### 金融行情

```powershell
python skills/web-search/scripts/tavily_search.py --query "XAU USD price today" --topic finance --time-range day --max-results 5
```

## 执行步骤

1. 判断问题是否真的需要联网，以及是否属于 `general / news / finance`。
2. 运行 Tavily 脚本，读取返回的 JSON。
3. 优先关注：
   - `results[].title`
   - `results[].url`
   - `results[].score`
   - `results[].published_date`
   - `results[].content`
4. 如果结果足够明确，直接整理答案并给出来源。
5. 如果问题高风险、细节敏感，或多个结果冲突：
   - 先换更具体的查询词重试一次
   - 再用 `fetch_url` 抓取 Tavily 返回的候选 URL 正文核验
6. 对“今天 / 最新 / 当前”这类查询，回答里必须写明本次查询日期或来源发布日期。

## 结果筛选规则

- 不要只用第一条结果下结论。
- 优先使用官方文档、官方公告、政府/学校/标准组织、主流一手媒体。
- 如果多个来源冲突，优先最新且更权威的来源，并显式说明冲突。
- 如果 Tavily 返回的是聚合页、SEO 页或低质量转载，换查询词或加域名过滤重试。

## 失败处理

1. 如果脚本报 `TAVILY_API_KEY is not set`，明确说明是本地配置缺失。
2. 如果返回 `401/403`，明确说明是 Tavily 鉴权失败。
3. 如果返回 `429`，明确说明是 Tavily 限流或额度问题。
4. 如果返回 `5xx` 或网络异常，明确说明是 Tavily 服务或链路问题。
5. 如果结果不足以支持结论，只能说“本次 Tavily 搜索证据不足”，不要编造答案。

## 输出格式

推荐输出：

```md
结论：...

依据：
1. ...
2. ...

来源：
- 标题 1: URL
- 标题 2: URL

时间说明：
- 查询时间：2026-03-10
- 或来源发布日期：2026-03-10
```

## 特别约束

- 对明显会变化的信息，不要省略时间说明。
- 对高风险信息，不要只引用二手总结页。
- 对实时行情，优先使用 `topic=finance` 并给出市场或计价单位。
