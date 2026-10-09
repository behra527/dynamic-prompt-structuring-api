
import json

import requests
import streamlit as st


st.set_page_config(
    page_title="Dynamic Prompt Structuring",
    page_icon="📝",
    layout="wide",
)

st.title("Dynamic Prompt Structuring")
st.caption(
    "Role-based structured clinical documentation "
    "with API integration and schema validation."
)

st.sidebar.header("API Configuration")

api_url = st.sidebar.text_input(
    "FastAPI base URL",
    value="http://127.0.0.1:8001",
    help="Make sure the FastAPI server is running on this address.",
).strip().rstrip("/")

if st.sidebar.button("Check API connection"):
    try:
        health_response = requests.get(
            f"{api_url}/health",
            timeout=5,
        )
        if health_response.ok:
            st.sidebar.success("FastAPI is connected.")
        else:
            st.sidebar.error(
                f"Health check failed: HTTP {health_response.status_code}"
            )
    except requests.RequestException:
        st.sidebar.error("Cannot connect to FastAPI.")


def lines(value: str) -> list[str]:
    """Convert multiline text into a clean list."""
    return [
        item.strip()
        for item in value.splitlines()
        if item.strip()
    ]


def display_list(title: str, items: list[str], empty_message: str) -> None:
    """Display a list without treating missing values as facts."""
    st.subheader(title)

    if items:
        for item in items:
            st.markdown(f"- {item}")
    else:
        st.info(empty_message)


with st.form("note_form"):
    st.subheader("Documentation settings")

    col1, col2, col3 = st.columns(3)

    with col1:
        role = st.selectbox(
            "User role",
            [
                "doctor",
                "nurse",
                "medical_scribe",
                "patient",
            ],
        )

    with col2:
        note_type = st.selectbox(
            "Note type",
            [
                "clinical_summary",
                "progress_note",
                "discharge_summary",
                "patient_instructions",
            ],
        )

    with col3:
        output_format = st.selectbox(
            "Output format",
            [
                "standard_json",
                "concise_json",
                "patient_friendly_json",
            ],
        )

    st.subheader("Patient information")

    age_input = st.number_input(
        "Patient age (leave at 0 if unknown)",
        min_value=0,
        max_value=120,
        value=0,
        step=1,
    )

    col1, col2 = st.columns(2)

    with col1:
        symptoms = st.text_area(
            "Symptoms (one per line)",
            placeholder="Fatigue\nHeadache",
        )

        history = st.text_area(
            "Relevant medical history (one per line)",
            placeholder="Enter known history, or leave blank if unknown.",
        )

        medications = st.text_area(
            "Medications (one per line)",
            placeholder="Enter reported medications.",
        )

    with col2:
        allergies = st.text_area(
            "Allergies (one per line)",
            placeholder="Enter reported allergies.",
        )

        st.caption(
            "Only enter information that has been supplied or verified. "
            "Leave unknown information blank."
        )

    instruction = st.text_area(
        "Task instruction",
        value="Summarize the supplied information.",
        help="Describe what the model should produce.",
    )

    submitted = st.form_submit_button(
        "Generate structured note",
        type="primary",
        use_container_width=True,
    )


if submitted:
    if not api_url:
        st.error("Enter the FastAPI URL in the sidebar.")
    elif not instruction.strip():
        st.error("Task instruction is required.")
    else:
        payload = {
            "user_role": role,
            "patient_context": {
                "age": age_input if age_input > 0 else None,
                "symptoms": lines(symptoms),
                "relevant_history": lines(history),
                "medications": lines(medications),
                "allergies": lines(allergies),
                "vitals": {},
            },
            "note_type": note_type,
            "output_format": output_format,
            "user_instruction": instruction.strip(),
        }

        try:
            with st.spinner(
                "Generating and validating the structured note..."
            ):
                response = requests.post(
                    f"{api_url}/generate-note",
                    json=payload,
                    timeout=120,
                )

            if response.ok:
                result = response.json()

                st.success("API request completed successfully.")

                st.subheader("Generated note")
                st.write(
                    result.get("summary")
                    or "The API returned no summary."
                )

                observations = result.get("key_observations") or []
                missing = result.get("missing_information") or []

                col1, col2 = st.columns(2)

                with col1:
                    display_list(
                        "Key observations",
                        observations,
                        "No observations were supplied.",
                    )

                with col2:
                    display_list(
                        "Missing information",
                        missing,
                        "No missing information was reported by the API.",
                    )

                disclaimer = result.get("disclaimer")
                if disclaimer:
                    st.warning(disclaimer)

                st.subheader("Structured JSON response")
                st.json(result)

                st.download_button(
                    label="Download JSON",
                    data=json.dumps(
                        result,
                        indent=2,
                        ensure_ascii=False,
                    ),
                    file_name="clinical_note.json",
                    mime="application/json",
                )

            else:
                st.error(
                    f"API returned HTTP {response.status_code}."
                )

                try:
                    error_data = response.json()
                    st.json(error_data)
                except ValueError:
                    st.code(response.text or "No error details returned.")

        except requests.Timeout:
            st.error(
                "The request timed out. Check the API server logs "
                "before retrying."
            )

        except requests.ConnectionError:
            st.error(
                "Could not connect to FastAPI. Confirm that the server "
                "is running and the URL uses the correct port."
            )

        except requests.RequestException as exc:
            st.error(f"Request failed: {exc}")

        except (ValueError, KeyError) as exc:
            st.error(
                "The API response could not be parsed as expected."
            )
            st.caption(str(exc))

