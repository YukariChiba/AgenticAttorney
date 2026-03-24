# AgenticAttorney

基于 AutoGen 的逆转裁判风格辩论生成器。

## 项目结构

### 代码：

- `main.py`: 主入口
- `src/`: 源代码

### 剧情提示词:

- `prompts/init.md`: 辩论开始
- `prompts/prepare.md`: 准备阶段
- `prompts/final.md`: 最终审判
- `prompts/selector.md`: 角色选择

### 剧情介绍

- `prompts/topics/*.md`: 剧本介绍

### 角色提示词:

- `prompts/agents/common`: 角色相关的公共部分
- `prompts/agents/prosecution`: 检察官
- `prompts/agents/defense`: 辩护律师
- `prompts/agents/judge`: 法官
- `prompts/agents/witness`: 证人

### 配置文件:

- `config.json.example`: 配置示例
- `config.json`: 配置文件（需自行创建）

## 机制说明

### 辩论环节的身份管理

辩论环节中，agent 很容易忘记自己和上一个发言的人的身份。为此引入了 Clerk Agent (书记员)，其作用是让 agent 认清上一个发言人的身份，未来可能还有其他用处。

### 起始准备环节

起始准备环节是让双方一辩 Agent 先收集一些资料，这样可以降低后续辩论中收集资料的 token 消耗，使辩论更加流畅。

### 上下文压缩

辩论过长会超出最大 context 长度限制，此时系统需要自动压缩之前的辩论内容，以保持在上下文窗口范围内。

### 结束方式

辩论有两种结束方式：
- 最大回合数：达到预设的最大发言轮次后自动结束
- 法官主动结束：由 selector 机制判断需要结束辩论，实际上是由 selector 认为辩论应该终止

## 使用

### 安装依赖

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 创建配置文件

复制 `config.json.example` 为 `config.json`，并根据需求修改

### 运行

```bash
python main.py
```

## `config.json` 配置说明

#### `debate` 辩论设置

- `max_words`：每次发言长度限制
- `max_rounds`：最大发言轮次
- `max_context`：最大上下文消息数
- `summary_context`：上下文摘要起始点

#### `mcp_servers` MCP 工具配置

预置以下 MCP 服务：
- `wikipedia-mcp`：维基百科搜索
- `@jharding_npm/mcp-server-searxng`：通用网络搜索
- `arxiv-mcp-server`：学术论文搜索
- `mcp-server-fetch`：网页抓取
- `@jjfather/civil-code-of-china-mcp`：中国民法典查询

### 添加自定义角色

在 `prompts/agents/<type>/<name>.md` 创建角色文件：

```markdown
---
name: 角色中文名
desc: 角色描述
objlol: 角色在 objection.lol 中对应的 ID，用于生成剧本，没有可以留空
---

## 立场

{stance}

## 身份

角色背景介绍...

## 性格与行动准则

1. 角色特征 1
2. 角色特征 2
...
```

可用变量：
- `{stance}`：已方观点
- `{affirmative_stance}`：正方观点
- `{negative_stance}`：反方观点
- `{max_words}`：每次发言长度

### 添加自定义辩题

在 `prompts/topics/<name>.md` 创建辩题文件：

```markdown
---
debate_topic: "辩论主题标题"
affirmative_stance: 正方立场描述
negative_stance: 反方立场描述
---

案件介绍全文...
```

### 模板变量

以下变量可在提示词模板中使用：

| 变量 | 说明 |
|------|------|
| `{stance}` | 已方观点 |
| `{affirmative_stance}` | 正方观点 |
| `{negative_stance}` | 反方观点 |
| `{affirmative_agents}` | 正方辩手列表 |
| `{negative_agents}` | 反方辩手列表 |
| `{witness_agents}` | 证人列表 |
| `{debate_topic}` | 辩论主题 |
| `{debate_topic_full}` | 案件介绍全文 |
| `{max_words}` | 每次发言长度 |
| `{max_rounds}` | 最大发言轮次 |
| `{current_date}` | 当前时间 |

### 添加自定义 MCP

在 `config.json` 的 `mcp_servers` 中添加新配置，例如：

```json
{
  "type": "stdio",
  "command": "uvx",
  "args": ["your-mcp-server"],
  "env": { "ENV_VAR": "value" },
  "read_timeout_seconds": 20
}
```

## 内置辩论主题

- `schrodinger`：「逆转的盲盒」：薛定谔的猫
- `theseus`：「逆转的船骸」：忒修斯之船
- `gene-edit`：「逆转的螺旋」：基因编辑婴儿是否合法？
- `euthanasia`：「逆转的处方笺」：安乐死是否合法？
- `ai-paint`：「逆转的画笔」：AI 模仿人类画师风格的作品是否合法？
- `simulation`：「逆转的矩阵」：我们是否生活在模拟的现实之中？
- `aliens`：「逆转的星空」：外星人存在吗？
- `chicken-egg`：「逆转的起源」：先有鸡还是先有蛋？
- `tram`：「逆转的道岔」：电车难题

## TODO

- 给 agent 增加 memory 和修改自己 memory 的工具
- 开源 AgenticAttorneyObjectionGenerator，然后与本项目合并。

## 许可证

MIT
