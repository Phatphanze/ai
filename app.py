import os, json, re, shutil, subprocess
from pathlib import Path
import streamlit as st

BASE = Path(__file__).parent
OUT = BASE / "output"
for d in ["scenes", "audio", "images", "video", "final"]:
    (OUT/d).mkdir(parents=True, exist_ok=True)

st.set_page_config(page_title="AI Workflow Studio v3", page_icon="🎬", layout="wide")
st.title("🎬 AI WORKFLOW STUDIO v3")
st.caption("One-click video pipeline — storyboard → prompts → voice → subtitles → render")

topic = st.text_input("🎯 Chủ đề", "Một người thành công đánh mất người thầy của mình")
col1, col2, col3 = st.columns(3)
with col1:
    duration = st.slider("⏱️ Thời lượng (giây)", 20, 180, 60)
with col2:
    scenes_count = st.slider("🎞️ Số cảnh", 4, 12, 6)
with col3:
    style = st.selectbox("🎨 Phong cách", ["Cinematic", "Realistic", "Anime", "Documentary", "Luxury"])

language = st.selectbox("🌐 Ngôn ngữ", ["Tiếng Việt", "English"])

def build_project(topic, duration, scenes_count, style, language):
    hook = "Bạn có bao giờ nhận ra thành công đôi khi khiến chúng ta quên mất người quan trọng nhất?"
    scenes = []
    beats = [
        ("Hook", "Nhân vật chính đứng một mình giữa thành phố, nhìn lại hành trình đã qua."),
        ("Khởi đầu", "Hồi tưởng thời điểm người thầy xuất hiện và trao cho anh niềm tin."),
        ("Thành công", "Nhân vật trở nên giàu có, nổi tiếng và ngày càng bận rộn."),
        ("Mất mát", "Anh bỏ lỡ một cuộc gọi quan trọng từ người thầy."),
        ("Nhận ra", "Anh trở về nơi cũ và nhận ra người thầy đã không còn ở đó."),
        ("Thông điệp", "Anh hiểu rằng thành công không có ý nghĩa nếu đánh mất người đã giúp mình bắt đầu.")
    ]
    beats = beats[:scenes_count] if scenes_count <= 6 else beats + [
        ("Thay đổi", "Nhân vật quyết định sống chậm lại và trân trọng những người bên cạnh."),
        ("Kết", "Anh gọi cho gia đình và những người quan trọng, bắt đầu lại bằng lòng biết ơn."),
        ("CTA", "Màn hình kết thúc với thông điệp: Hãy trân trọng khi vẫn còn cơ hội.")
    ][:scenes_count-6]
    sec = max(3, duration // len(beats))
    for i, (title, visual) in enumerate(beats, 1):
        scenes.append({
            "id": i,
            "title": title,
            "duration": sec,
            "narration": visual + " " + ("Đừng đợi đến khi quá muộn mới biết trân trọng." if i == len(beats) else ""),
            "image_prompt": f"{style}, vertical 9:16, cinematic storytelling, emotional lighting, realistic composition, {visual}",
            "video_prompt": f"{style}, vertical 9:16, slow cinematic camera movement, emotional acting, {visual}"
        })
    return {"topic": topic, "duration": duration, "language": language, "style": style, "hook": hook, "scenes": scenes}

def write_srt(project):
    lines = []
    t = 0
    for s in project["scenes"]:
        start = t
        end = t + s["duration"]
        def fmt(x):
            h=int(x//3600); m=int((x%3600)//60); sec=int(x%60); ms=int((x-int(x))*1000)
            return f"{h:02}:{m:02}:{sec:02},{ms:03}"
        lines.append(f'{s["id"]}\n{fmt(start)} --> {fmt(end)}\n{s["narration"]}\n')
        t = end
    return "\n".join(lines)

def save_project(project):
    (OUT/"project.json").write_text(json.dumps(project, ensure_ascii=False, indent=2), encoding="utf-8")
    (OUT/"subtitles.srt").write_text(write_srt(project), encoding="utf-8")
    for s in project["scenes"]:
        p = OUT/"scenes"/f"scene_{s['id']:02}.txt"
        p.write_text(
            f"SCENE {s['id']}: {s['title']}\n\n"
            f"NARRATION:\n{s['narration']}\n\n"
            f"IMAGE PROMPT:\n{s['image_prompt']}\n\n"
            f"VIDEO PROMPT:\n{s['video_prompt']}\n",
            encoding="utf-8"
        )

st.header("1️⃣ Tạo Storyboard")
if st.button("🚀 GENERATE WORKFLOW", type="primary"):
    project = build_project(topic, duration, scenes_count, style, language)
    st.session_state.project = project
    save_project(project)
    st.success("Đã tạo storyboard + prompt + subtitle!")

if "project" in st.session_state:
    p = st.session_state.project
    st.subheader("📋 Storyboard")
    for s in p["scenes"]:
        with st.expander(f"Cảnh {s['id']} — {s['title']} ({s['duration']}s)"):
            st.write("**Narration:**", s["narration"])
            st.write("**Image prompt:**", s["image_prompt"])
            st.write("**Video prompt:**", s["video_prompt"])

st.header("2️⃣ Production Pipeline")
steps = [
    ("🧠 AI Script", "Kịch bản & storyboard đã tạo"),
    ("🖼️ Image Generator", "Tạo ảnh từng cảnh bằng API"),
    ("🎥 Video Generator", "Tạo chuyển động từ ảnh/prompt"),
    ("🔊 Text-to-Speech", "Tạo voice từng cảnh"),
    ("💬 Subtitles", "SRT đã tạo tự động"),
    ("🎵 Music", "Đặt nhạc nền trong output/audio"),
    ("✂️ FFmpeg Render", "Ghép cảnh + voice + subtitle → MP4")
]
for name, desc in steps:
    st.write(f"**{name}** — {desc}")

if st.button("🛠️ Kiểm tra môi trường"):
    checks = {
        "Python": shutil.which("python"),
        "FFmpeg": shutil.which("ffmpeg"),
    }
    for k,v in checks.items():
        st.write(f"{'✅' if v else '❌'} {k}: {v or 'chưa cài'}")

st.header("3️⃣ Render MP4")
st.info("Khi đã có scene video/audio trong output, FFmpeg sẽ được dùng để render. API tạo ảnh/video/voice cần được cấu hình ở bước tích hợp.")
if st.button("🎬 RENDER (kiểm tra)"):
    if not shutil.which("ffmpeg"):
        st.error("Chưa có FFmpeg.")
    else:
        st.success("FFmpeg sẵn sàng. Pipeline render có thể được nối vào các file scene.")

st.header("4️⃣ Xuất project")
if st.button("📦 Đóng gói"):
    archive = shutil.make_archive(str(BASE/"AI_Workflow_Project_v3"), "zip", OUT)
    st.success(f"Đã tạo {archive}")

st.sidebar.header("🔑 API")
for key in ["OPENAI_API_KEY","GEMINI_API_KEY","ELEVENLABS_API_KEY"]:
    st.sidebar.write(key, "✓" if os.getenv(key) else "—")
    import time
from google import genai
def get_gemini_client():
    api_key = st.secrets.get("GEMINI_API_KEY")

    if not api_key:
        raise RuntimeError(
            "Chưa cấu hình GEMINI_API_KEY trong Streamlit Secrets."
        )

    return genai.Client(api_key=api_key)
    def generate_video(prompt, filename):
    client = get_gemini_client()

    operation = client.models.generate_videos(
        model="veo-3.1-generate-preview",
        prompt=prompt,
    )

    progress = st.progress(0)
    status = st.empty()

    while not operation.done:
        status.info("🎬 AI đang tạo video...")
        progress.progress(20)
        time.sleep(10)
        operation = client.operations.get(operation)

    progress.progress(100)

    video = operation.response.generated_videos[0]

    output_file = OUT / "video" / filename

    client.files.download(
        file=video.video,
        download_path=str(output_file)
    )

    status.success("✅ Đã tạo video!")
    return output_file
st.sidebar.markdown("---")
st.sidebar.write("Output:", str(OUT))
