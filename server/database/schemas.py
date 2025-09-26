from bson import ObjectId

def individual_chat(chat):
    messages = chat.get("messages", [])  # lista de mensagens
    last_message = messages[-1]["text"] if messages else None

    return {
        "chat_id": str(chat["_id"]),  # converte ObjectId em string
        "title": chat.get("title"),
        "is_completed": chat.get("is_completed", False),
        "creation": chat.get("creation"),
        "lastMessage": last_message,
        "triagem": chat.get("triagem", {}),
    }

def all_chats(chats):
    return [individual_chat(chat) for chat in chats]

