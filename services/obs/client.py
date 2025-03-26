import json
import threading
import time
import uuid
from typing import Literal, Dict

import websockets
from loguru import logger
from retry import retry
from websockets import Subprotocol
from websockets.sync.client import connect, ClientConnection

from common.abs_runnable import ThreadRunnable
from common.utils.pws_util import do_challenge
from services.obs.config import ObsStudioClientConfig


class ObsStudioWsClient(ThreadRunnable):

    def __init__(self, config: ObsStudioClientConfig):
        """
        Reference:
            https://github.com/obsproject/obs-websocket/blob/master/docs/generated/protocol.md
        :param config: See ObsStudioClientConfig
        """
        super().__init__()
        assert config.uri is not None, "Please provide OBS studio Websocket server uri"
        self._uri: str = config.uri
        self._client: ClientConnection | None = None
        self._password: str = config.password
        self._text_comps: Dict[str, str] = {
            "assistant": config.assistant_text_comp_name,
            "user": config.user_text_comp_name,
        }

    @retry(exceptions=websockets.exceptions.ConnectionClosed, tries=-1, delay=2)
    def start(self):
        self._client = connect(uri=self._uri, subprotocols=[Subprotocol("obswebsocket.json"), ])
        try:
            logger.info("Connect to OBS Websocket server")
            while self._client.close_code is None:
                msg = self._client.recv()
                logger.debug(msg)
                try:
                    json_dict = json.loads(msg)
                    self._handle_json(json_dict)
                except Exception as e:
                    logger.exception(e)
                    continue
        except websockets.exceptions.ConnectionClosed as e:
            logger.warning("Connection closed.")
            raise e

    @property
    def is_connected(self) -> bool:
        if self._client is None:
            return False
        if self._client.close_code is not None:
            return False
        return True

    def _handle_json(self, json_dict: dict | list):
        if json_dict['op'] == 0:
            self._auth(json_dict)

    def _auth(self, json_dict: dict | list):
        """
        Suppose your OBS server has authentication validation.
        :param json_dict:
        :return:
        """
        challenge = json_dict['d']['authentication']['challenge']
        salt = json_dict['d']['authentication']['salt']
        my_auth = do_challenge(password=self._password, salt=salt, challenge=challenge)

        request = {
            "op": 1,
            "d": {
                "rpcVersion": 1,
                "authentication": my_auth,
                "eventSubscriptions": 33
            }
        }

        self._client.send(json.dumps(request))

    def _subtitle(self, text: str, which: str):
        # Discussion:
        #   https://github.com/obsproject/obs-websocket/discussions/1019
        request = {
            "op": 6,
            "d": {
                "requestType": "SetInputSettings",
                "requestId": str(uuid.uuid4()),
                "requestData": {
                    "inputName": which,
                    "inputSettings": {
                        "text": text  # Here edit your text!
                    }
                }
            }
        }
        self._client.send(json.dumps(request))

    def subtitle(self, text: str, which: Literal["user", "assistant"], duration: float = None):
        """
        Change specific Text (GDI+) input component text value.
        :param text: The text value you want to display.
        :param which: Which Text (GDI+) input component.
        :param duration: Default to None will display immediately.
                         Or it will display like a streaming subtitle in the duration.
        """
        if duration is None:
            self._subtitle(text, which)
            return

        if text is None or len(text) == 0:
            return

        def stream_subtitle():
            sec_per_char = duration / len(text)
            for i in range(len(text)):
                self._subtitle(text[0:i], self._text_comps[which])
                time.sleep(sec_per_char)

        threading.Thread(target=stream_subtitle).start()

    def name(self):
        return "ObsStudioWsClient"

    def stop(self):
        if self._client is not None:
            self._client.close()
