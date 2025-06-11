call C:\ProgramData\Anaconda3\Scripts\activate.bat
call conda activate comfy
cd C:\deepl\gpu0_comfyui_py3127\comfyui_api
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
pause
