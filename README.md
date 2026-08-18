# AI Workflow Studio v3

## Luồng
Chủ đề → Storyboard → Prompt từng cảnh → Voice → Subtitle → Music → FFmpeg Render → MP4 9:16.

## Chạy Windows
1. Cài Python 3.11+.
2. Cài FFmpeg và thêm vào PATH.
3. Bấm `run.bat`.
4. Nhấn `GENERATE WORKFLOW`.

## Quan trọng
v3 là pipeline/engine nền. Các nhà cung cấp AI có API khác nhau; cần cấu hình API cụ thể trước khi tự động tạo file ảnh/video/voice thật.

## Output
- project.json
- subtitles.srt
- scenes/scene_XX.txt
- images/
- audio/
- video/
- final/
