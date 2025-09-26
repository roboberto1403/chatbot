import React from "react";
import { View, Text, FlatList, TouchableOpacity, StyleSheet } from "react-native";

export interface Chat {
    id: string;
    title: string;
    lastMessage?: string;
}

export interface ChatListProps {
    chats: Chat[];
    onSelectChat: (chatId: string) => void;
    onNewChat: () => void;
}

export function ChatList({ chats, onSelectChat, onNewChat }: ChatListProps) {
  return (
    <View style={styles.container}>
    <TouchableOpacity style={styles.newChatButton} onPress={onNewChat}>
        <Text style={styles.newChatText}>+ Nova Conversa</Text>
    </TouchableOpacity>
      <FlatList
        data={chats}
        keyExtractor={(item) => item.id}
        renderItem={({ item }) => (
          <TouchableOpacity
            style={styles.chatItem}
            onPress={() => onSelectChat(item.id)}
          >
            <Text style={styles.title}>{item.title}</Text>
            {item.lastMessage && (
              <Text style={styles.subtitle}>{item.lastMessage}</Text>
            )}
          </TouchableOpacity>
        )}
      />

    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, padding: 16, backgroundColor: "#fff" },
  chatItem: { padding: 12, borderBottomWidth: 1, borderColor: "#ddd" },
  title: { fontSize: 16, fontWeight: "bold" },
  subtitle: { fontSize: 14, color: "#555" },
  newChatButton: {
    marginTop: 16,
    padding: 12,
    backgroundColor: "#007AFF",
    borderRadius: 8,
    alignItems: "center",
  },
  newChatText: { color: "#fff", fontWeight: "bold" },
});