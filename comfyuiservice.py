import websocket
import uuid
import json
import os
import urllib.request
import urllib.parse
from PIL import Image
from io import BytesIO
import base64
import io
import random
import socket
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)

save_image_websocket = 'SaveImageWebsocket'
save_video_websocket = 'SaveVideoWebsocket'
server_address = "127.0.0.1:8188"
#server_address = "49.254.222.239:8188"
client_id = str(uuid.uuid4())

# for magic eranser
def get_magic_eraser_json(image_base64, mask_image_base64, eraser):
    IMAGEID = "85"
    MASKID = "99"

    workflow_folder = "workflows-api"
    if eraser == "lama":
        file_name = "magic-eraser-lama-api.json"
    else:
        file_name = "magic-eraser-magic-api.json"
        MASKID = "86"

    # with open("image.txt", "w") as file:
    #     file.write(str(image_base64))  # Convert result to string if it's not already

    # with open("mask.txt", "w") as file:
    #     file.write(str(mask_image_base64))  # Convert result to string if it's not already

    # Construct the full path to the JSON file
    file_path = os.path.join(workflow_folder, file_name)

    # Open the JSON file and load its content into a variable
    with open(file_path, "r", encoding="utf8") as file:
        prompt_json = json.load(file)
        prompt_json[IMAGEID]["inputs"]["image"] = image_base64
        prompt_json[MASKID]["inputs"]["mask"] = mask_image_base64
        return prompt_json

# for magic eranser
def get_face_inpainting_json(image_base64, mask_image_base64, prompt, negative_prompt, ref_image):
    random_number = random.randint(10**14, 10**15 - 1)
    workflow_folder = "workflows-api"
    #file_name = "face-inpaint-api.json"
    if ref_image == "NONE":
        file_name = "face-inpaint-api.json"
        IMAGEID = "136"
        MASKID = "137"
        REFIMAGEID = "136"
        PROMPTID = "133"
        NPROMPTID = "134"
        SEEDID = "3"     # seed
    else:
        file_name = "face-inpaint-pulid-api-gguf.json"
        IMAGEID = "101"
        MASKID = "102"
        REFIMAGEID = "103"
        PROMPTID = "78"
        NPROMPTID = "79"
        SEEDID = "73"     # seed

    # Construct the full path to the JSON file
    file_path = os.path.join(workflow_folder, file_name)

    # Open the JSON file and load its content into a variable
    with open(file_path, "r", encoding="utf8") as file:
        prompt_json = json.load(file)
        prompt_json[IMAGEID]["inputs"]["image"] = image_base64
        prompt_json[MASKID]["inputs"]["mask"] = mask_image_base64
        prompt_json[PROMPTID]["inputs"]["clip_l"] = prompt
        prompt_json[PROMPTID]["inputs"]["t5xxl"] = prompt
        prompt_json[NPROMPTID]["inputs"]["clip_l"] = negative_prompt
        prompt_json[NPROMPTID]["inputs"]["t5xxl"] = negative_prompt
        prompt_json[SEEDID]["inputs"]["seed"] = random_number

        if ref_image != "NONE":
            prompt_json[REFIMAGEID]["inputs"]["image"] = image_base64

        return prompt_json

# for sticker
def get_sticker_sdxl_pulid_json(reference_image_base64, model, lora, lora_strength, sticker_strength, cartoon_strength, smile_strength, prompt, negative_prompt):
    REFERENCEIMAGEID = "558"
    MODELID = "305"
    LORAID = "405"
    PROMPTID = "540"
    NEGATIVE_PROMPTID = "555"
    SEED1ID = "404"     # seed everywhere for Ksampler Efficient 1
    SEED2ID = "560"     # seed everywhere for Ksampler Efficient 2
    #SEED3ID = "561"     # FaceDetailerPipe
    #SEED4ID = "563"     # KSampler (pipe)

    random_numbers = [str(random.randint(10**14, 10**15 - 1)) for _ in range(4)]

    workflow_folder = "workflows-api"
    file_name = "sdxl-pulid-sticker-api-v2.json"

    # Construct the full path to the JSON file
    file_path = os.path.join(workflow_folder, file_name)

    # Open the JSON file and load its content into a variable
    with open(file_path, "r", encoding="utf8") as file:
        prompt_json = json.load(file)
        prompt_json[REFERENCEIMAGEID]["inputs"]["image"] = reference_image_base64
        prompt_json[MODELID]["inputs"]["ckpt_name"] = model
        prompt_json[LORAID]["inputs"]["lora_1_strength"] = sticker_strength
        prompt_json[LORAID]["inputs"]["lora_2_strength"] = cartoon_strength
        prompt_json[LORAID]["inputs"]["lora_3_strength"] = smile_strength
        prompt_json[LORAID]["inputs"]["lora_4_name"] = lora
        prompt_json[LORAID]["inputs"]["lora_4_strength"] = lora_strength
        prompt_json[PROMPTID]["inputs"]["text"] = prompt
        prompt_json[NEGATIVE_PROMPTID]["inputs"]["text"] = negative_prompt
        prompt_json[SEED1ID]["inputs"]["seed"] = random_numbers[0]
        prompt_json[SEED2ID]["inputs"]["seed"] = random_numbers[1]
        #prompt_json[SEED3ID]["inputs"]["seed"] = random_numbers[2]
        #prompt_json[SEED4ID]["inputs"]["seed"] = random_numbers[3]
        return prompt_json

# for caricature
def get_caricature_sdxl_pulid_json(reference_image_base64, model, lora, lora_strength, prompt, negative_prompt):
    REFERENCEIMAGEID = "573"
    MODELID = "305"
    LORAID = "405"
    PROMPTID = "540"
    NEGATIVE_PROMPTID = "555"
    SEEDID = "404"     # seed everywhere for Ksampler Efficient 1

    random_number = random.randint(10**14, 10**15 - 1)

    workflow_folder = "workflows-api"
    file_name = "sdxl-pulid-caricature-api.json"

    # Construct the full path to the JSON file
    file_path = os.path.join(workflow_folder, file_name)

    # Open the JSON file and load its content into a variable
    with open(file_path, "r", encoding="utf8") as file:
        prompt_json = json.load(file)
        prompt_json[REFERENCEIMAGEID]["inputs"]["image"] = reference_image_base64
        prompt_json[MODELID]["inputs"]["ckpt_name"] = model
        prompt_json[LORAID]["inputs"]["lora_4_name"] = lora
        prompt_json[LORAID]["inputs"]["lora_4_strength"] = lora_strength
        prompt_json[PROMPTID]["inputs"]["text"] = prompt
        prompt_json[NEGATIVE_PROMPTID]["inputs"]["text"] = negative_prompt
        prompt_json[SEEDID]["inputs"]["seed"] = random_number
        return prompt_json

# for inpainting logo on target image
def get_inpaint_image_on_target_json(inpaint_image_base64, target_image_base64, mask_image_base64):
    TARGETIMAGEID = "405"
    INPAINTIMAGEID = "404"
    MASKIMAGEID = "403"
    SEEDID = "3"     # seed everywhere for Ksampler Efficient 1

    random_number = random.randint(10**14, 10**15 - 1)

    workflow_folder = "workflows-api"
    file_name = "replace_item_api.json"

    # Construct the full path to the JSON file
    file_path = os.path.join(workflow_folder, file_name)
    print(f"file path: {file_path}")

    # Open the JSON file and load its content into a variable
    with open(file_path, "r", encoding="utf8") as file:
        prompt_json = json.load(file)
        prompt_json[TARGETIMAGEID]["inputs"]["image"] = target_image_base64
        prompt_json[INPAINTIMAGEID]["inputs"]["image"] = inpaint_image_base64
        prompt_json[MASKIMAGEID]["inputs"]["mask"] = mask_image_base64
        prompt_json[SEEDID]["inputs"]["seed"] = random_number
        return prompt_json

# swap cloth on model image with mask
def swap_cloth_model_iamge_json(model_image_base_64, cloth_image_base_64, mask_image_base_64):
    CLOTHIMAGEID = "410"
    MODELIMAGEID = "412"
    MASKIMAGEID = "393"
    file_path = "data.json"
    workflow_folder = "workflows-api"
    file_name = "flux-redux-cloth-swap-api.json"
    # Construct the full path to the JSON file
    file_path = os.path.join(workflow_folder, file_name)
    # Open the JSON file and load its content into a variable
    with open(file_path, "r") as file:
        prompt_json = json.load(file)
        prompt_json[CLOTHIMAGEID]["inputs"]["image"] = cloth_image_base_64
        prompt_json[MODELIMAGEID]["inputs"]["image"] = model_image_base_64
        prompt_json[MASKIMAGEID]["inputs"]["mask"] = mask_image_base_64
        return prompt_json
    
# swap cloth on model image with mask
def multi_photos_json(prompt):
    POSITIVEPROMPTID = "6"

    file_path = "data.json"
    workflow_folder = "workflows-api"
    file_name = "portrait_realism_api.json"
    # Construct the full path to the JSON file
    file_path = os.path.join(workflow_folder, file_name)
    # Open the JSON file and load its content into a variable
    print("aaaa")
    with open(file_path, "r") as file:
        prompt_json = json.load(file)
        prompt_json[POSITIVEPROMPTID]["inputs"]["text"] = prompt
        return prompt_json

# swap cloth on model image with mask
def swap_cloth_model_iamge_json(model_image_base_64, cloth_image_base_64, mask_image_base_64):
    CLOTHIMAGEID = "410"
    MODELIMAGEID = "412"
    MASKIMAGEID = "393"
    file_path = "data.json"
    workflow_folder = "workflows-api"
    file_name = "flux-redux-cloth-swap-api.json"
    # Construct the full path to the JSON file
    file_path = os.path.join(workflow_folder, file_name)
    # Open the JSON file and load its content into a variable
    with open(file_path, "r") as file:
        prompt_json = json.load(file)
        prompt_json[CLOTHIMAGEID]["inputs"]["image"] = cloth_image_base_64
        prompt_json[MODELIMAGEID]["inputs"]["image"] = model_image_base_64
        prompt_json[MASKIMAGEID]["inputs"]["mask"] = mask_image_base_64
        return prompt_json

# ltxv
def ltxv_distilled_json(image_base_64, prompt):
    POSITIVEPROMPTID = "6"
    LOADIMAGEID = "1880"

    file_path = "data.json"
    workflow_folder = "workflows-api/video"
    file_name = "ltxv-0.9.7.json"
    # Construct the full path to the JSON file
    file_path = os.path.join(workflow_folder, file_name)
    # Open the JSON file and load its content into a variable
    with open(file_path, "r") as file:
        prompt_json = json.load(file)
        prompt_json[POSITIVEPROMPTID]["inputs"]["text"] = prompt
        prompt_json[LOADIMAGEID]["inputs"]["base64_data"] = image_base_64
        return prompt_json
    
# flux ultimate sd upscale
def flux_ultimate_sd_upscale_json(image_base_64):
    LOADIMAGEID = "16"

    file_path = "data.json"
    workflow_folder = "workflows-api"
    file_name = "flux-upscaler-ultimate-sd-api.json"
    # Construct the full path to the JSON file
    file_path = os.path.join(workflow_folder, file_name)
    # Open the JSON file and load its content into a variable
    with open(file_path, "r") as file:
        prompt_json = json.load(file)
        prompt_json[LOADIMAGEID]["inputs"]["base64_data"] = image_base_64
        return prompt_json
    
# qwen image edit
def qwen_image_edit_json(image_base_64, prompt):
    PROMPTID = "20"
    LOADIMAGEID = "45"

    file_path = "data.json"
    workflow_folder = "workflows-api"
    file_name = "qwen-edit-api.json"
    # Construct the full path to the JSON file
    file_path = os.path.join(workflow_folder, file_name)
    # Open the JSON file and load its content into a variable
    with open(file_path, "r") as file:
        prompt_json = json.load(file)
        prompt_json[LOADIMAGEID]["inputs"]["base64_data"] = image_base_64
        prompt_json[PROMPTID]["inputs"]["prompt"] = prompt
        return prompt_json


# uses the flux-guff-text-api.json workflow to generate image with prompt
def get_cloth_with_prompt(prompt):
    TEXTID = "6"

    file_path = "data.json"

    workflow_folder = "workflows-api"
    file_name = "flux-guff-text-api.json"

    # Construct the full path to the JSON file
    file_path = os.path.join(workflow_folder, file_name)

    # Open the JSON file and load its content into a variable
    with open(file_path, "r") as file:
        prompt_json = json.load(file)
        prompt_json[TEXTID]["inputs"]["text"] = prompt
        return prompt_json

# flux pulid
def flux_pulid_json(reference_image_base64, prompt):
    REFERENCEIMAGEID = "66"
    PROMPTID = "6"

    workflow_folder = "workflows-api"
    file_name = "flux-pulid-api.json"
    # Construct the full path to the JSON file
    file_path = os.path.join(workflow_folder, file_name)
    # Open the JSON file and load its content into a variable
    with open(file_path, "r") as file:
        prompt_json = json.load(file)
        prompt_json[REFERENCEIMAGEID]["inputs"]["image"] = reference_image_base64
        prompt_json[PROMPTID]["inputs"]["text"] = prompt
        return prompt_json

# flux pulid
def flux_pulid_json_91(reference_image_base64, prompt):
    REFERENCEIMAGEID = "66"
    PROMPTID = "6"

    workflow_folder = "workflows-api"
    file_name = "flux-pulid-api_91.json"
    # Construct the full path to the JSON file
    file_path = os.path.join(workflow_folder, file_name)
    # Open the JSON file and load its content into a variable
    with open(file_path, "r") as file:
        prompt_json = json.load(file)
        prompt_json[REFERENCEIMAGEID]["inputs"]["image"] = reference_image_base64
        prompt_json[PROMPTID]["inputs"]["text"] = prompt
        return prompt_json

# flux pulid single
def flux_pulid_single_json(reference_image_base64, prompt, negative_prompt, width, height):
    REFERENCEIMAGEID = "207"
    PROMPTID = "202"
    NPROMPTID = "203"
    IMAGESIZEID = "113"
    RANDOMID = "205"

    random_number = random.randint(10**14, 10**15 - 1)

    workflow_folder = "workflows-api"
    file_name = "PuLID2_single_api.json"
    # Construct the full path to the JSON file
    file_path = os.path.join(workflow_folder, file_name)
    # Open the JSON file and load its content into a variable
    with open(file_path, "r", encoding="utf-8") as file:
        prompt_json = json.load(file)
        prompt_json[REFERENCEIMAGEID]["inputs"]["image"] = reference_image_base64
        prompt_json[PROMPTID]["inputs"]["clip_l"] = prompt
        prompt_json[PROMPTID]["inputs"]["t5xxl"] = prompt
        prompt_json[NPROMPTID]["inputs"]["clip_l"] = negative_prompt
        prompt_json[NPROMPTID]["inputs"]["t5xxl"] = negative_prompt
        prompt_json[IMAGESIZEID]["inputs"]["width"] = width
        prompt_json[IMAGESIZEID]["inputs"]["height"] = height
        prompt_json[RANDOMID]["inputs"]["noise_seed"] = random_number
        return prompt_json

# flux pulid single
def flux_pulid_multiple_json(reference_image1_base64, reference_image2_base64, prompt, negative_prompt, width, height):
    REFERENCEIMAGE1ID = "203"
    REFERENCEIMAGE2ID = "204"
    PROMPTID = "200"
    NPROMPTID = "201"
    IMAGESIZEID = "202"
    RANDOMID = "199"

    random_number = random.randint(10**14, 10**15 - 1)
    workflow_folder = "workflows-api"
    file_name = "PuLID2_multi_api.json"
    # Construct the full path to the JSON file
    file_path = os.path.join(workflow_folder, file_name)
    # Open the JSON file and load its content into a variable
    with open(file_path, "r", encoding="utf-8") as file:
        prompt_json = json.load(file)
        prompt_json[REFERENCEIMAGE1ID]["inputs"]["image"] = reference_image1_base64
        prompt_json[REFERENCEIMAGE2ID]["inputs"]["image"] = reference_image2_base64
        prompt_json[PROMPTID]["inputs"]["clip_l"] = prompt
        prompt_json[PROMPTID]["inputs"]["t5xxl"] = prompt
        prompt_json[NPROMPTID]["inputs"]["clip_l"] = negative_prompt
        prompt_json[NPROMPTID]["inputs"]["t5xxl"] = negative_prompt
        prompt_json[IMAGESIZEID]["inputs"]["width"] = width
        prompt_json[IMAGESIZEID]["inputs"]["height"] = height
        prompt_json[RANDOMID]["inputs"]["noise_seed"] = random_number
        return prompt_json

# flux choice
def flux_pulid_select_json(reference_image_base64, prompt, method, index, width, height):
    REFERENCEIMAGEID = "205"
    PROMPTID = "107"
    IMAGESIZEID = "113"
    RANDOMID = "111"
    SELECTID = "197"

    random_number = random.randint(10**14, 10**15 - 1)

    workflow_folder = "workflows-api"
    file_name = "PuLID2_select_ref_api.json"
    # Construct the full path to the JSON file
    file_path = os.path.join(workflow_folder, file_name)
    # Open the JSON file and load its content into a variable
    with open(file_path, "r", encoding="utf-8") as file:
        prompt_json = json.load(file)
        prompt_json[REFERENCEIMAGEID]["inputs"]["image"] = reference_image_base64
        prompt_json[PROMPTID]["inputs"]["text"] = prompt
        prompt_json[IMAGESIZEID]["inputs"]["width"] = width
        prompt_json[IMAGESIZEID]["inputs"]["height"] = height
        prompt_json[RANDOMID]["inputs"]["noise_seed"] = random_number
        prompt_json[SELECTID]["inputs"]["input_faces_order"] = method
        prompt_json[SELECTID]["inputs"]["input_faces_index"] = index
        return prompt_json

# outpainting sdxl
def outpainting_sdxl_json(reference_image_base64, left, right, top, bottom, prompt):
    REFERENCEIMAGEID = "361"
    NEWIMAGESIZENODEID = "340"
    IMAGEBLENDADVANCENODEID = "355"
    SEEDID = "24"
    PROMPTID = "366"

    random_number = random.randint(10**14, 10**15 - 1)

    image_data = base64.b64decode(reference_image_base64)
    # Open the image using Pillow
    image = Image.open(BytesIO(image_data))
    # Get width and height
    width, height = image.size
    # calculate x and y pivot
    new_width = width + left + right
    new_height = height + top + bottom
    center_point_width = width / 2
    center_point_height = height / 2


    x_percent = (center_point_width + left) / new_width * 100
    y_percent = (center_point_height + top) / new_height  * 100

    workflow_folder = "workflows-api"
    file_name = "sdxl-outpainting-api-v2.json"
    # Construct the full path to the JSON file
    file_path = os.path.join(workflow_folder, file_name)
    # Open the JSON file and load its content into a variable
    with open(file_path, "r", encoding="utf8") as file:
        prompt_json = json.load(file)
        prompt_json[REFERENCEIMAGEID]["inputs"]["image"] = reference_image_base64
        prompt_json[NEWIMAGESIZENODEID]["inputs"]["width"] = new_width
        prompt_json[NEWIMAGESIZENODEID]["inputs"]["height"] = new_height
        prompt_json[IMAGEBLENDADVANCENODEID]["inputs"]["x_percent"] = x_percent
        prompt_json[IMAGEBLENDADVANCENODEID]["inputs"]["y_percent"] = y_percent
        prompt_json[SEEDID]["inputs"]["seed"] = random_number
        prompt_json[PROMPTID]["inputs"]["text"] = prompt
        return prompt_json

# outpainting sdxl
def outpainting_flux_json(reference_image_base64, left, right, top, bottom, width, height, prompt, resize):
    REFERENCEIMAGEID = "58"
    SEEDID = "3"
    #PROMPTID = "23"
    PADID = "44"
    RESIZEID = "63"

    random_number = random.randint(10**14, 10**15 - 1)

    image_data = base64.b64decode(reference_image_base64)
    # Open the image using Pillow
    image = Image.open(BytesIO(image_data))
    image.save("ref_image_1.png")

    resize_ratio = 1
    max_dimension = 1200 if resize else 1920
    original_width, original_height = image.size

    # 실제 늘어나는 크기 계산
    resize_width_scale = original_width / width
    resize_height_scale = original_height / height
    resize_left = left * resize_width_scale
    resize_right = right * resize_width_scale
    resize_top = top * resize_height_scale
    resize_bottom = bottom * resize_height_scale

    if resize or ((original_width+resize_left+resize_right) >= 1920 or (original_height+resize_top+resize_bottom) >= 1920):
        # 리사이즈 비율 계산
        resize_ratio = calculate_resize_ratio(
            original_width, original_height,
            resize_left, resize_right,
            resize_top, resize_bottom,
            max_dimension
        )

    if resize_ratio < 1:
        resize_left = int(resize_left * resize_ratio)
        resize_right = int(resize_right * resize_ratio)
        resize_top = int(resize_top * resize_ratio)
        resize_bottom = int(resize_bottom * resize_ratio)

        new_width = int(original_width * resize_ratio)
        new_height = int(original_height * resize_ratio)

        # 이미지 축소 (LANCZOS 보간법 사용)
        image_new = image.resize((new_width, new_height), Image.LANCZOS)
        # 이미지 다시 Base64 인코딩
        buffered = io.BytesIO()
        image_new.save(buffered, format="PNG")
        reference_image_base64 = base64.b64encode(buffered.getvalue()).decode('utf-8')

    workflow_folder = "workflows-api"
    file_name = "flux-outpainting-api.json"
    # Construct the full path to the JSON file
    file_path = os.path.join(workflow_folder, file_name)

    print(f"resize ratio: {resize_ratio}")
    image_data = base64.b64decode(reference_image_base64)
    # Open the image using Pillow
    image = Image.open(BytesIO(image_data))
    image.save("ref_image_2.png")

    # Open the JSON file and load its content into a variable
    with open(file_path, "r", encoding="utf8") as file:
        prompt_json = json.load(file)
        prompt_json[REFERENCEIMAGEID]["inputs"]["image"] = reference_image_base64
        prompt_json[SEEDID]["inputs"]["seed"] = random_number
        #prompt_json[PROMPTID]["inputs"]["text"] = prompt
        prompt_json[PADID]["inputs"]["left"] = resize_left
        prompt_json[PADID]["inputs"]["top"] = resize_top
        prompt_json[PADID]["inputs"]["right"] = resize_right
        prompt_json[PADID]["inputs"]["bottom"] = resize_bottom
        #prompt_json[RESIZEID]["inputs"]["width"] = new_width
        #prompt_json[RESIZEID]["inputs"]["height"] = new_height

        return prompt_json

def calculate_resize_ratio(original_width, original_height, expand_left, expand_right, expand_top, expand_bottom, max_dimension=1200):
    """
    원본 이미지와 확장 픽셀 수를 받아 최대 크기를 초과하지 않는 리사이즈 비율 계산

    Args:
        original_width (int): 원본 이미지 너비
        original_height (int): 원본 이미지 높이
        expand_left (int): 좌측 확장 픽셀 수
        expand_right (int): 우측 확장 픽셀 수
        expand_top (int): 상단 확장 픽셀 수
        expand_bottom (int): 하단 확장 픽셀 수
        max_dimension (int): 최대 허용 이미지 크기

    Returns:
        float: 리사이즈 비율 (1.0 이하)
    """
    # 확장 후 예상 크기
    target_width = original_width + expand_left + expand_right
    target_height = original_height + expand_top + expand_bottom

    # 최대 크기를 초과하는지 확인
    if target_width <= max_dimension and target_height <= max_dimension:
        # 리사이즈 필요 없음
        return 1

    # 가로/세로 중 최대 크기를 초과하는 쪽을 기준으로 비율 계산
    width_ratio = max_dimension / target_width if target_width > max_dimension else 1
    height_ratio = max_dimension / target_height if target_height > max_dimension else 1

    # 더 작은 비율을 선택 (가로, 세로 모두 max_dimension 이하가 되도록)
    resize_ratio = min(width_ratio, height_ratio)

    return resize_ratio

def queue_prompt(prompt):
    p = {"prompt": prompt, "client_id": client_id}
    data = json.dumps(p).encode('utf-8')
    req =  urllib.request.Request("http://{}/prompt".format(server_address), data=data)
    return json.loads(urllib.request.urlopen(req).read())

def get_images(ws, prompt):
    try:
        prompt_id = queue_prompt(prompt)['prompt_id']
        output_image = None
        current_node = ""

        while True:
            try:
                out = ws.recv()
            except (websocket.WebSocketTimeoutException, socket.timeout):
                logging.warning("WebSocket timed out while receiving data.")
                break
            except Exception as e:
                logging.error(f"WebSocket receive error: {e}")
                break

            if isinstance(out, str):
                try:
                    message = json.loads(out)
                    if message['type'] == 'executing':
                        data = message['data']
                        if data['prompt_id'] == prompt_id:
                            if data['node'] is None:
                                break
                            else:
                                node_number = data['node']
                                current_node = prompt[node_number]["class_type"]
                except json.JSONDecodeError as e:
                    logging.error(f"JSON decode error: {e}")
                    continue
            else:
                if current_node == save_image_websocket:
                    output_image = out[8:]

        return output_image

    finally:
        ws.close()
        logging.info("WebSocket connection closed.")

def get_images_array(ws, prompt):
    try:
        prompt_id = queue_prompt(prompt)['prompt_id']
        output_images = []
        current_node = ""

        while True:
            try:
                out = ws.recv()
            except (websocket.WebSocketTimeoutException, socket.timeout):
                logging.warning("WebSocket timed out while receiving data.")
                break
            except Exception as e:
                logging.error(f"WebSocket receive error: {e}")
                break

            if isinstance(out, str):
                try:
                    message = json.loads(out)
                    if message['type'] == 'executing':
                        data = message['data']
                        if data['prompt_id'] == prompt_id:
                            if data['node'] is None:
                                break
                            else:
                                node_number = data['node']
                                current_node = prompt[node_number]["class_type"]
                except json.JSONDecodeError as e:
                    logging.error(f"JSON decode error: {e}")
                    continue
            else:
                if current_node == save_image_websocket:
                    output_images.append(out[8:])

        return output_images

    finally:
        ws.close()
        logging.info("WebSocket connection closed.")

def wrap_websocket_call(prompt_generator):
    ws = websocket.WebSocket()
    ws.settimeout(30)
    ws.connect(f"ws://{server_address}/ws?clientId={client_id}")
    try:
        return get_images(ws, prompt_generator)
    finally:
        if ws:
            ws.close()

def wrap_websocket_call_array_result(prompt_generator):
    ws = websocket.WebSocket()
    ws.settimeout(30)
    ws.connect(f"ws://{server_address}/ws?clientId={client_id}")
    try:
        return get_images_array(ws, prompt_generator)
    finally:
        if ws:
            ws.close()

def fetch_image_from_comfy(input):
    return wrap_websocket_call(get_cloth_with_prompt(
        input))

def get_model_image_with_cloth(cloth_base_64, model_base_64, mask_base_64):
    return wrap_websocket_call(swap_cloth_model_iamge_json(
        cloth_image_base_64=cloth_base_64,
        model_image_base_64=model_base_64,
        mask_image_base_64=mask_base_64))

def get_target_image_with_logo(target_image_base64, logo_image_base64, mask_image_base64):
    return wrap_websocket_call(get_inpaint_image_on_target_json(
        inpaint_image_base64=logo_image_base64,
        target_image_base64=target_image_base64,
        mask_image_base64=mask_image_base64))

# Gets new image with prompt and reference image using Pulid
def get_image_with_reference_pulid(reference_image_base64, prompt):
    return wrap_websocket_call(flux_pulid_json(
        reference_image_base64=reference_image_base64,
        prompt=prompt))

# Gets new image with prompt and reference image using Pulid
def get_image_with_reference_pulid_91(reference_image_base64, prompt):
    return wrap_websocket_call(flux_pulid_json_91(
        reference_image_base64=reference_image_base64,
        prompt=prompt))

# Gets new image with prompt and reference image using Pulid
def get_sticker_sdxl_pulid(reference_image_base64, model, lora, lora_strength, sticker_strength, cartoon_strength, smile_strength, prompt, negative_prompt):
    return wrap_websocket_call(get_sticker_sdxl_pulid_json(
        reference_image_base64=reference_image_base64,
        model=model, lora=lora,
        lora_strength=lora_strength,
        sticker_strength=sticker_strength,
        cartoon_strength=cartoon_strength,
        smile_strength=smile_strength,
        prompt=prompt,
        negative_prompt=negative_prompt))

# Gets new image with prompt and reference image using Pulid
def get_caricature_sdxl_pulid(reference_image_base64, model, lora, lora_strength, prompt, negative_prompt):
    return wrap_websocket_call(get_caricature_sdxl_pulid_json(
        reference_image_base64=reference_image_base64,
        model=model,
        lora=lora,
        lora_strength=lora_strength,
        prompt=prompt,
        negative_prompt=negative_prompt))

# Gets outpainting image with increaes in each sides
def get_image_with_outpainting_sdxl(reference_image_base64, left, right, top, bottom, prompt):
    return wrap_websocket_call(outpainting_sdxl_json(
        reference_image_base64=reference_image_base64,
        left=left,
        right=right,
        top=top,
        bottom=bottom,
        prompt=prompt))

def get_image_with_outpainting_flux(reference_image_base64, left, right, top, bottom, width, height, prompt, resize):
    return wrap_websocket_call(outpainting_flux_json(
        reference_image_base64=reference_image_base64,
        left=left,
        right=right,
        top=top,
        bottom=bottom,
        width=width,
        height=height,
        prompt=prompt,
        resize=resize))

# Gets new image with object removed, input target image and mask where mask area is where object is removed
def get_magic_eraser_image(image_base64, mask_image_base64, eraser):
    return wrap_websocket_call(get_magic_eraser_json(
        image_base64=image_base64,
        mask_image_base64=mask_image_base64,
        eraser=eraser))

# Gets new image with prompt and reference image using Pulid (single face)
def get_image_swap_face_single(reference_image_base64, prompt, negative_prompt, width, height):
    return wrap_websocket_call(flux_pulid_single_json(
        reference_image_base64=reference_image_base64,
        prompt=prompt,
        negative_prompt=negative_prompt,
        width=width,
        height=height))

# Gets new image with prompt and reference image using Pulid (2 faces)
def get_image_swap_face_multiple(reference_image1_base64, reference_image2_base64, prompt, negative_prompt, width, height):
    return wrap_websocket_call(flux_pulid_multiple_json(
        reference_image1_base64=reference_image1_base64,
        reference_image2_base64=reference_image2_base64,
        prompt=prompt,
        negative_prompt=negative_prompt,
        width=width,
        height=height))

# Gets new image with prompt and reference image using Pulid (2 faces)
def get_image_swap_face_select(reference_image_base64, prompt, method, index, width, height):
    return wrap_websocket_call(flux_pulid_select_json(
        reference_image_base64=reference_image_base64,
        prompt=prompt,
        method=method,
        index=index,
        width=width,
        height=height))

# Gets new image with prompt
def get_face_inpainting(image_base64, mask_image_base64, prompt, negative_prompt, ref_image):
    return wrap_websocket_call(get_face_inpainting_json(
        image_base64=image_base64,
        mask_image_base64=mask_image_base64,
        prompt=prompt,
        negative_prompt=negative_prompt,
        ref_image=ref_image))

# Gets new image to video for LTXV 0.9.6 distilled model
def get_ltxv_video(image_base64, prompt):
    wrap_websocket_call(ltxv_distilled_json(image_base64, prompt))
    video_path = r"C:\Comfyui_V4\ComfyUI_windows_portable_nvidia\ComfyUI_windows_portable\ComfyUI\output\ltxv-video"
        
    # Find the most recent video file in the directory
    video_files = [f for f in os.listdir(video_path) if f.endswith(('.mp4', '.avi', '.mov'))]
    if not video_files:
        raise Exception(f"No video files found in {video_path}")
        
    # Sort by creation time, newest first
    video_files.sort(key=lambda x: os.path.getmtime(os.path.join(video_path, x)), reverse=True)
    latest_video = os.path.join(video_path, video_files[0])

    base_filename = os.path.splitext(os.path.basename(latest_video))[0]

    # Read the video file and encode it to base64
    with open(latest_video, "rb") as video_file:
        video_data = video_file.read()
        encoded_video = base64.b64encode(video_data).decode('utf-8')

    # Try to find and delete a PNG with the same prefix
    try:
        matching_png = next(
            (f for f in os.listdir(video_path) if f.startswith(base_filename) and f.endswith(".png")),
            None
        )
        if matching_png:
            png_path = os.path.join(video_path, matching_png)
            os.remove(png_path)
            print(f"Deleted PNG file: {png_path}")
        else:
            print("no matching png")
            print(base_filename)
    except Exception as e:
        print(f"Failed to delete PNG file: {e}")
    
    # Now delete the file
    try:
        os.remove(latest_video)
        print(f"Deleted video file: {latest_video}")
    except Exception as e:
        print(f"Failed to delete video file: {e}")
    
    # Return the video with proper data URL format
    return {
        "video": f"data:video/mp4;base64,{encoded_video}",
        "metadata": {
            "fps": 30,
            "frames": 150,
            "duration": 5.0
        }
    }

# Gets new image to video for LTXV 0.9.6 distilled model
def get_flux_upscale(image_base64):
    return wrap_websocket_call(flux_ultimate_sd_upscale_json(image_base64))

# Gets new image to video for LTXV 0.9.6 distilled model
def get_qwen_image_edit(image_base64, prompt):
    return wrap_websocket_call(qwen_image_edit_json(image_base64, prompt))

def get_multi_photo(prompt):
    result = wrap_websocket_call_array_result(multi_photos_json(
        prompt=prompt))

    return result