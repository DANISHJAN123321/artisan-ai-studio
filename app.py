import os
from google import genai
import streamlit as st

# Page Configuration
st.set_page_config(
    page_title="Artisan AI Studio", page_icon="🎨", layout="wide"
)

# Custom CSS for a professional dark studio look
st.markdown(
    """
    <style>
    .stApp {
        background-color: #0e1117;
        color: #ffffff;
    }
    .sidebar .stSidebar {
        background-color: #161b22;
    }
    div.stButton > button:first-child {
        background: linear-gradient(90deg, #6366f1 0%, #a855f7 100%);
        color: white;
        border: none;
        width: 100%;
        font-weight: bold;
        border-radius: 8px;
        padding: 0.6rem;
    }
    div.stButton > button:hover {
        opacity: 0.9;
    }
    </style>
""",
    unsafe_allow_html=True,
)

# Initialize Gemini Client securely via Streamlit Secrets
# (You will add GEMINI_API_KEY in your Streamlit Cloud settings later)
api_key = st.secrets.get("GEMINI_API_KEY") or os.environ.get("GEMINI_API_KEY")

# Main Title Header
st.markdown(
    "## ⚡ Artisan AI Studio",
    help="Professional AI Image Generation Workspace",
)
st.markdown("---")

# Layout Layout: Sidebar for controls, Main area for canvas
with st.sidebar:
  st.markdown("### 🎛️ Prompt Engineering")
  prompt = st.text_area(
      "Master Prompt",
      value=(
          "Cinematic shot of a futuristic neon sports car racing through a"
          " cyberpunk city at night, highly detailed, 8k resolution, volumetric"
          " lighting"
      ),
      height=120,
  )

  st.markdown("### ⚙️ Image Settings")
  aspect_ratio = st.selectbox(
      "Aspect Ratio", ["1:1 (Square)", "16:9 (Landscape)", "9:16 (Portrait)"]
  )
  style_preset = st.selectbox(
      "Style Preset",
      ["Photorealistic", "Cinematic", "Cyberpunk", "Anime", "Digital Art"],
  )

  st.markdown("### 🎚️ Advanced Controls")
  guidance_scale = st.slider("Guidance Scale", 1.0, 20.0, 7.5)
  steps = st.slider("Sampling Steps", 10, 50, 30)

  st.markdown("---")
  generate_btn = st.button("✨ Generate Artwork")

# Main Workspace Canvas
col1, col2 = st.columns([2, 1])

with col1:
  st.markdown("#### 🖼️ Live Preview Canvas")
  canvas_container = st.container()

  with canvas_container:
    if generate_btn:
      if not api_key:
        st.error(
            "⚠️ Gemini API Key not found! Please add it to your Streamlit"
            " Secrets."
        )
      else:
        with st.spinner(
            "🎨 Artisan AI is rendering your masterpiece... Please wait."
        ):
          try:
            # Initialize the official Google GenAI client
            client = genai.Client(api_key=api_key)

            # Combine user prompt with style presets
            full_prompt = (
                f"{prompt}, Style: {style_preset}, highly detailed, professional"
                " digital rendering"
            )

            # Call Gemini / Imagen model for image generation
            # Note: Using gemini-2.5-flash or imagen model depending on your endpoint capability
            result = client.models.generate_images(
                model="imagen-3.0-generate-002",
                prompt=full_prompt,
                config=dict(
                    number_of_images=1,
                    output_mime_type="image/jpeg",
                    aspect_ratio=(
                        "16:9"
                        if "16:9" in aspect_ratio
                        else ("9:16" if "9:16" in aspect_ratio else "1:1")
                    ),
                ),
            )

            # Display generated image
            for generated_image in result.generated_images:
              st.image(
                  generated_image.image.image_bytes,
                  caption=f"Generated: {prompt[:40]}...",
                  use_container_width=True,
              )
              # Save to session state history
              if "history" not in st.session_state:
                st.session_state.history = []
              st.session_state.history.append(
                  generated_image.image.image_bytes
              )

          except Exception as e:
            st.error(
                f"An error occurred during generation: {e}. Make sure your"
                " API key supports image generation models."
            )
    else:
      st.info(
          "👉 Configure your settings in the sidebar and click **'Generate"
          " Artwork'** to start."
      )

with col2:
  st.markdown("#### 📁 Quick Info & Specs")
  st.markdown(
      """
    * **Engine:** Google Gemini & Imagen API
    * **Mode:** Studio Pro Workspace
    * **Resolution:** High-Definition Upscaled
    """
  )

  st.markdown("#### 🕒 Recent Session Gallery")
  if "history" in st.session_state and st.session_state.history:
    for idx, img_bytes in enumerate(
        reversed(st.session_state.history[-3:])
    ):  # Show last 3
      st.image(img_bytes, width=150)
  else:
    st.text("No history yet.")

# Footer
st.markdown("---")
st.markdown(
    "<p style='text-align: center; color: gray;'>Artisan AI Studio — Built"
    " with Streamlit & Google GenAI SDK</p>",
    unsafe_allow_html=True,
)
