from dataclasses import dataclass


@dataclass
class ICIOPrompt:
    """
    Instruction（必须）：指令：即您希望模型执行的具体任务。

    Context（选填）：背景信息：或称为上下文信息，这有助于引导模型做出更精准的反应。

    Input Data（选填）：输入数据：告知模型需要处理的具体数据。

    Output Indicator（选填）：输出指示器：指明我们期望模型输出的类型或格式。
    """
    instruction: str | None = None
    context: str | None = None
    input_data: str | None = None
    output_indicator: str | None = None

    def en_format(self):
        result = ""
        result += f"Instruction: {self.instruction}\n" if self.instruction is not None else ""
        result += f"Context: {self.context}\n" if self.context is not None else ""
        result += f"Input: {self.input_data}\n" if self.input_data is not None else ""
        result += f"Indicator: {self.output_indicator}" if self.output_indicator is not None else ""
        return result
