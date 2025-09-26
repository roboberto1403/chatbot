import React from "react";
import { Stack } from "expo-router";

export default function Layout() {
  return (
    <Stack
      screenOptions={{
        contentStyle: { backgroundColor: "#fff" },
      }}
      initialRouteName="chatlist"
    >
      <Stack.Screen name="index" options={{ headerShown: false }} />
      <Stack.Screen name="chatlist" options={{ headerShown: false }} />
    </Stack>
  );
}