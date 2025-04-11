from pydantic import Field, BaseModel


class Gift(BaseModel):
    uid: str = Field(description="Sender ID.")
    username: str = Field(description="Sender username.")
    gift_name: str = Field(description="Gift name.")
    num: int = Field(description="Number of gifts.")
