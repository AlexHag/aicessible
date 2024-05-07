import sys
import os
from openai import OpenAI
import json
from PROMPTS import GET_ACTION_PROMPT, MPAY_PROMPT
from pymongo import MongoClient

def get_action(user_input, client):
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

def mpay_action(user_input, client):
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

    return content

def chat(session_id, user_input, collection, client):
    query = {"sessionId": session_id}
    document = collection.find_one(query)

    action = ""
    full_user_input = ""

    if document is None:
        action_response = get_action(user_input, client)
        document = {
                "sessionId": session_id,
                "action": action_response["action"],
                "userInput": user_input
            }
        collection.insert_one(document)
        action = action_response["action"]
        full_user_input = user_input
    else:
        action = document["action"]
        full_user_input = document["userInput"] + " " + user_input
        update = {'$set': {'userInput': full_user_input}}
        result = collection.update_one(query, update)

    if action == "MPay":
        return mpay_action(full_user_input, client)

    if action == "Remittance":
        return {"response": "Remittance is not supported yet", "status": "failed"}

    if action == "Calling":
        return {"response": "Calling is not supported yet", "status": "failed"}

    if action == "Transaction":
        action_response["status"] = "NeedDetails"
        return action_response

    action_response["status"] = "NeedDetails"
    return action_response
