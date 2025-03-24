from pydantic import BaseModel, Field


class BilibiliServiceConfig(BaseModel):
    class Credential(BaseModel):
        sessdata: str = Field(default="<SESSDATA>", description="Value of the `SESSDATA` from the cookie.")
        bili_jct: str = Field(default="<bili_jct>", description="Value of the `bili_jct` from the cookie.")
        buvid3: str = Field(default="<buvid3>", description="Value of the `buvid3` from the cookie.")

    room_id: int = Field(default=-1,
                         description="Bilibili Room ID. \n"
                                     "Note: Must be a positive integer.")
    credential: Credential = Field(default=Credential(),
                                   description="Your Bilibili Credential. \n"
                                               "How to get: [See here](https://nemo2011.github.io/bilibili-api/#/get-credential)")


class TwitchServiceConfig(BaseModel):
    channel_id: str = Field(default="<CHANNEL_ID>",
                            description="Your Twitch channel ID.")
    app_id: str = Field(default="<APP_ID>",
                        description="Your Twitch app ID.")
    app_secret: str | None = Field(default=None,
                                   description="Your Twitch app secret. \n"
                                               "Leave it as `null` if you only want to use User Authentication.")


class YoutubeServiceConfig(BaseModel):
    token: str = Field(default="<YOUTUBE_TOKEN>",
                       description="GCloud auth print access token.")


class LiveStreamConfig(BaseModel):
    enable: bool = Field(default=True,
                         description="Enable live stream listening.")
    bilibili: BilibiliServiceConfig = Field(default=BilibiliServiceConfig(),
                                            description="Config for connecting to Bilibili live-streaming server")
    twitch: TwitchServiceConfig = Field(default=TwitchServiceConfig(),
                                        description="Config for connecting to Twitch live-streaming server")
    youtube: YoutubeServiceConfig = Field(default=TwitchServiceConfig(),
                                          description="Config for connecting to YouTube live-streaming server")
