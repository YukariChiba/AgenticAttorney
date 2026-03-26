# Director 剧本生成

将辩论日志转换为 objection.lol 可播放剧本。

## 工作流程

1. 读取辩论日志 (`logs/*.json`)
2. 提取参与角色，获取角色资源（姿势、气泡等）
3. 逐条处理日志，生成导演帧
4. 验证帧格式，重试机制确保输出质量
5. 输出 objection.lol 兼容的剧本文件

## 资源管理

从 objection.lol API 获取：

- **角色**: ID、名称、立场、姿势、对话气泡
- **音乐**: ID、名称
- **音效**: ID、名称

缓存位置: `cache/objection_api/`

## 配置说明

### `director` 剧本生成设置

- `model`: LLM 配置（建议 temperature 较高以增加创意）
- `buffer_size`: 上下文缓冲区大小
- `max_retries`: 验证失败时的最大重试次数
- `cache_duration`: API 资源缓存时间（秒）
