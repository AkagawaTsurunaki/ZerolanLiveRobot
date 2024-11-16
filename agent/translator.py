from langchain_core.prompts import ChatPromptTemplate

from agent.adaptor import LangChainAdaptedLLM
from common.config import get_config

config = get_config()
model = LangChainAdaptedLLM(config=config.pipeline.llm)

system_template = "Translate the following from {src_lang} into {tgt_lang}"

prompt_template = ChatPromptTemplate.from_messages(
    [("system", system_template), ("user", "{text}")]
)

result = prompt_template.invoke({"src_lang": "English", "tgt_lang": "Chinese", "text": "hi!"})
result.to_messages()
response = model.invoke(result)

print(result)
print(response)
