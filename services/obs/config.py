from pydantic import BaseModel


class ObsStudioClientConfig(BaseModel):
    enable: bool = True
    # URI for connection with target OBS studio WebSocket server. For example: ws://127.0.0.1:4455
    uri: str = "ws://127.0.0.1:4455"
    # Password for connection with target OBS studio Websocket server. Select Tool > WebSocket Server Setting > Show Connect Info, and you can find Server Password.
    password: str
    # The name of specific Text (GDI+) input component in the `Sources` panel. Display assistant output text.
    assistant_text_comp_name: str = "AssistantText"
    # The name of specific Text (GDI+) input component in the `Sources` panel. Display user input text.
    user_text_comp_name: str = "UserText"
