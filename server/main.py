from fastapi import FastAPI, APIRouter, HTTPException
from database.configurations import collection, db
from database.schemas import all_chats, individual_chat
from bson import ObjectId
from database.models import Chat, Message, MessageInput
from dotenv import load_dotenv
from agent.default_agent import app as agent_app

# carrega o .env
load_dotenv()

app = FastAPI()
router = APIRouter()

@router.get("/chats")
async def get_all_chats():
    data = collection.find()
    return all_chats(data)

@router.get("/chat/{chat_id}")
async def get_chat(chat_id: str):
    try:
        obj_id = ObjectId(chat_id)
    except Exception:
        raise HTTPException(status_code=400, detail="ID de chat inválido")

    data = collection.find_one({"_id": obj_id})
    if not data:
        raise HTTPException(status_code=404, detail="Chat não encontrado")

    return individual_chat(data)

@router.post("/criar-chat")
async def create_chat(new_chat: Chat):
    try:
        # Converte o Pydantic model inteiro em dict serializável
        chat_dict = new_chat.model_dump()
        resp = collection.insert_one(chat_dict)
        return {"status_code": 200, "message": "Chat criado com sucesso!", "_id": str(resp.inserted_id)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ocorreu um erro ao criar o chat: {e}")
    
@router.get("/chat-messages/{chat_id}", response_model=list[Message])
async def get_chat_messages(chat_id: str):
    try:
        obj_id = ObjectId(chat_id)
    except Exception:
        raise HTTPException(status_code=400, detail="ID de chat inválido")

    chat = collection.find_one({"_id": obj_id})
    if not chat:
        raise HTTPException(status_code=404, detail="Chat não encontrado")

    return chat.get("messages", [])
    
@router.post("/send-user/{chat_id}")
async def send_message(chat_id: str, message: MessageInput):
    try:
        chat = collection.find_one({"_id": ObjectId(chat_id)})
        # calcular próximo id
        next_id = len(chat.get("messages", [])) + 1
        collection.update_one(
            {"_id": ObjectId(chat_id)}, 
            {"$push": {"messages": {"id": next_id, "text": message.text, "sender": "user"}}}
        )
        return {"status_code": 200, "message": "Mensagem enviada com sucesso!"}
    except Exception:
        raise HTTPException(status_code=404, detail="Chat não encontrado")

@router.post("/send-model/{chat_id}")
async def send_model(chat_id: str):    
    chat = collection.find_one({"_id": ObjectId(chat_id)})
    if not chat:
        raise HTTPException(status_code=404, detail="Chat não encontrado")

    # 1. Monta estado 
    state = {
        "messages": chat.get("messages", []),
        "triagem": chat.get("triagem", {}),
        "resumo_confirmado": chat.get("resumo_confirmado", False),
        "emergency_detected": chat.get("emergency_detected", False),
        "turn_count": chat.get("turn_count", 0) 
    }
    
    # 2. Executa LangGraph usando STREAM para rodar APENAS UM TURNO
    final_state = state.copy()

    for s in agent_app.stream(state):
        final_state.update(s)
        
        # Interrompe o ciclo após o primeiro ciclo completo, ou se atingir END
        if "__end__" in s or "end_or_continue" in s or "emergency_protocol" in s: 
            break
            
    updated_state = final_state

    # Encontra a chave do último nó que executou 
    last_node_key = [k for k in final_state if k not in state][0] if [k for k in final_state if k not in state] else None

    if last_node_key:
        state_from_last_node = final_state[last_node_key]
        updated_state["messages"] = state_from_last_node.get("messages", [])
        updated_state["triagem"] = state_from_last_node.get("triagem", {})
        updated_state["resumo_confirmado"] = state_from_last_node.get("resumo_confirmado", False)
        updated_state["emergency_detected"] = state_from_last_node.get("emergency_detected", False)
        updated_state["turn_count"] = state_from_last_node.get("turn_count", 0)

    # 3. Prepara os dados de atualização para o DB
    is_confirmed = updated_state.get("resumo_confirmado", False)
    is_emergency = updated_state.get("emergency_detected", False)
    
    update_fields = {
        "messages": updated_state.get("messages", []),
        "triagem": updated_state.get("triagem", {}),
        "resumo_confirmado": is_confirmed,
        "emergency_detected": is_emergency,
        "turn_count": updated_state.get("turn_count", 0),
        "is_completed": False
    }

    # 4. Lógica de Salvamento Final
    if is_confirmed:
        print("DEBUG 4.1 - CONDIÇÃO ATINGIDA: is_confirmed é True. Salvando conclusão!")
        
        # Se a triagem foi confirmada (pelo usuário ou emergência), salva os campos de conclusão
        update_fields["is_completed"] = True
        
        update_fields["triagem"] = updated_state.get("triagem", {}) 
        
        if is_emergency:
            update_fields["status"] = "EMERGENCY_ALERT"
        else:
            update_fields["status"] = "TRIAGE_COMPLETED"
    else:
        print("DEBUG 4.1 - CONDIÇÃO IGNORADA: is_confirmed é False. Continua a triagem.")

    collection.update_one(
        {"_id": ObjectId(chat_id)},
        {"$set": update_fields}
    )

    # 5. Retorna a última mensagem do agente
    agent_message = updated_state["messages"][-1]
        
    return {
        "status_code": 200,
        "agent_message": agent_message
    }

@router.delete("/apagar-tudo")
async def delete_all_data():
    try:
        # apaga todos os documentos de todas as coleções
        for collection_name in db.list_collection_names():
            db[collection_name].delete_many({})
        return {"status": "sucesso", "message": "Todos os dados foram apagados!"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao apagar dados: {e}")

app.include_router(router)
