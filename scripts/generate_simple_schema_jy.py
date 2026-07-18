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


def createSimpleSchemasJY(
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
    prompt_base = """You are a Senior API Architect expert in OpenAPI 3.0 specifications.
Your task is to generate realistic API response data and its corresponding OpenAPI 3.0 specification in {type_example} format.

ABSOLUTE MANDATORY RULES:

1. THE GOLDEN SKELETON (CRITICAL): 
Every single OpenAPI specification you generate MUST adhere to this exact structural hierarchy. Schemas MUST ONLY exist inside `components/schemas`. NEVER place "type", "properties", or "schemas" directly at the root level.
ROOT
|-- openapi: "3.0.0"
|-- info: (title, version)
|__ components:
    |__ schemas:
        |__ [YourSchemaNameHere]: 
            type: object
            properties: ...

2. ADAPTIVE COMPLEXITY:
- SIMPLE SCENARIOS: Generate a flat JSON (1-4 keys). In the OpenAPI spec, create exactly ONE schema inside `components/schemas`. Do NOT use `$ref`. Define all properties directly inside that single schema.
- COMPLEX SCENARIOS: Generate a nested JSON. In the OpenAPI spec, extract nested objects/arrays into separate distinct schemas inside `components/schemas` and link them together using `$ref`.

3. BATCH GENERATION: Generate exactly 3 distinct variations for the requested scenario.

4. METADATA & LANGUAGE: Every property must have a `description` and `example`. JSON keys must be in English. All `description` texts MUST be written EXCLUSIVELY in {language}.

5. STRICT OUTPUT: Respond ONLY with a valid JSON string. NO markdown formatting blocks (do not use ```json). The structure must be EXACTLY:
{{
  "examples": [
    {{
      "raw_json": {{ ... }},
      "{output_key}": "..."
    }}
  ]
}}
"""
    yaml_examples = {
        "micro": [
            """--- EXAMPLE ---
    User Scenario: 'Simple system status check'
    Output:
    {
    "raw_json": { "status": "active" },
    "yaml_code": "openapi: 3.0.0\\ninfo:\\n  title: Status Response\\n  version: 1.0.0\\ncomponents:\\n  schemas:\\n    StatusResponse:\\n      type: object\\n      description: 'Current system status'\\n      properties:\\n        status:\\n          type: string\\n          description: 'System operational status'\\n          example: 'active'"
    }""",
            """--- EXAMPLE ---
    User Scenario: 'A simple email address payload'
    Output:
    {
    "raw_json": { "email": "dev@example.com" },
    "yaml_code": "openapi: 3.0.0\\ninfo:\\n  title: Email Payload\\n  version: 1.0.0\\ncomponents:\\n  schemas:\\n    EmailPayload:\\n      type: object\\n      description: 'Payload containing a user email'\\n      properties:\\n        email:\\n          type: string\\n          format: email\\n          description: 'User email address'\\n          example: 'dev@example.com'"
    }""",
            """--- EXAMPLE ---
    User Scenario: 'A simple public visibility toggle'
    Output:
    {
    "raw_json": { "is_public": true },
    "yaml_code": "openapi: 3.0.0\\ninfo:\\n  title: Visibility Toggle\\n  version: 1.0.0\\ncomponents:\\n  schemas:\\n    VisibilityToggle:\\n      type: object\\n      description: 'Toggle for content visibility'\\n      properties:\\n        is_public:\\n          type: boolean\\n          description: 'Indicates if the resource is public'\\n          example: true"
    }""",
        ],
        "medium": [
            """--- EXAMPLE ---
User Scenario: 'A user profile update request with nested contact preferences'
Output:
{
  "raw_json": {
    "user_id": "usr_9921",
    "contact_preferences": {
      "email_marketing": true,
      "sms_alerts": false
    }
  },
  "yaml_code": "openapi: 3.0.0\\ninfo:\\n  title: User Profile Update\\n  version: 1.0.0\\ncomponents:\\n  schemas:\\n    ContactPreferences:\\n      type: object\\n      description: 'User contact preferences configuration'\\n      properties:\\n        email_marketing:\\n          type: boolean\\n          description: 'Opt-in flag for promotional emails'\\n          example: true\\n        sms_alerts:\\n          type: boolean\\n          description: 'Opt-in flag for SMS text alerts'\\n          example: false\\n    UserUpdatePayload:\\n      type: object\\n      description: 'Payload for updating user settings'\\n      properties:\\n        user_id:\\n          type: string\\n          description: 'Unique identifier of the user'\\n          example: 'usr_9921'\\n        contact_preferences:\\n          $ref: '#/components/schemas/ContactPreferences'"
}""",
            """--- EXAMPLE ---
User Scenario: 'A simple shopping cart summary with an array of basic items'
Output:
{
  "raw_json": {
    "cart_id": "cart_123",
    "items": [
      { "sku": "A1", "quantity": 2 }
    ]
  },
  "yaml_code": "openapi: 3.0.0\\ninfo:\\n  title: Cart Summary\\n  version: 1.0.0\\ncomponents:\\n  schemas:\\n    CartItem:\\n      type: object\\n      description: 'Individual product item in the cart'\\n      properties:\\n        sku:\\n          type: string\\n          description: 'Product Stock Keeping Unit'\\n          example: 'A1'\\n        quantity:\\n          type: integer\\n          description: 'Number of units added'\\n          example: 2\\n    CartSummaryResponse:\\n      type: object\\n      description: 'Summary of the shopping cart session'\\n      properties:\\n        cart_id:\\n          type: string\\n          description: 'Unique session identifier for the cart'\\n          example: 'cart_123'\\n        items:\\n          type: array\\n          description: 'List of items currently in the cart'\\n          items:\\n            $ref: '#/components/schemas/CartItem'"
}""",
            """--- EXAMPLE ---
User Scenario: 'A product price update with a nested pricing currency object'
Output:
{
  "raw_json": {
    "product_id": "prod_88291",
    "pricing": {
      "amount": 29.99,
      "currency": "USD"
    }
  },
  "yaml_code": "openapi: 3.0.0\\ninfo:\\n  title: Product Price Update\\n  version: 1.0.0\\ncomponents:\\n  schemas:\\n    PricingDetails:\\n      type: object\\n      description: 'Nested pricing details'\\n      properties:\\n        amount:\\n          type: number\\n          format: float\\n          description: 'The new unit price of the product'\\n          example: 29.99\\n        currency:\\n          type: string\\n          description: 'ISO 4217 currency code'\\n          example: 'USD'\\n    PriceUpdatePayload:\\n      type: object\\n      description: 'Payload for updating a product price'\\n      properties:\\n        product_id:\\n          type: string\\n          description: 'Unique identifier of the product'\\n          example: 'prod_88291'\\n        pricing:\\n          $ref: '#/components/schemas/PricingDetails'"
}""",
        ],
    }

    json_examples = {
        "micro": [
            """--- EXAMPLE ---
    User Scenario: 'Simple system status check'
    Output:
    {
    "raw_json": { "status": "active" },
    "json_schema_code": "{\\n  \\"openapi\\": \\"3.0.0\\",\\n  \\"info\\": { \\"title\\": \\"Status Response\\", \\"version\\": \\"1.0.0\\" },\\n  \\"components\\": {\\n    \\"schemas\\": {\\n      \\"StatusResponse\\": {\\n        \\"type\\": \\"object\\",\\n        \\"description\\": \\"Current system status\\",\\n        \\"properties\\": {\\n          \\"status\\": { \\"type\\": \\"string\\", \\"description\\": \\"System operational status\\", \\"example\\": \\"active\\" }\\n        }\\n      }\\n    }\\n  }\\n}"
    }""",
            """--- EXAMPLE ---
    User Scenario: 'A simple email address payload'
    Output:
    {
    "raw_json": { "email": "dev@example.com" },
    "json_schema_code": "{\\n  \\"openapi\\": \\"3.0.0\\",\\n  \\"info\\": { \\"title\\": \\"Email Payload\\", \\"version\\": \\"1.0.0\\" },\\n  \\"components\\": {\\n    \\"schemas\\": {\\n      \\"EmailPayload\\": {\\n        \\"type\\": \\"object\\",\\n        \\"description\\": \\"Payload containing a user email\\",\\n        \\"properties\\": {\\n          \\"email\\": { \\"type\\": \\"string\\", \\"format\\": \\"email\\", \\"description\\": \\"User email address\\", \\"example\\": \\"dev@example.com\\" }\\n        }\\n      }\\n    }\\n  }\\n}"
    }""",
            """--- EXAMPLE ---
    User Scenario: 'A simple public visibility toggle'
    Output:
    {
    "raw_json": { "is_public": true },
    "json_schema_code": "{\\n  \\"openapi\\": \\"3.0.0\\",\\n  \\"info\\": { \\"title\\": \\"Visibility Toggle\\", \\"version\\": \\"1.0.0\\" },\\n  \\"components\\": {\\n    \\"schemas\\": {\\n      \\"VisibilityToggle\\": {\\n        \\"type\\": \\"object\\",\\n        \\"description\\": \\"Toggle for content visibility\\",\\n        \\"properties\\": {\\n          \\"is_public\\": { \\"type\\": \\"boolean\\", \\"description\\": \\"Indicates if the resource is public\\", \\"example\\": true }\\n        }\\n      }\\n    }\\n  }\\n}"
    }""",
        ],
        "medium": [
            """--- EXAMPLE ---
User Scenario: 'A basic weather widget response with nested metrics'
Output:
{
  "raw_json": {
    "city": "São Paulo",
    "metrics": {
      "temperature": 22.5,
      "humidity": 65
    }
  },
  "json_schema_code": "{\\n  \\"openapi\\": \\"3.0.0\\",\\n  \\"info\\": { \\"title\\": \\"Weather Widget\\", \\"version\\": \\"1.0.0\\" },\\n  \\"components\\": {\\n    \\"schemas\\": {\\n      \\"WeatherMetrics\\": {\\n        \\"type\\": \\"object\\",\\n        \\"description\\": \\"Detailed climatic metrics\\",\\n        \\"properties\\": {\\n          \\"temperature\\": { \\"type\\": \\"number\\", \\"description\\": \\"Current temperature in Celsius\\", \\"example\\": 22.5 },\\n          \\"humidity\\": { \\"type\\": \\"integer\\", \\"description\\": \\"Relative air humidity percentage\\", \\"example\\": 65 }\\n        }\\n      },\\n      \\"WeatherResponse\\": {\\n        \\"type\\": \\"object\\",\\n        \\"description\\": \\"Basic response containing city and weather metrics\\",\\n        \\"properties\\": {\\n          \\"city\\": { \\"type\\": \\"string\\", \\"description\\": \\"Queried city name\\", \\"example\\": \\"São Paulo\\" },\\n          \\"metrics\\": { \\"$ref\\": \\"#/components/schemas/WeatherMetrics\\" }\\n        }\\n      }\\n    }\\n  }\\n}"
}""",
            """--- EXAMPLE ---
User Scenario: 'A blog post comment payload with nested author details'
Output:
{
  "raw_json": {
    "post_id": "post_55",
    "author": { "id": "u_9", "name": "Edson" },
    "content": "Great article!"
  },
  "json_schema_code": "{\\n  \\"openapi\\": \\"3.0.0\\",\\n  \\"info\\": { \\"title\\": \\"Blog Comment\\", \\"version\\": \\"1.0.0\\" },\\n  \\"components\\": {\\n    \\"schemas\\": {\\n      \\"CommentAuthor\\": {\\n        \\"type\\": \\"object\\",\\n        \\"description\\": \\"Snippet of the comment author details\\",\\n        \\"properties\\": {\\n          \\"id\\": { \\"type\\": \\"string\\", \\"description\\": \\"Author user ID\\", \\"example\\": \\"u_9\\" },\\n          \\"name\\": { \\"type\\": \\"string\\", \\"description\\": \\"Author display name\\", \\"example\\": \\"Edson\\" }\\n        }\\n      },\\n      \\"CommentPayload\\": {\\n        \\"type\\": \\"object\\",\\n        \\"description\\": \\"Payload for submitting a new blog post comment\\",\\n        \\"properties\\": {\\n          \\"post_id\\": { \\"type\\": \\"string\\", \\"description\\": \\"ID of the target blog post\\", \\"example\\": \\"post_55\\" },\\n          \\"content\\": { \\"type\\": \\"string\\", \\"description\\": \\"The text content of the comment\\", \\"example\\": \\"Great article!\\" },\\n          \\"author\\": { \\"$ref\\": \\"#/components/schemas/CommentAuthor\\" }\\n        }\\n      }\\n    }\\n  }\\n}"
}""",
            """--- EXAMPLE ---
User Scenario: 'A server error response containing an error code and a simple array of error messages'
Output:
{
  "raw_json": {
    "error_code": "VALIDATION_FAILED",
    "messages": ["Invalid email", "Password too short"]
  },
  "json_schema_code": "{\\n  \\"openapi\\": \\"3.0.0\\",\\n  \\"info\\": { \\"title\\": \\"Error Response\\", \\"version\\": \\"1.0.0\\" },\\n  \\"components\\": {\\n    \\"schemas\\": {\\n      \\"ErrorPayload\\": {\\n        \\"type\\": \\"object\\",\\n        \\"description\\": \\"Standardized error response block\\",\\n        \\"properties\\": {\\n          \\"error_code\\": { \\"type\\": \\"string\\", \\"description\\": \\"High-level error classification\\", \\"example\\": \\"VALIDATION_FAILED\\" },\\n          \\"messages\\": {\\n            \\"type\\": \\"array\\",\\n            \\"description\\": \\"List of specific error descriptions\\",\\n            \\"items\\": { \\"type\\": \\"string\\", \\"description\\": \\"Individual error detail string\\", \\"example\\": \\"Invalid email\\" }\\n          }\\n        }\\n      }\\n    }\\n  }\\n}"
}""",
        ],
    }

    examples = {"YAML": yaml_examples, "JSON": json_examples}
    client = genai.Client()

    def generateSchema(scenario, type_example):
        """Essa função coleta dados da azure para simulação"""
        language = random.choice(languages)
        example = random.choice(examples[type_example][type_schema])
        if type_example == "JSON":
            key_example = "json_schema_code"
        else:
            key_example = "yaml_code"

        print("Linguagem", language)
        config = genai.types.GenerateContentConfig(
            system_instruction=prompt_base.format(
                type_example=type_example, language=language, output_key=key_example
            )
            + f"\n{example}",
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
        if i % 2 == 0:
            type_example = "JSON"
        else:
            type_example = "YAML"
        try:
            result = generateSchema(scenario=scenario, type_example=type_example)

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
