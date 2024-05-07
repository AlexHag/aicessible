import sys
import os
from openai import OpenAI
import json
from PROMPTS import GET_ACTION_PROMPT, MPAY_PROMPT

client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

def get_action(user_input):
    response = client.chat.completions.create(
        model="gpt-4-turbo",
        response_format={ "type": "json_object" },
        messages=[
            {
                "role": "system",
                "content": GET_ACTION_PROMPT
            },
            {
                "role": "user",
                "content": user_input
            }
        ],
        temperature=0.7,
        max_tokens=64,
        top_p=1
    )

    content = json.loads(response.choices[0].message.content)
    print(f"User Input: {user_input}\n Content: {content}")

    return content

def mpay_action(user_input):
    
    response = client.chat.completions.create(
        model="gpt-4-turbo",
        response_format={ "type": "json_object" },
        messages=[
            {
                "role": "system",
                "content": MPAY_PROMPT
            },
            {
                "role": "user",
                "content": user_input
            }
        ],
        temperature=0.7,
        max_tokens=64,
        top_p=1,
    )

    content = json.loads(response.choices[0].message.content)
    print(f"User Input: {user_input}\n Content: {content}")

    if content["status"] == "needDetails":
        user_input += input(content["response"])
        content = mpay_action(user_input)
        return content
    
    if content["status"] == "unknown":
        print(content["response"])
        sys.exit(1)

    return content

def main(user_input):
    action = get_action(user_input)

    if action["action"] == "Unknown":
        print("Unknonw action")
        sys.exit(1)
    
    if action["action"] == "MPay":
        response = mpay_action(user_input)
        return response
    
    if action["action"] == "transaction":
        user_input += input(action["response"])
        response = main(user_input)
        return response
    
    if action["action"] == "Remittance":
        print("Remittance is not supported yet")
        sys.exit(1)

    if (action["action"] == "Calling"):
        print("Calling is not supported yet")
        sys.exit(1)

    return response


if __name__ == "__main__":
    user_input = input("What would you like to do: ")
    response = main(user_input)
    print(response)