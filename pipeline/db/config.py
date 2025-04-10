from pydantic import BaseModel, Field

from pipeline.db.milvus_sync import MilvusDatabaseConfig


#########
# VecDB #
#########

class VectorDBConfig(BaseModel):
    enable: bool = Field(default=True, description="Whether the Vector Database is enabled.")
    milvus: MilvusDatabaseConfig = Field(default=MilvusDatabaseConfig(),
                                         description="Configuration for the Milvus Database.")
