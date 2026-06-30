from docling_ocr_mistral.model import MistralOcrModel


def ocr_engines() -> dict[str, list[type[MistralOcrModel]]]:
    return {"ocr_engines": [MistralOcrModel]}
