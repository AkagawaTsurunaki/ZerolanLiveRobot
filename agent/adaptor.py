from typing import Optional, Any, Mapping

from langchain_core.callbacks import CallbackManagerForLLMRun
from langchain_core.language_models import LLM
from zerolan.data.data.llm import LLMQuery

from common.config import LLMPipelineConfig
from pipeline.llm import LLMPipeline


class LangChainAdaptedLLM(LLM):
    """
    https://python.langchain.com/docs/how_to/custom_llm/
    """
    def __init__(self, config: LLMPipelineConfig):
        super().__init__()
        self._pipeline = LLMPipeline(config=config)
        self._model_name = "CustomLLM"

    @property
    def _llm_type(self) -> str:
        return "custom"

    def _call(
        self,
        prompt: str,
        stop: Optional[list[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> str:
        if stop is not None:
            raise ValueError("stop kwargs are not permitted.")
        prediction = self._pipeline.predict(LLMQuery(
            text=prompt,
            history=[]
        ))
        return prediction.response

    # async def _acall(
    #     self,
    #     prompt: str,
    #     stop: Optional[list[str]] = None,
    #     run_manager: Optional[AsyncCallbackManagerForLLMRun] = None,
    #     **kwargs: Any,
    # ) -> str:
    #     if stop is not None:
    #         raise ValueError("stop kwargs are not permitted.")
    #     for prediction in self._pipeline.stream_predict(LLMQuery()):
    #         yield prediction.response

    @property
    def _identifying_params(self) -> Mapping[str, Any]:
        """Get the identifying parameters."""
        return {"model_name": self._model_name}
