from autogen_core.tools import FunctionTool


class AgentMemory:
    def __init__(self) -> None:
        self.entries: list[str] = []
        self.read_func = FunctionTool(self.read, "读取备忘录中的所有条目")
        self.write_func = FunctionTool(self.write, "将内容追加写入备忘录")
        self.clear_func = FunctionTool(self.clear, "清空备忘录")
        self.tools = [self.read_func, self.write_func, self.clear_func]

    def read(self) -> str:
        if not self.entries:
            return "备忘录当前为空。"
        return "\n".join(f"- {entry}" for entry in reversed(self.entries))

    def write(self, content: str) -> str:
        self.entries.append(content)
        return "已成功记录到备忘录。"

    def clear(self) -> str:
        self.entries.clear()
        return "备忘录已清空。"
