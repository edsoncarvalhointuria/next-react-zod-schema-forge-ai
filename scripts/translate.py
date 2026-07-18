import json
from typing import Literal
import pandas as pd
from sklearn import model_selection
import re
from huggingface_hub import login
from datasets import load_dataset
from dotenv import load_dotenv
import os
from pathlib import Path

load_dotenv()
data_path = Path.cwd() / "data"

system_messages = {
    "zod": "Você é um Engenheiro de Software Sênior especialista em TypeScript. Sua tarefa é receber um objeto JSON bruto e gerar o código TypeScript correspondente utilizando a biblioteca 'zod' estendida com '@asteasolutions/zod-to-openapi'. Reflita a complexidade exata do JSON: mantenha esquemas em um único bloco para dados planos, e extraia sub-esquemas modulares apenas para estruturas aninhadas reais. Inclua descrições e exemplos OpenAPI. Retorne APENAS o código TypeScript cru, sem formatação markdown (```typescript) e sem explicações.",
    "yaml": "Você é um Arquiteto de Software especialista em documentação de APIs. Converta o JSON de entrada em uma especificação OpenAPI 3.0 em formato YAML. Aloque os modelos em 'components/schemas'. Respeite a profundidade do dado: não crie referências ($ref) internas desnecessárias para objetos simples, utilizando a extração apenas para dados aninhados. Retorne APENAS o código YAML cru, sem formatação markdown e sem explicações adicionais.",
    "json": "Você é um Arquiteto de Software especialista em documentação de APIs. Converta o JSON de entrada em uma especificação OpenAPI 3.0 estruturada em formato JSON. Aloque os modelos em 'components/schemas'. Respeite a profundidade do dado: não crie referências ($ref) internas desnecessárias para objetos simples, utilizando a extração apenas para dados aninhados. Retorne APENAS o código JSON cru, sem formatação markdown e sem explicações adicionais.",
}


login(token=os.getenv("HF_API_KEY"))


regex = r"([^\\])\\'"
sub = r"\1\\\'"


def getFineTurningObject(
    type: Literal["zod", "yaml", "json"], user: dict, assistant: dict
):
    return {
        "type": type,
        "system": system_messages[type],
        "user": json.dumps(user),
        "assistant": assistant,
    }


with open(data_path / "fine_turning.jsonl", "a", encoding="utf-8") as final_archive:

    regex = r"([^\\])\\'"
    sub = r"\1\\\'"
    with open(data_path / "zod.jsonl", "r", encoding="utf-8") as zod:
        for i, line in enumerate(zod):
            item = json.loads(re.sub(regex, sub, json.loads(line)))
            obj = getFineTurningObject("zod", item["raw_json"], item["zod_code"])
            formated_obj = json.dumps(obj, ensure_ascii=False)

            final_archive.write(formated_obj + "\n")
    with open(data_path / "zod_simple.jsonl", "r", encoding="utf-8") as simple_zod:
        for i, line in enumerate(simple_zod):
            list = json.loads(json.loads(line))["examples"]

            for item in list:
                obj = getFineTurningObject("zod", item["raw_json"], item["zod_code"])
                formated_obj = json.dumps(obj, ensure_ascii=False)
                final_archive.write(formated_obj + "\n")
    print("passei do zod")
    with open(data_path / "json_and_yml.jsonl", "r", encoding="utf-8") as jy:
        for i, line in enumerate(jy):
            item = json.loads(
                re.sub(
                    regex,
                    sub,
                    json.loads(line)
                    .replace('\\"components\\": {}', "")
                    .replace('\\"paths\\": {}', "")
                    .replace('\\"schemas\\": {}', ""),
                ),
                strict=False,
            )

            if item["openapi_spec"].startswith("{"):
                type = "json"
            else:
                type = "yaml"

            obj = getFineTurningObject(type, item["raw_json"], item["openapi_spec"])
            formated_obj = json.dumps(obj, ensure_ascii=False)
            final_archive.write(formated_obj + "\n")

    with open(data_path / "jy_simple.jsonl", "r", encoding="utf-8") as simple_jy:
        for line in simple_jy:
            list = json.loads(json.loads(line))["examples"]

            for item in list:
                if item.get("json_schema_code"):
                    type = "json"
                    key = "json_schema_code"
                else:
                    type = "yaml"
                    key = "yaml_code"
                obj = getFineTurningObject(type, item["raw_json"], item[key])
                formated_obj = json.dumps(obj, ensure_ascii=False)
                final_archive.write(formated_obj + "\n")

df = pd.read_json(data_path / "fine_turning.jsonl", lines=True)

df_train, df_test = model_selection.train_test_split(
    df, test_size=0.10, stratify=df["type"], random_state=42
)

df_train.drop(columns=["type"], inplace=True)
df_test.drop(columns=["type"], inplace=True)

df_train.to_json(
    data_path / "train.jsonl", orient="records", lines=True, force_ascii=False
)
df_test.to_json(
    data_path / "test.jsonl", orient="records", lines=True, force_ascii=False
)
