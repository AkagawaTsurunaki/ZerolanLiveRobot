from services.img_cap.pipeline import ImaCapPipeline, ImgCapQuery

pipeline = ImaCapPipeline()

img_path = R"../resources/static/image/imgcap-test.png"

q = ImgCapQuery(img_path=img_path, prompt="there")

p = pipeline.predict(q)

print(p.caption)
