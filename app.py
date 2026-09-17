import io
import os
from google import genai
from google.genai import types
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
api_key = st.secrets.get("GEMINI_API_KEY") or os.environ.get("GEMINI_API_KEY")

# Main Title Header
st.markdown("## ⚡ Artisan AI Studio")
st.markdown("---")

# Layout: Sidebar for controls, Main area for canvas
with st.sidebar:
  st.markdown("### 🎛️ Prompt Engineering")
  prompt = st.text_area(
      "Master Prompt",
      value=(
          "Cinematic shot of a futuristic neon sports car racing through a"
          " cyberpunk city at night, highly detailed, 8k resolution"
      ),
      height=100,
  )

  negative_prompt = st.text_area(
      "Negative Prompt",
      value="blurry, low quality, distorted, deformed, extra limbs, bad anatomy",
      height=80,
      help="Specify elements you want to exclude from the image.",
  )

  st.markdown("### ⚙️ Image Settings")
  aspect_ratio = st.selectbox(
      "Aspect Ratio", ["1:1 (Square)", "16:9 (Landscape)", "9:16 (Portrait)"]
  )
  style_preset = st.selectbox(
      "Style Preset",
      ["Photorealistic", "Cinematic", "Cyberpunk", "Anime", "Digital Art"],
  )

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
            client = genai.Client(api_key=api_key)

            # Map the selected aspect ratio option (e.g., "16:9 (Landscape)" -> "16:9")
            ratio_code = aspect_ratio.split(" ")[0]

            # Combine elements into a comprehensive prompt payload
            full_prompt = (
                f"{prompt}, Style: {style_preset}, Aspect Ratio: {ratio_code},"
                f" highly detailed, professional digital rendering. Avoid:"
                f" {negative_prompt}"
            )

            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=full_prompt,
                config=types.GenerateContentConfig(
                    response_modalities=["IMAGE", "TEXT"]
                ),
            )

            image_found = False
            if response.candidates:
              for candidate in response.candidates:
                if candidate.content and candidate.content.parts:
                  for part in candidate.content.parts:
                    if getattr(part, "inline_data", None) and part.inline_data:
                      img_bytes = part.inline_data.data
                      st.image(
                          img_bytes,
                          caption=(
                              f"Generated ({ratio_code}): {prompt[:30]}..."
                          ),
                          use_container_width=True,
                      )

                      st.download_button(
                          label="📥 Download Masterpiece",
                          data=img_bytes,
                          file_name=f"artisan_ai_{ratio_code.replace(':', '-')}.jpg",
                          mime="image/jpeg",
                      )

                      image_found = True
                      if "history" not in st.session_state:
                        st.session_state.history = []
                      st.session_state.history.append(
                          (img_bytes, ratio_code)
                      )

            if not image_found:
              if response.text:
                st.info(f"Model Output Response: {response.text}")
              else:
                st.warning(
                    "No image data returned from the model. Please adjust your"
                    " prompt."
                )

          except Exception as e:
            st.error(f"An error occurred during generation: {e}")
    else:
      st.info(
          "👉 Configure your settings in the sidebar and click **'Generate"
          " Artwork'** to start."
      )

with col2:
  st.markdown("#### 📁 Quick Info & Specs")
  st.markdown(
      """
    * **Engine:** Google GenAI Developer API
    * **Mode:** Studio Pro Workspace
    * **Resolution:** High-Definition
    """
  )

  st.markdown("#### 🕒 Recent Session Gallery")
  if "history" in st.session_state and st.session_state.history:
    for idx, item in enumerate(reversed(st.session_state.history[-3:])):
      img_bytes, ratio = item
      st.image(img_bytes, width=150, caption=f"Ratio: {ratio}")
      st.download_button(
          label=f"📥 Download ({ratio})",
          data=img_bytes,
          file_name=f"artwork_{idx}_{ratio.replace(':', '-')}.jpg",
          mime="image/jpeg",
          key=f"history_download_{idx}",
      )
  else:
    st.text("No history yet.")

# Footer
st.markdown("---")
st.markdown(
    "<p style='text-align: center; color: gray;'>Artisan AI Studio — Built"
    " with Streamlit & Google GenAI SDK</p>",
    unsafe_allow_html=True,
)
