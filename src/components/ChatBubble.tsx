import React from "react";
import { View, Text, StyleSheet } from "react-native";

interface ChatBubbleProps {
  text: string;
  sender: string; 
}

export function ChatBubble({ text, sender }: ChatBubbleProps) {
  return (
    <View
      style={[
        styles.bubble,
        sender === "user" ? styles.user : styles.model,
      ]}
    >
      <Text style={[styles.text, sender === "user" && styles.userText]}>
        {text}
      </Text>
    </View>
  );
}

const styles = StyleSheet.create({
  bubble: {
    padding: 10,
    borderRadius: 16,
    marginVertical: 4,
    maxWidth: "80%",
  },
  user: {
    backgroundColor: "#007AFF",
    alignSelf: "flex-end",
    borderTopRightRadius: 0,
  },
  model: {
    backgroundColor: "#E5E5EA",
    alignSelf: "flex-start",
    borderTopLeftRadius: 0,
  },
  text: {
    color: "#000",
  },
  userText: {
    color: "#fff",
  },
});
