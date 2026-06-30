from importlib.metadata import entry_points

import pytest
from docling.datamodel.accelerator_options import AcceleratorOptions
from docling_core.types.doc import BoundingBox, CoordOrigin
from PIL import Image

from docling_ocr_mistral import MistralOcrModel, MistralOcrOptions
from docling_ocr_mistral.model import _MistralOcrResponse


def _make_model(*, enabled: bool = True) -> MistralOcrModel:
    return MistralOcrModel(
        enabled=enabled,
        artifacts_path=None,
        options=MistralOcrOptions(api_key="test-key", scale=2.0),
        accelerator_options=AcceleratorOptions(),
    )


def test_docling_entry_point_exposes_ocr_engine() -> None:
    matches = [
        entry_point
        for entry_point in entry_points(group="docling")
        if entry_point.name == "docling_ocr_mistral"
    ]

    assert len(matches) == 1
    plugin = matches[0].load()
    assert plugin.ocr_engines() == {"ocr_engines": [MistralOcrModel]}


def test_mistral_ocr_requires_api_key_when_enabled(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv("MISTRAL_API_KEY", raising=False)

    with pytest.raises(RuntimeError, match="requires an API key"):
        MistralOcrModel(
            enabled=True,
            artifacts_path=None,
            options=MistralOcrOptions(),
            accelerator_options=AcceleratorOptions(),
        )


def test_mistral_ocr_payload_requests_blocks_and_separate_images() -> None:
    model = _make_model()
    image = Image.new("RGB", (8, 6), "white")

    payload = model._request_payload(image)

    assert payload["model"] == "mistral-ocr-4-0"
    assert payload["include_blocks"] is True
    assert payload["include_image_base64"] is True
    assert payload["confidence_scores_granularity"] == "word"
    assert payload["table_format"] == "html"
    assert payload["document"]["type"] == "image_url"
    assert payload["document"]["image_url"].startswith("data:image/png;base64,")


def test_mistral_ocr_blocks_map_to_cells_and_skip_image_blocks() -> None:
    model = _make_model()
    response = _MistralOcrResponse.model_validate(
        {
            "pages": [
                {
                    "markdown": "Invoice 123\n\n![img-0.jpeg](img-0.jpeg)\n\nTotal $42",
                    "confidence_scores": {
                        "average_page_confidence_score": 0.7,
                        "word_confidence_scores": [
                            {"text": "Invoice", "confidence": 0.9, "start_index": 0},
                            {"text": " 123", "confidence": 0.8, "start_index": 7},
                            {"text": "Total", "confidence": 0.6, "start_index": 37},
                            {"text": " $42", "confidence": 0.5, "start_index": 42},
                        ],
                    },
                    "blocks": [
                        {
                            "type": "text",
                            "content": "Invoice 123",
                            "top_left_x": 20,
                            "top_left_y": 30,
                            "bottom_right_x": 220,
                            "bottom_right_y": 70,
                        },
                        {
                            "type": "image",
                            "content": "![img-0.jpeg](img-0.jpeg)",
                            "top_left_x": 30,
                            "top_left_y": 90,
                            "bottom_right_x": 180,
                            "bottom_right_y": 190,
                        },
                        {
                            "type": "text",
                            "content": "Total $42",
                            "top_left_x": 40,
                            "top_left_y": 220,
                            "bottom_right_x": 190,
                            "bottom_right_y": 260,
                        },
                    ],
                }
            ]
        }
    )
    ocr_rect = BoundingBox(
        l=10,
        t=100,
        r=410,
        b=500,
        coord_origin=CoordOrigin.TOPLEFT,
    )

    cells = model._response_to_cells(response, ocr_rect=ocr_rect, start_index=3)

    assert [cell.text for cell in cells] == ["Invoice 123", "Total $42"]
    assert [cell.index for cell in cells] == [3, 4]
    assert cells[0].confidence == pytest.approx(0.85)
    assert cells[0].rect.to_bounding_box().as_tuple() == pytest.approx(
        (20.0, 115.0, 120.0, 135.0)
    )
    assert cells[1].rect.to_bounding_box().as_tuple() == pytest.approx(
        (30.0, 210.0, 105.0, 230.0)
    )
