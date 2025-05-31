from pydantic import BaseModel, Field


class ResourceServerConfig(BaseModel):
    host: str = Field("0.0.0.0", description=_("The host address of the resource server"))
    port: int = Field(8899, description=_("The port number of the resource server"))