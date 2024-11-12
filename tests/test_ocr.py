from services.ocr.pipeline import OCRQuery
from pipeline.ocr import OCRPipeline

img_path = R"..\res\static\image\ocr-test-zh.png"

pipeline = OCRPipeline()
q = OCRQuery(img_path)
p = pipeline.predict(q)
print(p.unfold_as_str())
