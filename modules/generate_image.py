import json
import os
import dotenv
import aiohttp

dotenv.load_dotenv()
URL = os.getenv('URL')
DEFAULTPROMPT = os.getenv('DEFAULTPROMPT')
NEGATIVEPROMPT = os.getenv('NEGATIVEPROMPT')

# TODO place these in a config file at some point
batch_size = 1
steps = 28
cfg_scale = 12

async def generate_image(prompt, neg_prompt, width: int, height: int, seed: int, sampler, model, hypernetwork, hypernetwork_strenght):

    if DEFAULTPROMPT:
        prompt = f"{DEFAULTPROMPT}, {prompt}"

    if NEGATIVEPROMPT:
        neg_prompt = f"{NEGATIVEPROMPT}, {neg_prompt}"

    # TODO config for parameters
    # edit default steps and CFG scale here
    data = {
        "prompt": prompt,
        "negative_prompt": neg_prompt,
        "seed": seed,
        "batch_size": batch_size,
        "steps": steps,
        "cfg_scale": cfg_scale,
        "width": width,
        "height": height,
        "sampler_index": sampler
    }

    headers = {
        'Content-Type': 'application/json'
    }

    override_settings = {}

    # TODO might move this to config instead since the changes stay
    if model:
        option_settings = {"sd_model_checkpoint": model}
        print(f"Changing model to {model}")
        async with aiohttp.ClientSession() as session:
            async with session.post(f"{URL}/sdapi/v1/options", headers=headers, json=option_settings) as resp:
                await resp.json()
                print(f"Changed model to {model}")

    if hypernetwork:
        override_settings["sd_hypernetwork"] = hypernetwork
    
    if hypernetwork_strenght:
        override_settings["sd_hypernetwork_strength"] = hypernetwork_strenght

    override_data = {
        "override_settings": override_settings
    }

    print(override_data)

    data.update(override_data)

    async with aiohttp.ClientSession() as session:
        async with session.post(f"{URL}/sdapi/v1/txt2img", headers=headers, json=data) as resp:
            return await resp.json()
        
async def interrupt():
    async with aiohttp.ClientSession() as cs:
        async with cs.post(f"{URL}/sdapi/v1/interrupt") as result:
            print("Interrupted!")