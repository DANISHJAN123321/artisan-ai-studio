import os
from google import genai
from google.genai import types
import streamlit as st

# ==========================================
# Configuration & Setup
# ==========================================
st.set_page_config(
    page_title="Artisan AI Prompt Studio", page_icon="✍️", layout="wide"
)

# Define the standard text model used for free tier access
# Note: gemini-2.5-flash is used for high-speed, free tier operations.
FASTER_MODEL = "gemini-2.5-flash"

# Custom Professional Styling
st.markdown(
    """
    <style>
    .stApp { background-color: #0e1117; color: #ffffff; }
    .sidebar .stSidebar { background-color: #161b22; }
    div.stButton > button:first-child {
        background: linear-gradient(90deg, #6366f1 0%, #a855f7 100%);
        color: white; border: none; border-radius: 8px; font-weight: bold;
    }
    .stTextArea textarea { color: #e0e7ff; background-color: #1e293b; }
    .history-box {
        padding: 10px; border-radius: 5px; background-color: #1e293b;
        margin-bottom: 10px; border: 1px solid #334155;
    }
    </style>
""",
    unsafe_allow_html=True,
)

# Initialize Gemini Client
api_key = st.secrets.get("GEMINI_API_KEY") or os.environ.get("GEMINI_API_KEY")

# Session State Management
if "creative_output" not in st.session_state:
  st.session_state.creative_output = ""
if "prompt_history" not in st.session_state:
  st.session_state.prompt_history = []

# ==========================================
# Helper Functions
# ==========================================


def call_gemini_api(prompt, system_instruction):
  """Handles the API call to Gemini using the standard text model."""
  if not api_key:
    st.error("Gemini API Key not found. Please configure Streamlit Secrets.")
    return None
  try:
    client = genai.Client(api_key=api_key)
    response = client.models.generate_content(
        model=FASTER_MODEL,
        contents=prompt,
        config=types.GenerateContentConfig(
            system_instruction=system_instruction,
            temperature=0.7,  # Creative but controlled
            max_output_tokens=1000,
        ),
    )
    return response.text.strip()
  except Exception as e:
    st.error(f"API Error: {e}")
    return None


def add_to_history(tool_name, input_text, output_text):
  """Saves interaction to session state history."""
  st.session_state.prompt_history.append(
      {
          "tool": tool_name,
          "input": input_text[:50] + "...",
          "output": output_text,
      }
  )


# ==========================================
# Main UI Layout
# ==========================================
st.title("✍️ Artisan AI Prompt & Copywriting Studio")
st.markdown(
    "Professional copywriting tools powered by Gemini Standard Text Models."
)
st.markdown("---")

# Layout: 3 Columns
col1, col2, col3 = st.columns([1, 1.5, 1])

# --- Column 1: Toolkit Menu ---
with col1:
  st.subheader("🧰 Toolkit")
  selected_tool = st.radio(
      "Choose your craft:",
      [
          "AI Image Prompt Crafter",
          "Marketing Copywriter",
          "Blog Post Outline",
          "Email Subject Line Generator",
      ],
  )

  st.markdown("---")
  input_text = st.text_area(
      "Enter your core concept or topic:",
      placeholder="E.g., A futuristic city at sunset...",
      height=150,
  )

  generate_btn = st.button("✨ Craft Content")

# --- Column 2: Workspace Canvas ---
with col2:
  st.subheader("📄 Workspace")

  if generate_btn and input_text:
    with st.spinner(f"Artisan AI is crafting your {selected_tool}..."):
      result = None
      # Route to specific model instructions based on selected tool
      if selected_tool == "AI Image Prompt Crafter":
        system_instruction = (
            "Act as an expert AI image prompt engineer. Take the core concept"
            " and expand it into a highly detailed, descriptive prompt suitable"
            " for high-end AI image generators (like Midjourney or Imagen)."
            " Focus on lighting, composition, art style, and resolution. Return"
            " ONLY the prompt text."
        )
        result = call_gemini_api(input_text, system_instruction)

      elif selected_tool == "Marketing Copywriter":
        system_instruction = (
            "Act as a professional direct-response copywriter. Write persuasive"
            " marketing copy (AIDA framework) for the provided concept. Highlight"
            " benefits and include a call to action."
        )
        result = call_gemini_api(input_text, system_instruction)

      elif selected_tool == "Blog Post Outline":
        system_instruction = (
            "Act as a content strategist. Create a structured, detailed blog"
            " post outline based on the provided topic, including catchy H2/H3"
            " headers and key points for each section."
        )
        result = call_gemini_api(input_text, system_instruction)

      elif selected_tool == "Email Subject Line Generator":
        system_instruction = (
            "Act as an email marketing specialist. Generate 5 highly engaging,"
            " high-open-rate email subject lines for the provided topic."
        )
        result = call_gemini_api(input_text, system_instruction)

      if result:
        st.session_state.creative_output = result
        add_to_history(selected_tool, input_text, result)

  # Display the editable output area
  st.text_area(
      "Generated Content:",
      value=st.session_state.creative_output,
      height=400,
      key="output_display",
  )

  # Provide download and clear buttons
  if st.session_state.creative_output:
    st.download_button(
        label="💾 Download Result",
        data=st.session_state.creative_output,
        file_name="artisan_ai_output.txt",
        mime="text/plain",
    )
  if st.button("🗑️ Clear Workspace"):
    st.session_state.creative_output = ""
    st.rerun()

# --- Column 3: History Log ---
with col3:
  st.subheader("🕒 History Log")
  if not st.session_state.prompt_history:
    st.info("Your recent generations will appear here.")
  else:
    # Display history in reverse chronological order
    for i, item in enumerate(reversed(st.session_state.prompt_history)):
      with st.expander(f"{item['tool']} — {item['input']}"):
        st.markdown(f"**Output:** {item['output']}")
        # Add a button to restore this history item to the workspace
        if st.button("📤 Load to Workspace", key=f"load_hist_{i}"):
          st.session_state.creative_output = item["output"]
          st.rerun()

# Footer
st.markdown("---")
st.markdown(
    "<p style='text-align: center; color: gray;'>Artisan AI Studio — Built"
    " with Gemini Nano (Free Tier) & Streamlit</p>",
    unsafe_allow_html=True,
)
