import os
import json
from typing import TypedDict, List, Dict, Any
from langgraph.graph import StateGraph, END
from google import genai
from bson import ObjectId
from database.configurations import collection
from database.models import State

# --- CONSTANTES DE CONFIGURAÇÃO ---
MODEL_NAME = "gemini-2.5-flash-lite"
EMERGENCY_KEYWORDS = [
    # Cardiovasculares
    "dor no peito", "pressão no peito", "dor no coração", "taquicardia", "palpitação forte",
    
    # Respiratórios
    "falta de ar", "dificuldade para respirar", "respiração curta", "chiado no peito", "não consigo respirar", "engasguei",
    
    # Neurológicos
    "desmaio", "perda de consciência", "não consigo falar", "fraqueza de um lado do corpo", "formigamento súbito",
    
    # Hemorragia / Trauma
    "sangramento intenso", "sangramento que não para", "muito sangue", "hemorragia", "corte profundo", "acidente grave",
    
    # Outros críticos
    "parada cardiaca", "parada respiratória", "sem pulso", "convulsão", "ataque epiléptico", "choque elétrico"
]
# -------------------------------
# 1. Prompt do agente 
# -------------------------------
SYSTEM_PROMPT = f"""
Você é o assistente virtual da ClinicAI. Sua missão é conduzir uma triagem inicial:
1. Comece se apresentando, deixando claro que você coleta informações para agilizar a consulta e NÃO substitui o diagnóstico médico.
2. Colete sistematicamente as informações-chave: Queixa Principal, Sintomas Detalhados, Duração/Frequência, Intensidade (0-10), Histórico Relevante e Medidas Tomadas.
3. Ponto de Conclusão OBRIGATÓRIO: Quando sentir que TODOS os campos em 'triagem_data' estão preenchidos, você DEVE gerar um RESUMO COMPLETO de todas as informações coletadas no campo `next_response` e terminar perguntando ao usuário: "As informações acima estão corretas, e podemos encerrar a triagem e salvar os dados?"
4. NÃO forneça diagnósticos, tratamentos, nem sugestões médicas.

A sua SAÍDA DEVE SER SEMPRE UM OBJETO JSON VÁLIDO, contendo APENAS dois campos:
- "next_response": Sua resposta em linguagem natural para o usuário.
- "triagem_data": Um objeto com os dados estruturados da triagem.

O FORMATO JSON OBRIGATÓRIO é:
{{
 "next_response": "Sua próxima pergunta, ou resumo/pergunta de confirmação.",
 "triagem_data": {{
 "queixa_principal":"",
 "sintomas_detalhados":"",
 "duracao_frequencia":"",
 "intensidade":"",
 "historico_relevante":"",
 "medidas_tomadas":"",
 "emergency_alert": false
 }}
}}
Se o usuário mencionou sintomas de emergência, defina 'emergency_alert': true.
"""

# -------------------------------
# 2. Inicialização do Cliente
# -------------------------------
llm = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))

# ----------------------------------------------------
# 3. Funções Auxiliares e Nodos
# ----------------------------------------------------

def clean_json_string(text: str) -> str:
    """Limpa a string de resposta do LLM, removendo wrappers Markdown e texto extra."""
    text = text.strip()
    if text.startswith("```json"):
        text = text[7:]
    if text.endswith("```"):
        text = text[:-3]
    return text.strip()

def chatbot_node(state: State):
    """
    Nó principal: Interage, gera resposta, extrai triagem, e atualiza o estado em UMA CHAMADA.
    """
    messages = state.get("messages", [])

    # 1. VERIFICAÇÃO DE CONFIRMAÇÃO (CHECA A ÚLTIMA MENSAGEM DO USUÁRIO)
    last_user_input = messages[-1].get("text", "").lower()
    confirmation_keywords = ["sim", "confirmo", "correto", "pode salvar", "pode terminar"]
    user_confirmed_summary = any(kw in last_user_input for kw in confirmation_keywords)
    
    # 2. DECIDE O PROMPT A SER ENVIADO
    forced_instruction = ""
    new_resumo_confirmado = state.get("resumo_confirmado", False) 
    
    if user_confirmed_summary and not new_resumo_confirmado:
        # Se o usuário confirmou e ainda não tinha a flag, a mensagem final é forçada
        forced_instruction = (
            "\n\n INSTRUÇÃO DE FLUXO: O usuário CONFIRMOU o resumo na última mensagem. "
            "Sua ÚNICA TAREFA agora é gerar a mensagem final para o usuário no 'next_response': "
            "'Ótimo! Sua triagem foi concluída com sucesso e os dados foram salvos para a sua consulta. Obrigado por usar o ClinicAI.'. "
            "O grafo será encerrado após esta resposta. O JSON 'triagem_data' deve refletir o estado final do resumo."
        )
        new_resumo_confirmado = True # Marca a flag
    
    # Cria o histórico de mensagens para enviar ao LLM
    prompt_history = "\n".join([f"{msg.get('sender', 'user')}: {msg.get('text', '')}" for msg in messages])
    
    # Adiciona a instrução do sistema e a instrução forçada, se houver
    full_prompt = SYSTEM_PROMPT + forced_instruction + "\n\nHISTÓRICO DA CONVERSA:\n" + prompt_history

    # --- INÍCIO DA ÚNICA CHAMADA DE API ---
    response_text = ""
    try:
        response = llm.models.generate_content(
            model=MODEL_NAME, 
            contents=[{"role": "user", "parts": [{"text": full_prompt}]}]
        )
        response_text_raw = clean_json_string(response.text)
        
        # Tenta decodificar o JSON único
        response_data = json.loads(response_text_raw) 
        
        response_text = response_data.get("next_response", "Desculpe, não consegui gerar a próxima resposta.")
        triagem = response_data.get("triagem_data", state.get("triagem", {})) 
        
    except Exception as e:
        # Mantém a triagem anterior em caso de falha.
        print(f"Erro na ÚNICA CHAMADA DE API/Parsing de JSON: {e}. Retorno bruto: {response_text_raw if 'response_text_raw' in locals() else 'N/A'}")
        response_text = "Houve um erro no processamento. Por favor, tente novamente."
        triagem = state.get("triagem", {}) 
    # --- FIM DA ÚNICA CHAMADA DE API ---

    # 3. Adiciona a resposta do agente ao histórico
    messages.append({"id": len(messages) + 1, "text": response_text, "sender": "model"})

    # 4. Atualiza flags (emergency_detected)
    emergency_detected = triagem.get("emergency_alert", False) or state.get("emergency_detected", False)
    
    # Adiciona o contador de turnos
    new_turn_count = state.get("turn_count", 0) + 1

    return {
        "messages": messages,
        "triagem": triagem,
        "resumo_confirmado": new_resumo_confirmado,
        "emergency_detected": emergency_detected,
        "turn_count": new_turn_count 
    }

def emergency_protocol(state: State):
    """
    Nó de parada: Envia a mensagem de alerta e força o fim da triagem.
    """
    alert_message = (
        "🚨 **ALERTA DE EMERGÊNCIA** 🚨\n\n"
        "Entendi. Seus sintomas podem indicar uma situação de emergência. "
        "Por favor, **interrompa esta conversa** e procure o pronto-socorro mais próximo ou ligue para o **192** (SAMU) imediatamente."
    )
    
    messages = state["messages"] + [{"id": len(state["messages"]) + 1, "text": alert_message, "sender": "model"}]

    return {
        "messages": messages,
        "emergency_detected": True, 
        "resumo_confirmado": True,
        "turn_count": state.get("turn_count", 0)
    }

def router_emergency(state: State) -> str:
    last_user_message = state["messages"][-1].get("text", "").lower()
    
    if any(kw in last_user_message for kw in EMERGENCY_KEYWORDS):
        return "emergency"
    
    if state.get("emergency_detected"):
        return "emergency"
        
    return "continue_triage"

def router_end(state: State) -> str:
    """Roteia para o nó de salvamento se o resumo for confirmado, ou volta para a triagem.
    Adiciona uma condição de segurança para o contador de turnos.
    """
    # Condição 1: Confirmação do resumo (principal)
    if state.get("resumo_confirmado"):
        return "save_and_end"
    
    # Condição 2 (Segurança): Limite de turnos alcançado
    if state.get("turn_count", 0) >= 15: 
        print(f"AVISO: LangGraph atingiu o limite de turnos ({state['turn_count']}). Forçando encerramento.")
        state["resumo_confirmado"] = True 
        return "save_and_end"
        
    return "continue_triage"

# ----------------------------------------------------
# 4. CONFIGURAÇÃO DO GRAFO 
# ----------------------------------------------------

graph = StateGraph(State)

graph.add_node("chatbot", chatbot_node)
graph.add_node("emergency_protocol", emergency_protocol)
graph.add_node("end_or_continue", lambda x: x) 

graph.set_entry_point("chatbot")

graph.add_conditional_edges(
    "chatbot",
    router_emergency,
    {
        "emergency": "emergency_protocol",
        "continue_triage": "end_or_continue" # Roteia diretamente para o ponto de roteamento final
    }
)

# Roteia de Emergência para o ponto de roteamento final
graph.add_edge("emergency_protocol", "end_or_continue") 

graph.add_conditional_edges(
    "end_or_continue", 
    router_end,
    {
        "save_and_end": END,
        "continue_triage": "chatbot" 
    }
)

app = graph.compile()

# ----------------------------------------------------
# 5. FUNÇÃO DE INTEGRAÇÃO COM BANCO
# ----------------------------------------------------

def run_agent(chat_id: str, user_message: str) -> str:
    """
    Lógica de integração: Carrega estado, executa o grafo, salva o estado atualizado.
    """
    print("\n--- INICIANDO DEPURACÃO DA FUNÇÃO run_agent ---")
    
    chat = collection.find_one({"_id": ObjectId(chat_id)})
    if not chat:
        raise ValueError("Chat não encontrado")

    # 1. Prepara o estado inicial
    messages = chat.get("messages", []) + [{"sender": "user", "text": user_message}]
    state = {
        "messages": messages,
        "triagem": chat.get("triagem", {}),
        "resumo_confirmado": chat.get("resumo_confirmado", False),
        "emergency_detected": chat.get("emergency_detected", False),
        "turn_count": chat.get("turn_count", 0) 
    }
    
    print(f"1. ESTADO INICIAL (carregado do DB): {state}")

    # 2. Executa o LangGraph usando stream para rodar um turno
    final_state = state.copy()
    
    for s in app.stream(state):
        print(f"2. ATUALIZAÇÃO DO GRAFO (Stream): {s}")
        final_state.update(s)
        
        # Condição de parada de turno 
        if "__end__" in s or "decision_point" in s or "emergency_protocol" in s:
            print("2.1. O LangGraph atingiu um nó de parada. Saindo do loop de stream.")
            break
            
    updated_state = final_state
    
    print(f"3. ESTADO FINAL ATUALIZADO (após o stream): {updated_state}")
    
    # 3. Prepara a atualização base para o DB 
    update_fields = {
        "messages": updated_state.get("messages", []),
        "triagem": updated_state.get("triagem", {}),
        "resumo_confirmado": updated_state.get("resumo_confirmado", False),
        "emergency_detected": updated_state.get("emergency_detected", False),
        "turn_count": updated_state.get("turn_count", 0),
        "is_completed": False
    }

    print(f"4. VALOR DA FLAG 'resumo_confirmado': {updated_state.get('resumo_confirmado')}")
    
    # 4. LÓGICA DE SALVAMENTO FINAL E CONCLUSÃO 
    if updated_state.get("resumo_confirmado"):
        print("5. DETECTADO: resumo_confirmado é True. Entrando na lógica de salvamento final.")
        
        update_fields["is_completed"] = True
        update_fields["triagem"] = updated_state.get("triagem", {}) 
        
        if updated_state.get("emergency_detected"):
            update_fields["status"] = "EMERGENCY_ALERT"
        else:
            update_fields["status"] = "TRIAGE_COMPLETED"
    else:
        print("5. DETECTADO: resumo_confirmado é False. Nenhuma ação de salvamento final.")

    print(f"6. CAMPOS PREPARADOS PARA O DB: {update_fields}")

    # 5. Atualiza o MongoDB.
    collection.update_one(
        {"_id": ObjectId(chat_id)},
        {"$set": update_fields}
    )

    # 6. Retorna a última mensagem do agente
    agent_response = updated_state["messages"][-1]["text"]
    print(f"7. RESPOSTA DO AGENTE RETORNADA: {agent_response}")
    print("\n--- FIM DA DEPURACÃO ---")

    return agent_response