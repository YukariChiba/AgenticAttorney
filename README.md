# AgenticDebates

基于 AutoGen 的逆转裁判风格辩论生成器。

## Usage

### 修改 `config.py`：

- 修改 `model_config` 以使用您自己的模型（默认从 `MODEL_API_NAME` `MODEL_API_URL` `MODEL_API_KEY` 读取环境变量），建议使用带思考的模型
- 修改 `topic_config` 选择案件
- 修改 `max_words` 确定每次发言长度
- 修改 `max_rounds` 确定最大发言轮次
- 修改 `max_buffer` 确定上下文长度
- 修改 `teams` 增加、删除、修改辩论队员。

### 修改 `prompts/` 下的内容：

- 修改 `common.md` 编辑所有辩手（除裁判官）的公共提示词
- 修改 `init.md` 编辑辩论开始时的提示词
- 修改 `prepare.md` 编辑双方准备阶段的提示词
- 修改 `final.md` 编辑最终审判的提示词
- 修改 `agents/*.md` 编辑单个角色的提示词
- 修改 `topics/*.md` 编辑案件及介绍

有以下变量可供使用：

- `{stance}`：已方观点（默认为正方）
- `{affirmative_stance}`：正方观点
- `{negative_stance}`：反方观点
- `{affirmative_agents}`：正方辩手列表
- `{negative_agents}`：反方辩手列表
- `{witness_agents}`：证人列表
- `{debate_topic}`：辩论主题
- `{debate_topic_full}`：案件介绍全文
- `{max_words}`：每次发言长度
- `{max_rounds}`：最大发言轮次
- `{current_date}`：现在的时间

### 修改 `tools.py`:

增加、删除、修改 MCP 服务。

### 增加 `.env`:

如有必要（如 MCP 或 config 需要）

## LICENSE

MIT
