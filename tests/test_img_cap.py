from zerolan_live_robot_data.data.img_cap import ImgCapQuery
from pipeline.img_cap import ImaCapPipeline

pipeline = ImaCapPipeline()

img_path = R"../resources/static/image/imgcap-test.png"

q = ImgCapQuery(img_path=img_path, prompt="there")

p = pipeline.predict(q)

print(p.caption)
