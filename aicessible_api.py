import json
from PROMPTS import CONFIRMATION_PROMPT, get_prompt
import logging

logger = logging.getLogger(__name__)

def get_ai_response(user_input, client, prompt_type = ""):
    system_prompt = get_prompt(prompt_type)

    response = client.chat.completions.create(
        model="gpt-4-turbo-preview",
        response_format={ "type": "json_object" },
        messages=[
            {
                "role": "system",
                "content": system_prompt
            },
            {
                "role": "user",
                "content": user_input
            }
        ],
        temperature=0.7,
        # max_tokens=64,
        top_p=1
    )
    print(response)
    content = json.loads(response.choices[0].message.content)
    print(f"User Input: {user_input}\nContent: {content}")
    logger.info(f"User Input: {user_input}\n Content: {content}")

    return content

def get_confirmation(user_input, action, user_input_history, client):
    system_prompt = CONFIRMATION_PROMPT(action)
    response = client.chat.completions.create(
        model="gpt-4-turbo-preview",
        response_format={ "type": "json_object" },
        messages=[
            {
                "role": "system",
                "content": system_prompt
            },
            {
                "role": "user",
                "content": user_input_history
            },
            {
                "role": "user",
                "content": user_input
            }
        ],
        temperature=0.7,
        # max_tokens=64,
        top_p=1,
    )

    print(response)
    content = json.loads(response.choices[0].message.content)
    print(f"User Input: {user_input}\nContent: {content}")
    logger.info(f"User Input: {user_input}\n Content: {content}")

    return content

def chat(session_id, user_input, collection, client):
    query = {"sessionId": session_id}
    document = collection.find_one(query)

    action = ""
    full_user_input = ""

    if document is None:
        action_response = get_ai_response(user_input, client, "GET_ACTION_PROMPT")
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
            action_response["status"] = "NeedDetails"
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
        ai_response = get_ai_response(full_user_input, client, "MPay")
    
    elif action == "Remittance":
        ai_response = get_ai_response(full_user_input, client, "Remittance")
    
    elif action == "Calling":
        ai_response = {"response": "Calling is not supported yet", "status": "Failed"}
    
    elif action == "Transaction": # Remove and handle as Unknown or create a specific action prompt for transactions. 
        ai_response = get_ai_response(full_user_input, client, "GET_ACTION_PROMPT")
        ai_response["status"] = "NeedDetails"
    
    elif action == "Unknown":
        ai_response = get_ai_response(full_user_input, client, "GET_ACTION_PROMPT")
        ai_response["status"] = "NeedDetails"
    
    update = {'$set': {'userInput': full_user_input, 'status': ai_response["status"]}} #, 'data': ai_response["data"]}}
    result = collection.update_one(query, update)

    return ai_response
