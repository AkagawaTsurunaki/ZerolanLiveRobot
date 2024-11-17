from agent.baidu import MoeGirlTool
from agent.qa import question_answer
from services.browser.driver import DriverInitializer


def test_baike():
    # msg = search_baike("请搜素绫地宁宁")
    # question_awnser(msg.content, "在游戏中，绫地宁宁变为魔女，但是代价是什么？")
    # print(get_html("https://mzh.moegirl.org.cn/%E7%BB%AB%E5%9C%B0%E5%AE%81%E5%AE%81"))
    driver = DriverInitializer().get_driver()
    p = MoeGirlTool(driver).invoke("绫地宁宁")
    print(p)
    p = question_answer(p, "0721是什么意思？")
    print(p)
