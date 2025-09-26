import React from "react";
import { Stack } from "expo-router";

export default function EventoLayout() {
  return (
    <Stack
      screenOptions={{
        headerShown: false, 
        contentStyle: { flex: 1, backgroundColor: "#f0f0f0" },
      }}
    >
      <Stack.Screen name="/" />
      <Stack.Screen name="/chatlist/[chatId]" />
    </Stack>
  );
}
