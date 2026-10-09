
from app.prompt_builder import build_system_prompt
from app.schemas import PromptRequest


def test_prompt_contains_dynamic_fields():
    request = PromptRequest(
        user_role="nurse",
        note_type="progress_note",
        output_format="concise_json",
        user_instruction="Summarize the supplied symptoms.",
    )

    prompt = build_system_prompt(request)

    assert "nurse" in prompt
    assert "progress_note" in prompt
    assert "concise_json" in prompt
    assert "Never invent" in prompt