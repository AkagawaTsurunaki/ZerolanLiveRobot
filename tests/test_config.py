from common.config.model_config import ModelConfigLoader
from common.config.service_config import ServiceConfig

print(ServiceConfig.ocr_config)
print(ServiceConfig.asr_config)
print(ServiceConfig.llm_config)
print(ServiceConfig.imgcap_config)
print(ServiceConfig.controller_config)


print(ModelConfigLoader.speech_paraformer_model_config)
print(ModelConfigLoader.chatglm3_model_config)
print(ModelConfigLoader.qwen_model_config)
print(ModelConfigLoader.yi_model_config)
print(ModelConfigLoader.shisa_model_config)
print(ModelConfigLoader.blip_model_config)
print(ModelConfigLoader.paddle_ocr_model_config)
