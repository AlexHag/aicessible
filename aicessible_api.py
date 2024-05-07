import sys
import os
from openai import OpenAI
import json
from PROMPTS import GET_ACTION_PROMPT, MPAY_PROMPT, get_confirmation_prompt
from pymongo import MongoClient
import logging

logger = logging.getLogger(__name__)

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
    logger.info(f"User Input: {user_input}\n Content: {content}")

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
    logger.info(f"User Input: {user_input}\n Content: {content}")

    return content

def get_confirmation(user_input, action, user_input_history, client):
    system_prompt = get_confirmation_prompt(action, user_input)
    response = client.chat.completions.create(
        model="gpt-4-turbo",
        response_format={ "type": "json_object" },
        messages=[
            {
                "role": "system",
                "content": system_prompt
            },
            {
                "role": "user",
                "content": user_input_history
            }
        ],
        temperature=0.7,
        max_tokens=64,
        top_p=1,
    )

    content = json.loads(response.choices[0].message.content)
    logger.info(f"User Input: {user_input}\n Content: {content}")

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
                "userInput": user_input,
                "status": "NeedDetails"
            }
        collection.insert_one(document)
        action = action_response["action"]
        full_user_input = user_input

        if action == "Transaction" or action == "Unknown":
            return action_response

    else:
        action = document["action"]
        full_user_input = document["userInput"] + " " + user_input

        if document["status"] == "Accepted":
            ai_response = get_confirmation(user_input, action, document["userInput"], client)
            update = {'$set': {'userInput': full_user_input, 'status': ai_response["status"]}}
            result = collection.update_one(query, update)
            return ai_response

    ai_response = None

    if action == "MPay":
        ai_response = mpay_action(full_user_input, client)
    elif action == "Remittance":
        ai_response = {"response": "Remittance is not supported yet", "status": "Failed"}
    elif action == "Calling":
        ai_response = {"response": "Calling is not supported yet", "status": "Failed"}
    elif action == "Transaction":
        ai_response = get_action(full_user_input, client)
        ai_response["status"] = "NeedDetails"
    elif action == "Unknown":
        ai_response = get_action(full_user_input, client)
        ai_response["status"] = "NeedDetails"
    
    update = {'$set': {'userInput': full_user_input, 'status': ai_response["status"]}}
    result = collection.update_one(query, update)

    return ai_response
