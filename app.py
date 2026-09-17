import os
from google import genai
from google.genai import types
import streamlit as st

# Page Configuration
st.set_page_config(
    page_title="Artisan AI Studio Pro", page_icon="🎨", layout="wide"
)

# Colorful Professional Custom CSS (Neon Gradients & Glassmorphism)
st.markdown(
    """
    <style>
    .stApp {
        background: linear-gradient(135deg, #090d16 0%, #111827 100%);
        color: #f3f4f6;
    }
    .sidebar .stSidebar {
        background-color: #0f172a;
        border-right: 1px solid #1e293b;
    }
    div.stButton > button:first-child {
        background: linear-gradient(135deg, #ec4899 0%, #8b5cf6 50%, #3b82f6 100%);
        color: white;
        border: none;
        width: 100%;
        font-weight: bold;
        border-radius: 10px;
        padding: 0.7rem;
        box-shadow: 0 4px 15px rgba(236, 72, 153, 0.4);
        transition: all 0.3s ease;
    }
    div.stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(139, 92, 246, 0.6);
    }
    .metric-card {
        background: rgba(30, 41, 59, 0.7);
        border: 1px solid rgba(255, 255, 255, 0.1);
        padding: 15px;
        border-radius: 12px;
    }
    </style>
""",
    unsafe_allow_html=True,
)

# Initialize Gemini Client securely via Streamlit Secrets
api_key = st.secrets.get("GEMINI_API_KEY") or os.environ.get("GEMINI_API_KEY")

# Main Title Header with Neon Accent
st.markdown(
    "## ⚡ Artisan AI Studio <span style='font-size: 16px; background:"
    " linear-gradient(90deg, #ec4899, #8b5cf6); -webkit-background-clip:"
    " text; -webkit-text-fill-color: transparent;'>PRO 3.6</span>",
    unsafe_allow_html=True,
)
st.markdown("---")

# Layout: Sidebar Controls
with st.sidebar:
  st.markdown("### 🎛️ Prompt Engineering")
  prompt = st.text_area(
      "Master Prompt",
      value=(
          "Cyberpunk female warrior standing on a neon-lit skyscraper rooftop,"
          " dramatic rain, holographic displays, highly detailed, 8k"
          " resolution"
      ),
      height=100,
  )

  negative_prompt = st.text_area(
      "Negative Prompt",
      value="blurry, low quality, distorted, deformed, extra limbs",
      height=80,
  )

  st.markdown("### ⚙️ Studio Settings")
  aspect_ratio = st.selectbox(
      "Aspect Ratio", ["1:1 (Square)", "16:9 (Landscape)", "9:16 (Portrait)"]
  )
  style_preset = st.selectbox(
      "Style Preset",
      [
          "Cyberpunk Neon",
          "Cinematic Blockbuster",
          "Photorealistic Portrait",
          "Anime Fantasy",
          "Digital Masterpiece",
      ],
  )
  lighting_preset = st.selectbox(
      "Lighting Atmosphere",
      [
          "Volumetric Neon Glow",
          "Golden Hour Sunset",
          "Moody Cinematic Shadows",
          "Studio Softbox",
      ],
  )

  st.markdown("---")
  generate_btn = st.button("✨ Generate Masterpiece")

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
            "🎨 Gemini 3.6 Flash is crafting your visual masterpiece..."
        ):
          try:
            client = genai.Client(api_key=api_key)
            ratio_code = aspect_ratio.split(" ")[0]

            # Upgraded prompt injection including lighting and negative parameters
            full_prompt = (
                f"{prompt}, Style: {style_preset}, Lighting: {lighting_preset},"
                f" Aspect Ratio: {ratio_code}, professional ultra-high"
                f" definition rendering. Avoid: {negative_prompt}"
            )

            # Updated to use gemini-3.6-flash per current API availability
            response = client.models.generate_content(
                model="gemini-3.6-flash",
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
                          caption=f"Rendered with Gemini 3.6 ({ratio_code})",
                          use_container_width=True,
                      )

                      st.download_button(
                          label="📥 Download High-Res Image",
                          data=img_bytes,
                          file_name=f"artisan_ai_3.6_{ratio_code.replace(':', '-')}.jpg",
                          mime="image/jpeg",
                      )

                      image_found = True
                      if "history" not in st.session_state:
                        st.session_state.history = []
                      st.session_state.history.append(
                          (img_bytes, ratio_code, style_preset)
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
          "👉 Configure your studio settings in the sidebar and click"
          " **'Generate Masterpiece'** to start."
      )

with col2:
  st.markdown("#### 🚀 Studio Specs & Engine")
  st.markdown(
      """
    <div class="metric-card">
        <b style="color: #ec4899;">Model:</b> Gemini 3.6 Flash<br>
        <b style="color: #8b5cf6;">Pipeline:</b> Multimodal GenAI<br>
        <b style="color: #3b82f6;">Quality:</b> Ultra HD Pro
    </div>
    """,
      unsafe_allow_html=True,
  )

  st.markdown("#### 🕒 Session Gallery")
  if "history" in st.session_state and st.session_state.history:
    for idx, item in enumerate(reversed(st.session_state.history[-3:])):
      img_bytes, ratio, style = item
      st.image(img_bytes, width=150, caption=f"{style} ({ratio})")
      st.download_button(
          label=f"📥 Download #{idx+1}",
          data=img_bytes,
          file_name=f"artisan_gallery_{idx}.jpg",
          mime="image/jpeg",
          key=f"history_dl_{idx}",
      )
  else:
    st.text("No creations in session yet.")

# Footer
st.markdown("---")
st.markdown(
    "<p style='text-align: center; color: #94a3b8;'>Artisan AI Studio Pro"
    " — Powered by Gemini 3.6 Flash & Streamlit</p>",
    unsafe_allow_html=True,
)
