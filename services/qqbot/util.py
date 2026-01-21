import json

from ncatbot.core.api.api_group import EssenceMessage


def _essence_msg_to_dict(emsg: EssenceMessage):
    essence_message_dict = {
        "msg_seq": emsg.msg_seq,
        "msg_random": emsg.msg_random,
        "sender_id": emsg.sender_id,
        "sender_nick": emsg.sender_nick,
        "operator_id": emsg.operator_id,
        "operator_nick": emsg.operator_nick,
        "message_id": emsg.message_id,
        "operator_time": emsg.operator_time,
        "content": [
            msg.to_dict() for msg in emsg.content
        ]
    }
    return essence_message_dict


def _essence_msg_to_json(emsg: EssenceMessage):
    essence_message_dict = _essence_msg_to_dict(emsg)
    emsg_json_line = json.dumps(essence_message_dict, ensure_ascii=False)
    return emsg_json_line