import React, { useState, useEffect, useRef } from "react";
import { useLocalSearchParams } from "expo-router";
import { ChatScreen } from "../../../components/ChatScreen";
import { Text, FlatList } from "react-native";
import Constants from "expo-constants";

const apiUrl = Constants.expoConfig?.extra?.API_URL;

interface Message {
  id: string; 
  text: string;
  sender: string; 
}

export default function ChatScreenPage() {
  const params = useLocalSearchParams<{ chatId: string }>();
  const chatId = params.chatId ?? "desconhecido";
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputText, setInputText] = useState("");
  const [loading, setLoading] = useState(true);

  const flatListRef = useRef<FlatList<Message>>(null);

  // Função para buscar mensagens da API
  const fetchMessages = async () => {
    try {
      const response = await fetch(`${apiUrl}/chat-messages/${chatId}`);
      if (!response.ok) {
        throw new Error("Erro ao carregar mensagens.");
      }
      const data: Message[] = await response.json();
      const formatted = data.map((msg) => ({
        id: msg.id,
        text: msg.text,
        sender: msg.sender,
      }));
      setMessages(formatted);
    } catch (error) {
      console.error("Erro ao buscar mensagens:", error);
    } finally {
      setLoading(false);
    }
  };

  // Função para enviar uma nova mensagem
  const handleSend = async () => {
    if (!inputText.trim()) return;

    // Atualiza localmente imediatamente
    const userMessageId = `temp-${Date.now()}`;
    const newUserMessage = {
      id: userMessageId,
      text: inputText,
      sender: "user",
    };
    setMessages((prev) => [...prev, newUserMessage]);
    setInputText("");

    try {
      // Envia a mensagem do usuário
      const sendUserResponse = await fetch(`${apiUrl}/send-user/${chatId}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          text: newUserMessage.text,
          sender: newUserMessage.sender,
        }),
      });
      if (!sendUserResponse.ok) {
        throw new Error("Erro ao enviar mensagem do usuário.");
      }

      // Chama a API para o modelo responder
      const sendModelResponse = await fetch(`${apiUrl}/send-model/${chatId}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
      });
      if (!sendModelResponse.ok) {
        throw new Error("Erro ao obter resposta do modelo.");
      }

      // Recarrega mensagens para obter a resposta completa da IA
      await fetchMessages();
    } catch (error) {
      console.error("Erro no fluxo de envio:", error);
      // Opcional: Reverter o estado em caso de erro
      setMessages((prev) =>
        prev.filter((msg) => msg.id !== userMessageId)
      );
    }
  };

  // Efeitos para carregar mensagens na montagem e rolar a lista
  useEffect(() => {
    fetchMessages();
  }, [chatId]);

  useEffect(() => {
    // Adiciona um pequeno atraso para garantir que a renderização termine antes da rolagem
    const timer = setTimeout(() => {
      flatListRef.current?.scrollToEnd({ animated: true });
    }, 100);
    return () => clearTimeout(timer);
  }, [messages]);

  if (loading) {
    return <Text style={{ flex: 1, textAlign: 'center', marginTop: 50 }}>Carregando mensagens...</Text>;
  }

  // Passa o estado e as funções como props para o componente burro
  return (
    <ChatScreen
      chatId={chatId}
      messages={messages}
      inputText={inputText}
      setInputText={setInputText}
      handleSend={handleSend}
      flatListRef={flatListRef}
    />
  );
}