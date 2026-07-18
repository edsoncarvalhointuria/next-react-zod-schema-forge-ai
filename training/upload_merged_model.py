from transformers import AutoModelForCausalLM, AutoTokenizer
from peft import PeftModel
from huggingface_hub import login
from dotenv import load_dotenv
import os
import torch

load_dotenv()

login(os.getenv("HF_API_KEY"))

model_name = "microsoft/Phi-3-mini-4k-instruct"
repository = "edsoncarvalhointuria/merged-schema-forg-ai"

tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForCausalLM.from_pretrained(
    model_name, dtype=torch.float16, device_map="auto"
)

path_lora = "./schema-forg-ai"
model_lora = PeftModel.from_pretrained(model, path_lora)


fusion_model = model_lora.merge_and_unload()
fusion_model.push_to_hub(repository)
tokenizer.push_to_hub(repository)
