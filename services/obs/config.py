from pydantic import BaseModel, Field

from common.utils.i18n_util import i18n_config

_ = i18n_config()


class ObsStudioClientConfig(BaseModel):
    enable: bool = Field(default=True,
                         description=_(
                             "Enable system connect to OBS studio to control the Text component for displaying subtitles?"))
    uri: str = Field(default="ws://127.0.0.1:4455",
                     description=_("URI for connection with target OBS studio WebSocket server. \n"
                                   "For example: ws://127.0.0.1:4455"))
    password: str = Field(default="<PASSWORD>",
                          description=_("Password for connection with target OBS studio Websocket server. \n"
                                        "Select Tool > WebSocket Server Setting > Show Connect Info, and you can find Server Password."))
    assistant_text_comp_name: str = Field(default="AssistantText",
                                          description=_(
                                              "The name of specific Text (GDI+) input component in the `Sources` panel. \n"
                                              "Display assistant output text."))
    #
    user_text_comp_name: str = Field(default="UserText",
                                     description=_(
                                         "The name of specific Text (GDI+) input component in the `Sources` panel. \n"
                                         "Display user input text."))
