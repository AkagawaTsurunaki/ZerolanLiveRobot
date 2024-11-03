from services.vid_cap.pipeline import VidCapQuery
from pipeline.vid_cap import VidCapPipeline

pipeline = VidCapPipeline()
q = VidCapQuery(
    vid_path=R"..\res\static\vid\vidcap-test.mp4")

p = pipeline.predict(query=q)
print(p.caption)
