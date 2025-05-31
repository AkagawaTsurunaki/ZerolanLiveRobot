from pydantic import BaseModel, Field

from common.utils.i18n_util import i18n_config
from pipeline.db.milvus.milvus_sync import MilvusDatabaseConfig

_ = i18n_config()


#########
# VecDB #
#########

class VectorDBConfig(BaseModel):
    enable: bool = Field(default=True, description=_("Whether the Vector Database is enabled."))
    milvus: MilvusDatabaseConfig = Field(default=MilvusDatabaseConfig(),
                                         description=_("Configuration for the Milvus Database."))
