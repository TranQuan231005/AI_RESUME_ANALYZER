import json
from pathlib import Path

from app.main import app


ROOT = Path(__file__).resolve().parents[3]


def _multipart_properties(spec: dict, path: str) -> tuple[dict, list[str]]:
    schema = spec["paths"][path]["post"]["requestBody"]["content"][
        "multipart/form-data"
    ]["schema"]
    if "$ref" in schema:
        schema_name = schema["$ref"].rsplit("/", 1)[-1]
        schema = spec["components"]["schemas"][schema_name]
    return schema["properties"], schema.get("required", [])


def test_analyze_match_openapi_preserves_frozen_camel_case_form_fields():
    properties, required = _multipart_properties(app.openapi(), "/api/analyze-match")

    assert set(properties) == {"file", "jobDescription", "targetRole"}
    assert set(required) == {"file", "jobDescription"}
    assert properties["jobDescription"]["minLength"] == 50
    assert "job_description" not in properties
    assert "target_role" not in properties


def test_internal_and_public_openapi_use_the_same_frozen_match_field_names():
    internal_spec = json.loads(
        (ROOT / "contracts/openapi/ai-service.json").read_text(encoding="utf-8")
    )
    public_spec = json.loads(
        (ROOT / "contracts/openapi/public-api.json").read_text(encoding="utf-8")
    )

    internal_properties, internal_required = _multipart_properties(
        internal_spec,
        "/api/analyze-match",
    )
    public_properties, public_required = _multipart_properties(
        public_spec,
        "/api/analyses/match",
    )

    frozen_fields = {"file", "jobDescription", "targetRole"}
    assert set(internal_properties) == frozen_fields
    assert set(public_properties) == frozen_fields
    assert set(internal_required) == {"file", "jobDescription"}
    assert set(public_required) == {"file", "jobDescription"}
