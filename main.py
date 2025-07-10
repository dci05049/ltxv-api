from fastapi import FastAPI, Query
from fastapi import File, UploadFile, Form
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from PIL import Image
from io import BytesIO
import base64
import io
import comfyuiservice
from pydantic import BaseModel

app = FastAPI()
# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins; restrict to specific domains as needed
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

async def convert_transparent_to_white(img):
    white_background = Image.new("RGB", img.size, (255, 255, 255))
    white_background.paste(img, mask=img.split()[3])

    return white_background

async def convert_image_to_base64(image_file):
    """
    Converts an uploaded image file to a Base64 string.
    """
    # Open the image from the uploaded file
    img = Image.open(BytesIO(await image_file.read()))

    # Save the image to a BytesIO object in the desired format
    img_byte_arr = BytesIO()
    img.save(img_byte_arr, format="PNG")
    img_byte_arr.seek(0)  # Reset stream pointer to the beginning

    # Encode the BytesIO content to Base64
    base64_encoded_image = base64.b64encode(img_byte_arr.getvalue()).decode("utf-8")
    return base64_encoded_image

async def save_base64_to_file(base64_data, filename):
    """
    Save a Base64 string to a text file.
    """
    with open(filename, "w") as file:
        file.write(base64_data)

@app.get("/image-prompt/")
async def get_image_with_prompt(
    input: str = Query(None)
):
    """
    Endpoint to process three images and return modified images as raw data.
    """
    # Load images into memory
    image = comfyuiservice.fetch_image_from_comfy(input)
    image_stream = io.BytesIO(image)
    return StreamingResponse(image_stream, media_type="image/png")


@app.post("/swap-cloth-model/")
async def swap_cloth_on_model(
    mask_image: UploadFile = File(..., description="Mask image (JPG or PNG)"),
    cloth_image: UploadFile = File(..., description="Cloth image (JPG or PNG)"),
    model_image: UploadFile = File(..., description="Model person image (JPG or PNG)"),
):
    """
    Endpoint to process three images and return modified images as raw data.
    """
    # Load images into memory
    mask_image_base64 = await convert_image_to_base64(mask_image)
    cloth_image_base64 = await convert_image_to_base64(cloth_image)
    model_image_base64 = await convert_image_to_base64(model_image)

    result_image = comfyuiservice.get_model_image_with_cloth(cloth_base_64=cloth_image_base64, model_base_64=model_image_base64, mask_base_64=mask_image_base64)
    image_stream = io.BytesIO(result_image)
    return StreamingResponse(image_stream, media_type="image/png")

"""
@app.post("/target-logo")
async def get_target_image_with_logo(
    mask_image: UploadFile = File(..., description="Mask image (JPG or PNG)"),
    logo_image: UploadFile = File(..., description="Logo image (JPG or PNG)"),
    target_image: UploadFile = File(..., description="Target output image (JPG or PNG)"),
):

    #Endpoint to process three images and return modified images as raw data.

    # Load images into memory
    mask_image_base64 = await convert_image_to_base64(mask_image)
    target_image_base64 = await convert_image_to_base64(target_image)
    logo_image_base64 = await convert_image_to_base64(logo_image)

    result_image = comfyuiservice.get_target_image_with_logo(target_image_base64=target_image_base64, logo_image_base64=logo_image_base64, mask_image_base64=mask_image_base64)
    image_stream = io.BytesIO(result_image)
    return StreamingResponse(image_stream, media_type="image/png")
"""

# 요청 모델 정의
class ImageRequest(BaseModel):
    image_data: str     # Base64로 인코딩된 이미지 데이터
    mask_data: str      # Base64로 인코딩된 마스크 이미지 데이터
    logo_data: str      # Base64로 인코딩된 로고 이미지 데이터

@app.post("/target-logo/")
async def target_logo(data: ImageRequest):
    # Load images into memory
    #mask_base64 = await convert_image_to_base64(mask_image)
    #logo_base64 = await convert_image_to_base64(logo_image)
    #cloth_base64 = await convert_image_to_base64(clothing_image)
    cloth = Image.open(BytesIO(base64.b64decode(data.image_data)))
    #cloth.save("cloth.png")

    logo = Image.open(BytesIO(base64.b64decode(data.logo_data)))
    if logo.mode == 'RGBA':
        logo = await convert_transparent_to_white(logo)
        #logo.save("logo.png")

    mask = Image.open(BytesIO(base64.b64decode(data.mask_data))).convert("RGB")
    #mask.save("mask.png")

    result_image = comfyuiservice.get_target_image_with_logo(target_image_base64=data.image_data, logo_image_base64=data.logo_data, mask_image_base64=data.mask_data)
    result_image = "data:image/png;base64," + base64.b64encode(result_image).decode("utf-8")
    result = {"image": result_image}
    return result

# 요청 모델 정의
class ExpandRequest(BaseModel):
    image: str          # Base64로 인코딩된 이미지 데이터
    top: int            # 확장할 픽셀 수(상)
    bottom: int         # 확장할 픽셀 수(하)
    left: int           # 확장할 픽셀 수(좌)
    right: int          # 확장할 픽셀 수(우)
    prompt: str         # 프롬프트
    resize: bool        # resize 여부
    width: int          # 확장할 이미지 width
    height: int         # 확장할 이미지 height

@app.post("/outpaint-sdxl/")
async def outpaint_sdxl(data: ExpandRequest):
    # Load images into memory
    #img = Image.open(BytesIO(base64.b64decode(data.image)))
    #img.save("image_from_client.png")
    #print(f"top:{data.top}, bottom:{data.bottom}, left:{data.left}, right:{data.right}" )
    result_image = comfyuiservice.get_image_with_outpainting_sdxl(reference_image_base64=data.image, left=data.left, right=data.right, top=data.top, bottom=data.bottom, prompt=data.prompt, resize=data.resize)
    result_image = Image.open(io.BytesIO(result_image))

    # 이미지 사이즈 계산해서 정확한 크기로 resize 하는 작업 (workflow 에서 픽셀 adjust 함. 결과 사이즈가 약간 달라짐.)
    img = Image.open(BytesIO(base64.b64decode(data.image)))
    width, height = img.size
    # 새로운 크기 계산
    new_width = width + data.left + data.right
    new_height = height + data.top + data.bottom

    # 이미지 리사이즈
    resized_image = result_image.resize((new_width, new_height), Image.LANCZOS)
    buffered = io.BytesIO()
    resized_image.save(buffered, format="PNG")

    result_image = "data:image/png;base64," + base64.b64encode(buffered.getvalue()).decode("utf-8")
    result = {"image": result_image}
    return result

@app.post("/outpaint-flux/")
async def outpaint_flux(data: ExpandRequest):
    # 이미지 사이즈 계산해서 정확한 크기로 resize 하는 작업 (workflow 에서 픽셀 adjust 함. 결과 사이즈가 약간 달라짐.)
    img = Image.open(BytesIO(base64.b64decode(data.image)))
    img.save('expand-original.png')
    print(img.size)
    print(f"top:{data.top}, bottom:{data.bottom}, left:{data.left}, right:{data.right}")
    #if img.mode == 'RGBA':
    #    img = await convert_transparent_to_white(img)

    # data의 width/height로 이미지 리사이즈
    """
    resized_image = img.resize((data.width, data.height), Image.LANCZOS)
    buffered = io.BytesIO()
    resized_image.save(buffered, format="PNG")
    resized_image.save('outpaint_resized.png', format="PNG")

    resized_image_base64 = base64.b64encode(buffered.getvalue()).decode("utf-8")
    """

    result_image = comfyuiservice.get_image_with_outpainting_flux(reference_image_base64=data.image, left=data.left, right=data.right, top=data.top, bottom=data.bottom, width=data.width, height=data.height, prompt=data.prompt, resize=data.resize)

    #image_save = Image.open(io.BytesIO(result_image))
    #image_save.save('outpaint_expand.png', format="PNG")

    result_image = "data:image/png;base64," + base64.b64encode(result_image).decode("utf-8")
    result = {"image": result_image}
    return result

# 요청 모델 정의
class FaceRequest(BaseModel):
    image: str              # Base64로 인코딩된 이미지 데이터
    prompt: str             # prompt

@app.post("/swap-face-image/")
async def swap_face_and_create_new_image(data: FaceRequest):
    # Load images into memory
    result_image = comfyuiservice.get_image_with_reference_pulid(reference_image_base64=data.image, prompt=data.prompt)
    result_image = "data:image/png;base64," + base64.b64encode(result_image).decode("utf-8")
    result = {"image": result_image}
    return result

@app.post("/swap-face-image-91/")
async def swap_face_and_create_new_image_91(data: FaceRequest):
    # Load images into memory
    result_image = comfyuiservice.get_image_with_reference_pulid_91(reference_image_base64=data.image, prompt=data.prompt)
    result_image = "data:image/png;base64," + base64.b64encode(result_image).decode("utf-8")
    result = {"image": result_image}
    return result

# 요청 모델 정의
class StickerRequest(BaseModel):
    image: str                  # Base64로 인코딩된 이미지 데이터
    model: str                  # model
    lora: str                   # lora model
    lora_strength: float        # lora strength
    sticker_strength: float     # sticker strength
    cartoon_strength: float     # cartoon strength
    smile_strength: float       # smile strength
    prompt: str                 # prompt
    negative_prompt: str        # negative prompt

@app.post("/sdxl-pulid-sticker")
async def sdxl_pulid_sticker(data: StickerRequest):
    result_image = comfyuiservice.get_sticker_sdxl_pulid(reference_image_base64=data.image, model=data.model, lora=data.lora, lora_strength=data.lora_strength, sticker_strength=data.sticker_strength, cartoon_strength=data.cartoon_strength, smile_strength=data.smile_strength, prompt=data.prompt, negative_prompt=data.negative_prompt)
    result_image = "data:image/png;base64," + base64.b64encode(result_image).decode("utf-8")
    result = {"image": result_image}
    return result

# 요청 모델 정의
class CaricatureRequest(BaseModel):
    image: str                  # Base64로 인코딩된 이미지 데이터
    model: str                  # model
    lora: str                   # lora model
    lora_strength: float        # lora strength
    prompt: str                 # prompt
    negative_prompt: str        # negative prompt

@app.post("/sdxl-pulid-caricature")
async def sdxl_pulid_caricature(data: CaricatureRequest):
    result_image = comfyuiservice.get_caricature_sdxl_pulid(reference_image_base64=data.image, model=data.model, lora=data.lora, lora_strength=data.lora_strength, prompt=data.prompt, negative_prompt=data.negative_prompt)
    result_image = "data:image/png;base64," + base64.b64encode(result_image).decode("utf-8")
    result = {"image": result_image}
    return result

# 요청 모델 정의
class EraserRequest(BaseModel):
    image: str              # Base64로 인코딩된 이미지 데이터
    mask: str               # Base64로 인코딩된 마스크 데이터
    eraser: str             # 지우개 방식

@app.post("/magic-eraser")
async def magic_eraser(data: EraserRequest):
    #img_mask = Image.open(BytesIO(base64.b64decode(data.mask))).convert('RGB')
    #img_mask.save("eraser_mask.png")
    #width, height = img_mask.size
    #print(f"마스크 이미지 크기: {width}x{height} , 마스크 이미지 모드: {img_mask.mode}")
    #buffered = io.BytesIO()
    #img_mask.save(buffered, format="PNG")  # PNG 등의 형식으로도 변경 가능
    #mask = base64.b64encode(buffered.getvalue()).decode("utf-8")

    img = Image.open(BytesIO(base64.b64decode(data.image)))
    if img.mode == 'RGBA':
        img = await convert_transparent_to_white(img)
    #img.save("eraser_image.png")
    #width, height = img.size
    #print(f"이미지 크기: {width}x{height} , 이미지 모드: {img.mode}")
    buffered = io.BytesIO()
    img.save(buffered, format="PNG")  # PNG 등의 형식으로도 변경 가능
    image = base64.b64encode(buffered.getvalue()).decode("utf-8")

    # Load images into memory
    #result_image = comfyuiservice.get_magic_eraser_image(image_base64=data.image, mask_image_base64=data.mask, eraser=data.eraser)
    result_image = comfyuiservice.get_magic_eraser_image(image_base64=image, mask_image_base64=data.mask, eraser=data.eraser)
    #print('result_image: ', result_image)
    result_image = "data:image/png;base64," + base64.b64encode(result_image).decode("utf-8")
    result = {"image": result_image}
    return result

# 요청 모델 정의
class FaceRequestV2(BaseModel):
    image1: str              # Base64로 인코딩된 이미지 데이터
    image2: str              # Base64로 인코딩된 이미지 데이터
    prompt: str              # prompt
    negative_prompt: str     # 부정 prompt
    method: str              # 처리 방식
    index: int               # 몇번째에 해당하는 이미지인지 선택
    width: int               # 생성할 이미지 가로 크기
    height: int              # 생성할 이미지 세로 크기

@app.post("/swap-face-single/")
async def swap_face_single(data: FaceRequestV2):
    # Load images into memory
    result_image = comfyuiservice.get_image_swap_face_single(reference_image_base64=data.image1, prompt=data.prompt, negative_prompt=data.negative_prompt, width=data.width, height=data.height)
    result_image = "data:image/png;base64," + base64.b64encode(result_image).decode("utf-8")
    result = {"image": result_image}
    return result

@app.post("/multi-realistic-photos/")
async def multi_images(data: FaceRequestV2):
    # Load images into memory
    result_image = comfyuiservice.get_image_swap_face_single(reference_image_base64=data.image1, prompt=data.prompt, negative_prompt=data.negative_prompt, width=data.width, height=data.height)
    result_image = "data:image/png;base64," + base64.b64encode(result_image).decode("utf-8")
    result = {"image": result_image}
    return result

@app.post("/swap-face-multiple/")
async def swap_face_multiple(data: FaceRequestV2):
    # Load images into memory
    result_image = comfyuiservice.get_image_swap_face_multiple(reference_image1_base64=data.image1, reference_image2_base64=data.image2, prompt=data.prompt, negative_prompt=data.negative_prompt, width=data.width, height=data.height)
    result_image = "data:image/png;base64," + base64.b64encode(result_image).decode("utf-8")
    result = {"image": result_image}
    return result

@app.post("/swap-face-select/")
async def swap_face_select(data: FaceRequestV2):
    # Load images into memory
    result_image = comfyuiservice.get_image_swap_face_select(reference_image_base64=data.image1, prompt=data.prompt, method=data.method, index=data.index, width=data.width, height=data.height)
    result_image = "data:image/png;base64," + base64.b64encode(result_image).decode("utf-8")
    result = {"image": result_image}
    return result

class LTXVRequest(BaseModel):
    image1: str              # Base64로 인코딩된 이미지 데이터
    prompt: str              # prompt

@app.post("/ltxv/")
async def ltxv(data: LTXVRequest):
    # Load images into memory
    result = comfyuiservice.get_ltxv_video(image_base64=data.image1, prompt=data.prompt)
    
    # Return the result directly
    return result

# 요청 모델 정의
class FaceInpainting(BaseModel):
    image: str                  # Base64로 인코딩된 이미지 데이터
    mask: str                   # Base64로 인코딩된 마스크 데이터
    prompt: str                 # prompt
    negative_prompt: str        # negative prompt
    ref_image: str              # 레퍼런스 얼굴 이미지

@app.post("/face-inpainting/")
async def face_inpainting(data: FaceInpainting):
    # Load images into memory
    result_image = comfyuiservice.get_face_inpainting(image_base64=data.image, mask_image_base64=data.mask, prompt=data.prompt, negative_prompt=data.negative_prompt, ref_image=data.ref_image)
    result_image = "data:image/png;base64," + base64.b64encode(result_image).decode("utf-8")
    result = {"image": result_image}
    return result

@app.get("/hello")
def read_hello():
    return {"message": "Hello World!"}
