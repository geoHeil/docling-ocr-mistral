# docling-ocr-mistral

Mistral OCR plugin for [Docling](https://github.com/docling-project/docling).

## Install

```bash
pip install docling-ocr-mistral
```

## Use

```python
from docling.datamodel.base_models import InputFormat
from docling.datamodel.pipeline_options import PdfPipelineOptions
from docling.document_converter import DocumentConverter, PdfFormatOption
from docling_ocr_mistral import MistralOcrOptions

pipeline_options = PdfPipelineOptions(
    allow_external_plugins=True,
    ocr_options=MistralOcrOptions(),
)

converter = DocumentConverter(
    format_options={
        InputFormat.PDF: PdfFormatOption(pipeline_options=pipeline_options),
    }
)
result = converter.convert("document.pdf")
```

Set `MISTRAL_API_KEY` or pass `MistralOcrOptions(api_key="...")`.

CLI:

```bash
docling --allow-external-plugins --ocr-engine mistral_ocr document.pdf
```
