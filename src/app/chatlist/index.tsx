import React, { useEffect, useState } from "react";
import { Text } from "react-native";
import { ChatList, Chat } from "../../components/ChatList";
import { useRouter } from "expo-router";
import Constants from "expo-constants";

const apiUrl = Constants.expoConfig?.extra?.API_URL;

export default function ChatListScreen() {
  const router = useRouter();
  const [chats, setChats] = useState<Chat[]>([]);
  const [loading, setLoading] = useState(true);

  // Busca todos os chats
  async function fetchChats() {
    try {
      const response = await fetch(`${apiUrl}/chats`, {
        headers: {
          "Content-Type": "application/json",
          "ngrok-skip-browser-warning": "true",
        },
      });
      const data = await response.json();
      // mapeia o retorno para a interface Chat
      const formatted: Chat[] = data.map((chat: any) => ({
        id: chat.chat_id,
        title: chat.title,
        lastMessage: chat.lastMessage || "",
      }));
      setChats(formatted);
    } catch (error) {
      console.error("Erro ao buscar chats:", error);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    fetchChats();
  }, []);

  // Seleciona um chat
  function handleSelectChat(chatId: string) {
    router.push(`/chatlist/${chatId}`);
  }

  // Cria um novo chat
  async function handleNewChat() {
    try {
      const response = await fetch(`${apiUrl}/criar-chat`, {
        method: "POST",
        headers: { 
            "Content-Type": "application/json",
            "ngrok-skip-browser-warning": "true",
        },
        body: JSON.stringify({ title: "Nova Consulta" }), // você pode customizar o title
      });

      const data = await response.json();
      const newChatId = data.chat_id;

      // Atualiza a lista de chats
      await fetchChats();

    } catch (error) {
      console.error("Erro ao criar chat:", error);
    }
  }

  if (loading) return <Text>Carregando chats...</Text>;

  return (
    <ChatList
      chats={chats}
      onSelectChat={handleSelectChat}
      onNewChat={handleNewChat}
    />
  );
}