# AgenticAttorney

基于 AutoGen 的逆转裁判风格辩论生成器。

## 项目结构

### 代码：

- `main.py`: 主入口
- `src/core/actor.py`: 辩论引擎
- `src/core/director/`: 剧本生成
- `src/agents/`: Agent 定义与管理
- `src/prompts/`: 提示词模板
- `src/types/`: 类型定义
- `src/tools/`: MCP 工具管理
- `src/outputs/`: 输出格式化

### 剧情提示词:

- `prompts/init.md`: 辩论开始
- `prompts/prepare.md`: 准备阶段
- `prompts/final.md`: 最终审判
- `prompts/selector.md`: 角色选择

### 剧情介绍

- `prompts/topics/*.md`: 剧本介绍

### 角色提示词:

- `prompts/agents/common/`: 角色相关的公共部分
- `prompts/agents/prosecution/`: 检察官
- `prompts/agents/defense/`: 辩护律师
- `prompts/agents/judge/`: 法官
- `prompts/agents/witness/`: 证人

### 配置文件:

- `config.example.json`: 配置示例
- `config.json`: 配置文件（需自行创建）

## 子系统说明

- [Actor 辩论系统](README.actor.md): 辩论引擎，管理多 agent 辩论流程
- [Director 剧本生成](README.director.md): 将辩论日志转换为 objection.lol 剧本

## 使用

### 安装依赖

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 创建配置文件

复制 `config.example.json` 为 `config.json`，并根据需求修改

### 运行

```bash
python main.py
```

## 许可证

MIT
