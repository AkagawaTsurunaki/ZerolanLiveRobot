from langchain_core.prompts import ChatPromptTemplate

from agent.adaptor import LangChainAdaptedLLM
from common.config import get_config


def question_answer(text: str, question: str):
    """
    Generate the answer from the given text.
    Args:
        text: The long text to read.
        question: The question text.

    Returns:

    """
    config = get_config()
    model = LangChainAdaptedLLM(config=config.pipeline.llm)

    system_template = "你现在是一个问答助手，请仔细阅读文章内容，基于你阅读的内容，充分、正确地回答用户提出的问题。"

    prompt_template = ChatPromptTemplate.from_messages(
        [("system", system_template), ("user", "{text} \n\n【你的任务】现在根据上述文段，回答问题：\n{question}")]
    )

    result = prompt_template.invoke({"text": text, "question": question})
    result.to_messages()
    response = model.invoke(result)

    return response
