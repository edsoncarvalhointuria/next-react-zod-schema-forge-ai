from huggingface_hub import login
from datasets import load_dataset
from dotenv import load_dotenv
import os

load_dotenv()

archives = {
    "train": "./train.jsonl",
    "test": "./test.jsonl",
}

login(token=os.getenv("HF_API_KEY"))

dataset = load_dataset("json", data_files=archives)
dataset.push_to_hub(
    "edsoncarvalhointuria/erp-schema-forg-dataset",
    commit_message="subindo arquivos iniciais",
)
