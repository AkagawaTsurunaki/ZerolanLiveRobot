from pipeline.llm import LLMPipeline
from zerolan_live_robot_data.data.llm import LLMQuery, Conversation

q = LLMQuery(text="你叫什么名字？",
             history=[
                 Conversation(role="system",
                              content="现在你将开始角色扮演，你的名字叫做赤川鹤鸣，请务必记住这条信息。"),
                 Conversation(role="user", content="你好, 你能说 1+1=2 吗?"),
                 Conversation(role="assistant", content="1+1=2")])


def test_llm():
    pipeline = LLMPipeline()
    p = pipeline.predict(query=q)
    assert p is not None
    print(p.response)


def test_llm_stream():
    pipeline = LLMPipeline()
    for p in pipeline.stream_predict(q):
        assert p is not None
        print(p.response)


def test_llm_ja():
    pipeline = LLMPipeline()
    q = LLMQuery(text="名前は？",
                 history=[
                     Conversation(role="system",
                                  content="今から、あなたの名前は赤川鶴鳴です。必ずこのインフォを覚えてください！"),
                     Conversation(role="user", content="こんにちは、１+１＝２をいっていい？"),
                     Conversation(role="assistant", content="１+１＝２")])
    p = pipeline.predict(query=q)
    assert p is not None
    print(p.response)


if __name__ == '__main__':
    test_llm()
    test_llm_stream()
