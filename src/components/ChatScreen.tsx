import React, { useEffect, useRef, useState } from "react";
import {
  View,
  Text,
  FlatList,
  TextInput,
  TouchableOpacity,
  StyleSheet,
  Keyboard,
  Platform,
  KeyboardEvent,
  Animated,
} from "react-native";
import { useSafeAreaInsets } from "react-native-safe-area-context";
import { ChatBubble } from "./ChatBubble"; 

const KEYBOARD_BOTTOM_MARGIN = 6; 

interface Message {
  id: string;
  text: string;
  sender: string;
}

interface ChatScreenProps {
  chatId: string;
  messages: Message[];
  inputText: string;
  setInputText: (text: string) => void;
  handleSend: () => void;
  flatListRef: any;
}

export function ChatScreen({
  chatId,
  messages,
  inputText,
  setInputText,
  handleSend,
  flatListRef,
}: ChatScreenProps) {
  const insets = useSafeAreaInsets();
  const animatedBottom = useRef(new Animated.Value(0)).current; 

  useEffect(() => {
    flatListRef.current?.scrollToEnd({ animated: true });
  }, [messages]);

  useEffect(() => {
    const showListener = Keyboard.addListener(
      Platform.OS === "ios" ? "keyboardWillShow" : "keyboardDidShow",
      (e: KeyboardEvent) => {
        Animated.timing(animatedBottom, {
          toValue: e.endCoordinates.height + KEYBOARD_BOTTOM_MARGIN, 
          duration: 20,
          useNativeDriver: false,
        }).start();
      }
    );

    const hideListener = Keyboard.addListener(
      Platform.OS === "ios" ? "keyboardWillHide" : "keyboardDidHide",
      () => {
        Animated.timing(animatedBottom, {
          toValue: 0,
          duration: 20,
          useNativeDriver: false,
        }).start();
      }
    );

    return () => {
      showListener.remove();
      hideListener.remove();
    };
  }, []);

  const INPUT_CONTENT_HEIGHT = 64; 
  const flatListBottomPadding = INPUT_CONTENT_HEIGHT + insets.bottom + KEYBOARD_BOTTOM_MARGIN + 16;


  return (
    <View style={{ flex: 1, backgroundColor: "#f2f2f7" }}>
      <View style={styles.headerContainer}>
        <Text style={styles.header}>Chat {chatId}</Text>
      </View>

      <FlatList
        ref={flatListRef}
        data={messages}
        keyExtractor={(item) => item.id}
        renderItem={({ item }) => <ChatBubble text={item.text} sender={item.sender} />}
        contentContainerStyle={{ padding: 16, paddingBottom: flatListBottomPadding }}
        style={{ flex: 1 }}
      />

      <Animated.View
        style={[
          styles.inputContainer,
          {
            bottom: animatedBottom, 
            paddingBottom: insets.bottom + KEYBOARD_BOTTOM_MARGIN, 
          },
        ]}
      >
        <TextInput
          style={styles.input}
          placeholder="Digite sua mensagem..."
          placeholderTextColor="#888"
          multiline
          value={inputText}
          onChangeText={setInputText}
        />
        <TouchableOpacity style={styles.sendButton} onPress={handleSend}>
          <Text style={styles.sendText}>Enviar</Text>
        </TouchableOpacity>
      </Animated.View>
    </View>
  );
}

const styles = StyleSheet.create({
  headerContainer: {
    padding: 20,
    backgroundColor: "#fff",
    borderBottomWidth: 1,
    borderColor: "#ddd",
  },
  header: { fontSize: 20, fontWeight: "bold" },
  inputContainer: {
    position: "absolute",
    left: 0,
    right: 0,
    flexDirection: "row",
    paddingHorizontal: 10,
    paddingTop: 10, 
    borderTopWidth: 1,
    borderColor: "#ddd",
    backgroundColor: "#fff", 
    alignItems: "flex-end",
  },
  input: {
    flex: 1,
    minHeight: 44,
    maxHeight: 120,
    borderWidth: 1,
    borderColor: "#ddd",
    borderRadius: 25,
    paddingHorizontal: 14,
    paddingVertical: 10,
    backgroundColor: "#fff",
    fontSize: 16,
  },
  sendButton: {
    marginLeft: 8,
    backgroundColor: "#007AFF",
    borderRadius: 25,
    paddingHorizontal: 18,
    paddingVertical: 12,
    justifyContent: "center",
  },
  sendText: { color: "#fff", fontWeight: "bold", fontSize: 16 },
});

