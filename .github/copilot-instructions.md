# Copilot Instructions for AI Agents

## Project Overview
This is a React Native app using Expo and Expo Router. It implements a simple chat interface with mock data and navigation between chat lists and individual chat screens.

## Architecture & Key Files
- **App.tsx**: Entry point for the app, sets up the root view.
- **src/app/_layout.tsx**: Configures navigation stack and layout using Expo Router.
- **src/app/index.tsx**: Main screen, displays a list of chats via `ChatList` and handles navigation.
- **src/app/chatlist/[id]/index.tsx**: Dynamic route for individual chat screens, loads `ChatScreen` for a given chat ID.
- **src/components/ChatList.tsx**: Renders the chat list and handles selection/new chat actions.
- **src/components/ChatScreen.tsx**: Displays the chat ID; extend here for chat details/messages.

## Navigation & Routing
- Uses **Expo Router** for navigation. Dynamic routes are defined in the `src/app/chatlist/[id]/` directory.
- Use `router.push('/chatlist/{id}')` to navigate to a specific chat.

## Data Flow
- Chat data is currently mocked in `src/app/index.tsx`.
- No backend/API integration is present; all data is local and static.

## Developer Workflows
- **Start app**: `npm start` or `expo start` (see `package.json` scripts for platform-specific commands).
- **TypeScript**: Strict mode enabled via `tsconfig.json`.
- **Component Props**: Use explicit TypeScript interfaces for props.

## Project Conventions
- All navigation logic uses Expo Router hooks (`useRouter`, `useLocalSearchParams`).
- UI components use React Native primitives (`View`, `Text`, `FlatList`, etc.) and `StyleSheet` for styling.
- New chat creation is stubbed; implement logic in `handleNewChat` in `src/app/index.tsx`.
- Empty files (e.g., `MessageBubble.tsx`, `criar-chat.tsx`) are placeholders for future features.

## Patterns & Examples
- **Dynamic Routing**: See `src/app/chatlist/[id]/index.tsx` for pattern.
- **Component Communication**: Pass callbacks (`onSelectChat`, `onNewChat`) as props to child components.
- **Styling**: Use `StyleSheet.create` for all styles.

## External Dependencies
- `expo`, `expo-router`, `react`, `react-native`, and related packages.
- No custom native modules or backend services.

## How to Extend
- Add chat message rendering in `ChatScreen.tsx` and `MessageBubble.tsx`.
- Implement chat creation logic in `criar-chat.tsx` and connect to `handleNewChat`.
- Integrate backend/API for real chat data if needed.

---
**Update this file if you add new architectural patterns, workflows, or conventions.**
