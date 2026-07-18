import json
import os
from pathlib import Path
import time
from dotenv import load_dotenv
import random
from google import genai
from google.genai import types
from typing import Literal

load_dotenv()


def createSimpleSchemas(
    model: str,
    path_save: str,
    path_scenarios: str,
    type_schema: Literal["micro", "medium"],
):
    scenarios = []
    with open(path_scenarios, "r", encoding="utf-8") as s:
        lines = s.readlines()
        for line in lines:
            text = line.strip()
            scenarios.append(text)

    languages = ["Português do Brasil", "English"]
    prompt_base = """You are a Senior Software Architect expert in TypeScript, Zod, and RESTful API design.
Your task is to generate realistic API JSON data strictly matching the requested scenario's complexity, and output its corresponding Zod schema using the `@asteasolutions/zod-to-openapi` library.

CRITICAL RULES:
1. BATCH GENERATION: You must generate an array of exactly 3 to 5 DISTINCT variations based on the provided scenario. Vary the specific data values, lengths, and realistic contexts, but maintain the exact structural complexity requested.
2. SCOPE MATCHING (ANTI-OVERFITTING): Strictly follow the complexity of the requested scenario. If the scenario asks for a "simple" or "basic" payload, generate small, flat JSONs with 1-4 keys maximum. Do NOT invent nested objects, extra metadata, arrays, or massive payloads unless explicitly demanded.
3. ADAPTIVE MODULARITY: 
   - For simple/flat JSONs (Micro): Output a single, direct root Zod schema. Do not over-engineer or extract parts that don't need extraction.
   - For complex/nested JSONs (Macro): Analyze the structure and extract nested entities or arrays into independent `const` schemas. Build the final root schema by composing these smaller schemas.
4. OPENAPI METADATA: Every single field must have a `.openapi({ description: '...', example: ... })` method attached.
5. BILINGUAL DOCUMENTATION: JSON keys and TS variables must be in English. Write all .openapi(description) texts entirely in the requested language.
6. STRICT OUTPUT: You must respond ONLY with a valid JSON object containing a single key "examples", which holds an array of objects. Each object must have exactly two keys: "raw_json" and "zod_code". Do not use markdown formatting blocks (```json) around your response.
"""
    examples = {
        "micro": [
            """--- EXAMPLE ---
User Scenario: 'A simple user email update payload'
Output:
{
  "raw_json": {
    "user_id": "usr_992",
    "new_email": "edson@example.com"
  },
  "zod_code": "import { z } from 'zod';\nimport { extendZodWithOpenApi } from '@asteasolutions/zod-to-openapi';\n\nextendZodWithOpenApi(z);\n\nexport const EmailUpdatePayloadSchema = z.object({\n  user_id: z.string().openapi({ description: 'Identificador do usuário', example: 'usr_992' }),\n  new_email: z.string().email().openapi({ description: 'Novo endereço de email', example: 'edson@example.com' })\n}).openapi({ title: 'Atualização de Email', description: 'Payload simples para atualizar o email do usuário' });"
}""",
            """--- EXAMPLE ---
User Scenario: 'A simple delete request payload'
Output:
{
  "raw_json": {
    "item_id": "itm_404",
    "force_delete": true
  },
  "zod_code": "import { z } from 'zod';\\nimport { extendZodWithOpenApi } from '@asteasolutions/zod-to-openapi';\\n\\nextendZodWithOpenApi(z);\\n\\nexport const DeleteRequestSchema = z.object({\\n  item_id: z.string().openapi({ description: 'ID único do item a ser removido', example: 'itm_404' }),\\n  force_delete: z.boolean().openapi({ description: 'Bypass para exclusão forçada', example: true })\\n}).openapi({ title: 'Requisição de Exclusão', description: 'Payload contendo os parâmetros de deleção' });"
}""",
            """--- EXAMPLE ---
User Scenario: 'A basic feature toggle update'
Output:
{
  "raw_json": {
    "feature_name": "beta_dashboard",
    "is_enabled": false
  },
  "zod_code": "import { z } from 'zod';\\nimport { extendZodWithOpenApi } from '@asteasolutions/zod-to-openapi';\\n\\nextendZodWithOpenApi(z);\\n\\nexport const FeatureToggleSchema = z.object({\\n  feature_name: z.string().openapi({ description: 'Nome da flag do sistema', example: 'beta_dashboard' }),\\n  is_enabled: z.boolean().openapi({ description: 'Status de ativação da feature', example: false })\\n}).openapi({ title: 'Atualização de Feature', description: 'Payload para ligar ou desligar recursos' });"
}""",
            """--- EXAMPLE ---
User Scenario: 'A simple server health check response'
Output:
{
  "raw_json": {
    "status": "healthy",
    "uptime_seconds": 120500
  },
  "zod_code": "import { z } from 'zod';\\nimport { extendZodWithOpenApi } from '@asteasolutions/zod-to-openapi';\\n\\nextendZodWithOpenApi(z);\\n\\nexport const HealthCheckResponseSchema = z.object({\\n  status: z.enum(['healthy', 'degraded', 'down']).openapi({ description: 'Estado atual do servidor', example: 'healthy' }),\\n  uptime_seconds: z.number().int().openapi({ description: 'Tempo de atividade em segundos', example: 120500 })\\n}).openapi({ title: 'Status do Servidor', description: 'Resposta de integridade do sistema' });"
}""",
        ],
        "medium": [
            """--- EXAMPLE ---
User Scenario: 'A basic login response with a token and basic user info'
Output:
{
  "raw_json": {
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI...",
    "user": { "id": "usr_1", "role": "admin" }
  },
  "zod_code": "import { z } from 'zod';\nimport { extendZodWithOpenApi } from '@asteasolutions/zod-to-openapi';\n\nextendZodWithOpenApi(z);\n\nconst UserSnippetSchema = z.object({\n  id: z.string().openapi({ description: 'ID do usuário', example: 'usr_1' }),\n  role: z.enum(['admin', 'user']).openapi({ description: 'Nível de acesso', example: 'admin' })\n}).openapi({ description: 'Dados básicos do usuário logado' });\n\nexport const LoginResponseSchema = z.object({\n  access_token: z.string().openapi({ description: 'Token JWT de autenticação', example: 'eyJhbGciOiJIUzI1NiIsInR5cCI...' }),\n  user: UserSnippetSchema\n}).openapi({ title: 'Resposta de Login', description: 'Credenciais e dados do usuário após login de sucesso' });"
}""",
            """--- EXAMPLE ---
User Scenario: 'A product price update with a nested currency object'
Output:
{
  "raw_json": {
    "product_id": "prod_1",
    "pricing": {
      "amount": 19.99,
      "currency": "USD"
    }
  },
  "zod_code": "import { z } from 'zod';\\nimport { extendZodWithOpenApi } from '@asteasolutions/zod-to-openapi';\\n\\nextendZodWithOpenApi(z);\\n\\nconst PricingSchema = z.object({\\n  amount: z.number().openapi({ description: 'Valor monetário do produto', example: 19.99 }),\\n  currency: z.string().length(3).openapi({ description: 'Código da moeda (ISO 4217)', example: 'USD' })\\n}).openapi({ description: 'Estrutura de precificação' });\\n\\nexport const PriceUpdateSchema = z.object({\\n  product_id: z.string().openapi({ description: 'ID do produto', example: 'prod_1' }),\\n  pricing: PricingSchema\\n}).openapi({ title: 'Atualização de Preço', description: 'Payload de alteração de valores de catálogo' });"
}""",
            """--- EXAMPLE ---
User Scenario: 'User account with a nested settings object'
Output:
{
  "raw_json": {
    "user_id": "u_88",
    "settings": {
      "theme": "dark",
      "notifications": true
    }
  },
  "zod_code": "import { z } from 'zod';\\nimport { extendZodWithOpenApi } from '@asteasolutions/zod-to-openapi';\\n\\nextendZodWithOpenApi(z);\\n\\nconst UserSettingsSchema = z.object({\\n  theme: z.enum(['light', 'dark', 'system']).openapi({ description: 'Tema visual da interface', example: 'dark' }),\\n  notifications: z.boolean().openapi({ description: 'Opt-in de notificações push', example: true })\\n}).openapi({ description: 'Configurações de preferência do usuário' });\\n\\nexport const UserProfileSchema = z.object({\\n  user_id: z.string().openapi({ description: 'ID único do usuário', example: 'u_88' }),\\n  settings: UserSettingsSchema\\n}).openapi({ title: 'Perfil do Usuário', description: 'Objeto raiz contendo as configurações de conta' });"
}""",
            """--- EXAMPLE ---
User Scenario: 'A simple shopping cart with an array of basic items'
Output:
{
  "raw_json": {
    "cart_id": "cart_123",
    "items": [
      { "sku": "A1", "quantity": 2 }
    ]
  },
  "zod_code": "import { z } from 'zod';\\nimport { extendZodWithOpenApi } from '@asteasolutions/zod-to-openapi';\\n\\nextendZodWithOpenApi(z);\\n\\nconst CartItemSchema = z.object({\\n  sku: z.string().openapi({ description: 'Código do produto', example: 'A1' }),\\n  quantity: z.number().int().positive().openapi({ description: 'Quantidade adicionada', example: 2 })\\n}).openapi({ description: 'Item individual do carrinho' });\\n\\nexport const ShoppingCartSchema = z.object({\\n  cart_id: z.string().openapi({ description: 'Identificador da sessão do carrinho', example: 'cart_123' }),\\n  items: z.array(CartItemSchema).openapi({ description: 'Lista de produtos selecionados' })\\n}).openapi({ title: 'Carrinho de Compras', description: 'Estrutura básica de um carrinho' });"
}""",
        ],
    }

    client = genai.Client()

    def generateSchema(scenario):
        """Essa função coleta dados da azure para simulação"""
        language = random.choice(languages)
        example = random.choice(examples[type_schema])

        print("Linguagem", language)
        config = genai.types.GenerateContentConfig(
            system_instruction=f"{prompt_base} \n CRITICAL: Write ALL openapi descriptions and examples EXCLUSIVELY in {language}. \n {example}",
            temperature=0.2,
        )
        response = client.models.generate_content(
            model=model, contents=scenario, config=config
        )

        return response

    i = 0
    while True:
        print("INICIANDO")
        scenario = scenarios[i % len(scenarios)]
        try:
            result = generateSchema(scenario)
        except Exception as error:
            e = str(error)
            print(e)

            if "429" in e or "quota" in e or "exhausted" in e:
                print("ACABOU A COTA")
                break

            ("\nHouve um erro, esperando mais 10 minuto\n")
            time.sleep(1)
            continue

        with open(path_save, "a", encoding="utf-8") as path:
            text = json.dumps(result.text, ensure_ascii=False)
            path.write(text + "\n")

        time.sleep(4)
        print("ENCERRANDO", i)
        i += 1
