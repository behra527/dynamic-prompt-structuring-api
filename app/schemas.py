
from enum import StrEnum
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field


ShortText = Annotated[str, Field(min_length=1, max_length=300)]
VitalKey = Annotated[str, Field(min_length=1, max_length=50)]
VitalTextValue = Annotated[str, Field(max_length=200)]
VitalValue = VitalTextValue | float | int


class UserRole(StrEnum):
    DOCTOR = "doctor"
    NURSE = "nurse"
    MEDICAL_SCRIBE = "medical_scribe"
    PATIENT = "patient"


class NoteType(StrEnum):
    CLINICAL_SUMMARY = "clinical_summary"
    PROGRESS_NOTE = "progress_note"
    DISCHARGE_SUMMARY = "discharge_summary"
    PATIENT_INSTRUCTIONS = "patient_instructions"


class OutputFormat(StrEnum):
    STANDARD_JSON = "standard_json"
    CONCISE_JSON = "concise_json"
    PATIENT_FRIENDLY_JSON = "patient_friendly_json"


class StrictModel(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        str_strip_whitespace=True,
    )


class PatientContext(StrictModel):
    age: int | None = Field(default=None, ge=0, le=120)

    symptoms: list[ShortText] = Field(
        default_factory=list,
        max_length=30,
    )
    relevant_history: list[ShortText] = Field(
        default_factory=list,
        max_length=30,
    )
    medications: list[ShortText] = Field(
        default_factory=list,
        max_length=30,
    )
    allergies: list[ShortText] = Field(
        default_factory=list,
        max_length=30,
    )
    vitals: dict[VitalKey, VitalValue] = Field(
        default_factory=dict,
        max_length=30,
    )


class PromptRequest(StrictModel):
    user_role: UserRole

    patient_context: PatientContext = Field(
        default_factory=PatientContext
    )

    note_type: NoteType

    output_format: OutputFormat = OutputFormat.STANDARD_JSON

    user_instruction: str = Field(
        min_length=1,
        max_length=2000,
    )


class ClinicalNoteResponse(StrictModel):
    note_type: NoteType
    output_format: OutputFormat

    summary: str = Field(
        min_length=1,
        max_length=5000,
    )

    key_observations: list[ShortText] = Field(max_length=30)
    missing_information: list[ShortText] = Field(max_length=30)

    disclaimer: str = Field(
        min_length=1,
        max_length=500,
    )