from services.ocr.pipeline import OCRQuery, OcrPipeline

img_path = R"..\res\static\image\ocr-test-zh.png"

pipeline = OcrPipeline()
q = OCRQuery(img_path)
p = pipeline.predict(q)
print(p.unfold_as_str())
