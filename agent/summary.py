from langchain_core.prompts import ChatPromptTemplate

from agent.adaptor import LangChainAdaptedLLM
from common.config import get_config


def summary(text: str, question: str):
    config = get_config()
    model = LangChainAdaptedLLM(config=config.pipeline.llm)

    system_template = "在给出文段中查找信息，回答用户提出的问题。"

    prompt_template = ChatPromptTemplate.from_messages(
        [("system", system_template), ("user", "{text} 根据上述文段，回答问题：\n{question}")]
    )

    result = prompt_template.invoke({"text": text, "question": question})
    result.to_messages()
    response = model.invoke(result)

    print(result)
    print(response)
