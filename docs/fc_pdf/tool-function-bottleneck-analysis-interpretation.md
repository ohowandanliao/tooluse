# Tool Function Bottleneck Analysis 解读版

这份文档是给“看完 `tool-function-bottleneck-analysis.md` 还是觉得抽象”的人写的。

目标只有一个：

- 把里面的核心名词翻成人话
- 给出小例子
- 帮你看懂这份 `pro` 结果到底在建议什么

原文：

- `docs/fc_pdf/tool-function-bottleneck-analysis.md`

## 一句话先说结论

`pro` 不是在说“你现在的方法一定错了”，而是在说：

> 先别急着做新方法。
> 先证明当前 function calling 到底是：
> 不会决策，
> 不会把语义映射到工具接口，
> 还是不会在大工具池里搜和校准。

也就是先回答：

- `decision` 是不是主问题？
- `interface-grounding` 是不是主问题？
- `search/calibration` 是不是主问题？

如果这个问题都没分清，后面做什么方法都容易打偏。

## 为什么它不建议第一篇直接上 multi-turn / agent RL

核心不是 “multi-turn 不重要”。

而是：

- `multi-turn` 会混进：
  - 记忆前文
  - 状态跟踪
  - 多步规划
  - 中途改目标
- `agent RL` 会再混进：
  - delayed reward
  - credit assignment
  - exploration

这样一来，你就很难再回答：

> 这次失败到底是因为 tool/function 定义不好，
> 还是因为模型忘了前文、规划错了、奖励没学好？

所以 `pro` 的建议是：

- 第一篇：`single-turn clean measurement`
- 第二篇：再看 `multi-turn` 会不会放大同一个问题
- 更后面：才讨论 `agent RL`

## 三个瓶颈到底是什么意思

### 1. decision bottleneck

意思是：

- 模型根本没理解用户要干什么
- 或者没判断对“该不该调用工具”

例子：

用户说：

> 帮我看看北京明天会不会下雨。

工具有：

- `get_weather`
- `book_hotel`

如果模型去调了 `book_hotel`，
那问题大概率不是接口名写得不好，
而是它连任务方向都没理解对。

这更接近 `decision bottleneck`。

再比如：

用户说：

> 你好呀

模型却硬调了工具。

这也是 `decision` 问题，不是接口问题。

### 2. interface-grounding bottleneck

意思是：

- 模型其实知道要查天气
- 但它不能稳定地把这个语义映射到当前工具接口

例子：

同一个天气工具，我们写两种等价定义。

版本 A：

```json
{
  "name": "get_weather",
  "parameters": {
    "city": "string",
    "date": "string"
  }
}
```

版本 B：

```json
{
  "name": "query_forecast",
  "parameters": {
    "geo_target": "string",
    "travel_day": "string"
  }
}
```

这两个工具语义一样。

如果模型在 A 上表现好，在 B 上明显掉点，
尤其掉在：

- 参数 key 写错
- 参数 value 对不上
- 输出格式不合法

那更像是 `interface-grounding bottleneck`。

也就是：

> 它知道要做什么，
> 但不会把“要做的事”正确翻译成当前接口语言。

### 3. search/calibration bottleneck

意思是：

- 模型未必不懂任务
- 也未必不懂接口
- 但工具池一大、有近似工具、无关工具一多，它就搜错或判断错

例子：

工具池里不再只有一个天气工具，而是有：

- `get_weather`
- `get_air_quality`
- `get_city_events`
- `get_temperature_history`
- `get_travel_advice`

用户说：

> 帮我看看北京明天会不会下雨。

如果工具池一大，模型越来越容易选错工具，
那这更像 `search/calibration` 问题。

不是因为某个工具的参数名写得差，
而是它在很多候选里找不准、判不稳。

## 文档里几个最关键的术语

### 1. semantic-equivalent schema perturbation

翻成人话：

> 任务语义不变，只改工具接口的表面写法。

比如：

- 改 tool name
- 改 arg name
- 改 description
- 改参数顺序

但不能改真正要做的事。

这就是你现在仓库里 paired schema 能直接做的事情。

### 2. friendly vs hostile schema

`friendly schema`：

- 更自然
- 更容易让模型理解
- 但不能偷偷多给语义信息

`hostile schema`：

- 更别扭、更不直观
- 但必须和 friendly 在信息量上等价

坏例子：

- friendly 有详细描述
- hostile 直接把描述删掉一半

这就不叫“接口更差”，而叫“信息更少”。

如果这样做，结论不干净。

### 3. oracle

`oracle` 可以理解成“上帝提示”。

也就是：

为了定位瓶颈，
我们临时把某一层错误消掉，
看性能能恢复多少。

#### oracle decision

相当于告诉模型：

> 这题确实应该 call，不是 no-call，也不是 clarify。

如果这样一给，性能大涨，
说明 decision 问题很大。

#### oracle tool identity

相当于告诉模型：

> 正确工具就是天气工具，别再猜了。

如果这样一给，性能大涨，
说明 tool 选择或搜索是主问题。

#### oracle CIR / semantic slots

这是更强的 oracle。

相当于直接告诉模型：

> 这题真正的语义槽位就是：
> city = 北京
> date = 明天

它接下来只需要把这些语义槽位编译成当前工具接口。

如果 tool oracle 之后还会错，
但 CIR oracle 一给就恢复很多，
就说明：

> 问题主要在 interface-grounding。

## CIR 到底是什么

CIR = canonical intermediate representation

你可以先把它想成：

> 和具体工具接口无关的中间语义表达

例子：

用户：

> 帮我看看北京明天会不会下雨。

工具接口可能写成：

- `city`, `date`
- `geo_target`, `travel_day`
- `location_name`, `forecast_time`

但 CIR 应该统一写成更抽象的东西，比如：

```json
{
  "intent": "weather_lookup",
  "slots": {
    "city": "北京",
    "date": "明天"
  }
}
```

注意：

- CIR 不能偷带具体 schema 的命名
- 不然它就不是“canonical”，而只是伪装后的接口

## no-call / clarify / direct-answer / impossible 是什么

`pro` 建议别只做“call / no-call”二分类。

因为很多场景不止两种情况。

### call

该调工具。

例子：

> 查一下北京明天的天气。

### clarify

信息不够，应该先追问。

例子：

> 帮我订明天的票。

但没说：

- 什么票
- 去哪
- 几点

这时最合理的不是乱调工具，而是先问清楚。

### direct-answer

根本不用调工具，直接回答。

例子：

> 你好

### impossible-with-tools

当前工具池根本做不了。

例子：

> 帮我读取我脑子里现在在想什么。

如果把这些情况全压成 `no-call`，
任务会太粗，
你也更难分清楚模型到底哪里错了。

## ranking changes 是什么意思

意思是：

模型在普通接口上的排名，
和在改写后的等价接口上的排名，
会不会发生变化。

例子：

- 模型 A 在原始 schema 上第一
- 模型 B 在原始 schema 上第二

但一旦把工具名和参数名改得更 opaque：

- 模型 B 反而超过模型 A

这说明：

> 原来的 leaderboard 分数，不只是测语义能力，
> 还在测这个模型和当前接口写法配不配。

这个观察对 measurement 论文很有价值。

## 这份 pro 结果真正建议你做什么

最核心的不是“优化 schema”。

而是先做这两件事：

### 第一件：做 clean measurement

也就是在干净的 single-turn 条件下，
分清：

- 错在 decision
- 错在 interface-grounding
- 错在 search/calibration

### 第二件：只有 measurement 成立后，再想方法

如果结果真的显示：

- interface-grounding 是 first-order bottleneck

那后面才自然会导出方法线，比如：

- `canonical semantic IR + schema compiler`
- `interface-invariant training`
- `automated schema optimization`

## 这对你现在仓库里的东西意味着什么

### 不是都没用了

你之前做的这些东西仍然有价值：

- paired schema
  - 可以直接当 schema perturbation instrument
- exact evaluator
  - 还能继续做 end-to-end exact correctness
- xLAM baseline runtime
  - 还能用来观察 direct baseline 对 schema 的敏感性

### 但角色变了

它们现在更像：

- 论文地基
- measurement 工具
- baseline 参照

而不是：

- 直接就能支撑主方法 claim 的证据

## 你现在最该记住的 5 句话

1. `pro` 现在推荐你先写 measurement，不是先写方法。
2. 第一篇最好是 `single-turn causal measurement paper`。
3. `multi-turn / agent RL` 现在更像后续放大镜，不是第一篇主对象。
4. 你之前的 paired schema 工作没有白做，它现在是 instrument。
5. 真正最值得做的，是先证明 interface-grounding 到底是不是 first-order bottleneck。
