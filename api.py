from dotenv import load_dotenv
import os
from openai import OpenAI
import re
import json

OPENAI_API_KEY=""
OPENAI_BASE_URL=""

LLAMA_API_KEY=""
LLAMA_BASE_URL=""


def extract_gpt_content(message):
    # json_pattern = re.compile(r'```json\n([\s\S]*?)\n```', re.DOTALL)
    # match = json_pattern.search(message)
    # if match:
    #     try:
    #         json_str = match.group(1).strip('```').strip()
    #         data = eval(json_str)
    #         return data
    #     except json.JSONDecodeError:
    #         # 如果 JSON 解析失败，返回 None
    #         return None
        
    text_no_comments = re.sub(r'//.*', '', message)
    dict_match = re.search(r'\{[^{}]*\}', text_no_comments)

    if dict_match:
        try:
            dict_str = dict_match.group(0)
            data = eval(dict_str)
            if 'answer' not in data:
                # print(1)
                return None
            else:
                if data['answer'] not in ['A','B', 'N/S','I/E','J/P','T/F']:
                    # print(2)
                    return None
                else:
                    # print(data)
                    return data
        except Exception as e:
            print(f"Failed to parse dictionary: {e}")
            return None
    return None

def extract_llama_content(message):
    pattern = r"(?:'answer'|\"answer\"|answer)\s*:\s*(?:'([^']*)'|\"([^\"]*)\")"
    matches = re.findall(pattern, message)
    if matches:
        try:
            if matches[0][0] not in ['A','B', 'N/S','I/E','J/P','T/F']:
                    return None
            else:
                return {'answer': matches[0][0]}
        except Exception as e:
            # print(f"Failed to parse dictionary: {e}")
            # print(message)
            return None
    return None

def get_response(content : str, model : str, temperature):
    # if 'gpt' in model:
    #     client = OpenAI(
    #         api_key = OPENAI_API_KEY,
    #         base_url = OPENAI_BASE_URL,
    #     )
    # elif 'qwen' in model:
    #     client = OpenAI(
    #         api_key = QWEN_API_KEY,
    #         base_url = QWEN_BASE_URL,
    #     )
    # elif 'llama' in model:
    #     client = OpenAI(
    #         api_key = LLAMA_API_KEY,
    #         base_url = LLAMA_BASE_URL,
    #     )

    # else:
    #     raise ValueError(f"Unsupported model: {model}")
    if 'llama' in model:
        client = OpenAI(
            api_key = LLAMA_API_KEY,
            base_url = LLAMA_BASE_URL,
        )
    else:
        client = OpenAI(
                api_key = OPENAI_API_KEY,
                base_url = OPENAI_BASE_URL,
            )
    completion = client.chat.completions.create(
        # model="gpt-5-chat-latest",
        model = model,
        messages=[
            {"role": "user", "content": content}
        ],
        temperature = temperature,
    )
    response = completion.choices[0].message.content

    if 'gpt' in model:
        return extract_gpt_content(response)
    elif 'gemini' in model:
        return extract_gpt_content(response)
    elif 'llama' in model:
        return extract_llama_content(response)

    