import { Text, View } from "react-native";
import { MaterialCommunityIcons } from "@expo/vector-icons";
import { NavigationContainer } from "@react-navigation/native";
import { createBottomTabNavigator } from "@react-navigation/bottom-tabs";
import ChainlitChat from './screens/ChainlitChat';
import {
  ChainlitAPI,
  ChainlitContext
} from './libs/cl-sdk-1.2';

import { CHAINLIT_SERVER_HOST } from './chainlit.config.ts';
import { RecoilRoot } from "recoil";

const CHAINLIT_SERVER = `${CHAINLIT_SERVER_HOST}/chainlit`;

const apiClient = new ChainlitAPI(CHAINLIT_SERVER,"webapp");

function HomeScreen() {
  return (
    <View
      style={{
        flex: 1,
        justifyContent: "center", //垂直居中
        alignItems: "center", //水平剧中
      }}
    >
      <ChainlitContext.Provider value={apiClient}>
        <RecoilRoot>
          <ChainlitChat/>
        </RecoilRoot>
      </ChainlitContext.Provider>
    </View>
  );
}

function SettingsScreen() {
  return (
    <View style={{ flex: 1, justifyContent: "center", alignItems: "center" }}>
      <Text>Settings!</Text>
    </View>
  );
}

const Tab = createBottomTabNavigator();

export default function App() {
  return (
    <NavigationContainer>
      <Tab.Navigator>
        <Tab.Screen
          name="Chat"
          component={HomeScreen}
          options={{ tabBarIcon: makeIconRender("chat") }}
        />
        <Tab.Screen
          name="Settings"
          component={SettingsScreen}
          options={{ tabBarIcon: makeIconRender("cog") }}
        />
      </Tab.Navigator>
    </NavigationContainer>
  );
}

function makeIconRender(name) {
  return ({ color, size }) => (
    <MaterialCommunityIcons name={name} color={color} size={size} />
  );
}
