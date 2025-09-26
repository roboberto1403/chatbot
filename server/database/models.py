from pydantic import BaseModel
from typing import List, Dict, Any, TypedDict
from datetime import datetime

class Message(BaseModel):
    id: int
    text: str
    sender: str  # 'user' ou 'model'

class MessageInput(BaseModel):
    text: str
    sender: str

class Triagem(BaseModel):
    queixa_principal: str = ""
    sintomas_detalhados: str = ""
    duracao_frequencia: str = ""
    intensidade: str = ""
    historico_relevante: str = ""
    medidas_tomadas: str = ""
    emergency_alert: bool = False

class Chat(BaseModel):
    title: str
    is_completed: bool = False
    creation: int = int(datetime.timestamp(datetime.now()))
    messages: List[Message] = []  # histórico de mensagens
    triagem: Triagem = Triagem()  # preenchido ao final

class State(TypedDict):
    messages: List[Dict[str, str]]        # Histórico da conversa
    triagem: Dict[str, Any]               # Triagem estruturada
    resumo_confirmado: bool               # Flag de confirmação do resumo (gatilho de END)
    emergency_detected: bool              # Flag para protocolo de emergência
    turn_count: int                       # Contador de turnos para segurança
