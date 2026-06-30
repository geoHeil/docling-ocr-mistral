from typing import ClassVar, Literal

from pydantic import ConfigDict, Field, SecretStr

from docling.datamodel.pipeline_options import OcrOptions


class MistralOcrOptions(OcrOptions):
    """Configuration for Mistral OCR API."""

    kind: ClassVar[Literal["mistral_ocr"]] = "mistral_ocr"
    lang: list[str] = []
    model: str = Field(default="mistral-ocr-4-0", description="Mistral OCR model identifier.")
    api_key: SecretStr | None = Field(
        default=None,
        description="Mistral API key. If omitted, api_key_env_var is read.",
        exclude=True,
        repr=False,
    )
    api_key_env_var: str = Field(
        default="MISTRAL_API_KEY",
        description="Environment variable used to read the Mistral API key.",
    )
    url: str = Field(
        default="https://api.mistral.ai/v1/ocr",
        description="Mistral OCR endpoint URL.",
    )
    scale: float = Field(
        default=2.0,
        description="Image scale multiplier for OCR processing.",
        gt=0.0,
    )
    timeout: float = Field(default=120.0, description="HTTP request timeout in seconds.", gt=0.0)
    table_format: Literal["html", "markdown"] = Field(
        default="html",
        description="Table format requested from Mistral OCR.",
    )
    confidence_scores_granularity: Literal["page", "word"] = Field(
        default="word",
        description="Confidence score granularity requested from Mistral OCR.",
    )
    include_image_base64: bool = Field(
        default=True,
        description="Request extracted image payloads separately from markdown text.",
    )
    image_limit: int | None = Field(
        default=None,
        description="Maximum number of images Mistral OCR should extract per page.",
        ge=0,
    )
    image_min_size: int | None = Field(
        default=None,
        description="Minimum image size in pixels for Mistral OCR extraction.",
        ge=0,
    )
    model_config = ConfigDict(extra="forbid")
