from pydantic import BaseModel, Field


class ResourceServerConfig(BaseModel):
    host: str = Field("0.0.0.0", description="The host address of the resource server")
    port: int = Field(8899, description="The port number of the resource server")