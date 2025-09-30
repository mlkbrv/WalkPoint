import React from 'react';
import {NavigationContainer} from '@react-navigation/native';
import {createStackNavigator} from '@react-navigation/stack';
import {createBottomTabNavigator} from '@react-navigation/bottom-tabs';
import {Ionicons} from '@expo/vector-icons';
import {StatusBar} from 'expo-status-bar';
import {AuthProvider, useAuth} from './src/contexts/AuthContext';

// Screens
import LoginScreen from './src/screens/LoginScreen';
import RegisterScreen from './src/screens/RegisterScreen';
import HomeScreen from './src/screens/HomeScreen';
import ProfileScreen from './src/screens/ProfileScreen';
import PromotionsScreen from './src/screens/PromotionsScreen';
import MyRedemptionsScreen from './src/screens/MyRedemptionsScreen';
import StepTrackingScreen from './src/screens/StepTrackingScreen';

// Services
import {AuthService} from './src/services/AuthService';

const Stack = createStackNavigator();
const Tab = createBottomTabNavigator();

const AuthStack = () => (
  <Stack.Navigator screenOptions={{headerShown: false}}>
    <Stack.Screen name="Login" component={LoginScreen} />
    <Stack.Screen name="Register" component={RegisterScreen} />
  </Stack.Navigator>
);

const MainTabs = () => (
  <Tab.Navigator
    screenOptions={({route}) => ({
      tabBarIcon: ({focused, color, size}) => {
        let iconName: keyof typeof Ionicons.glyphMap;

        switch (route.name) {
          case 'Home':
            iconName = focused ? 'home' : 'home-outline';
            break;
          case 'Steps':
            iconName = focused ? 'walk' : 'walk-outline';
            break;
          case 'Promotions':
            iconName = focused ? 'gift' : 'gift-outline';
            break;
          case 'Profile':
            iconName = focused ? 'person' : 'person-outline';
            break;
          default:
            iconName = 'help-outline';
        }

        return <Ionicons name={iconName} size={size} color={color} />;
      },
      tabBarActiveTintColor: '#4CAF50',
      tabBarInactiveTintColor: 'gray',
      headerShown: false,
    })}>
    <Tab.Screen name="Home" component={HomeScreen} />
    <Tab.Screen name="Steps" component={StepTrackingScreen} />
    <Tab.Screen name="Promotions" component={PromotionsScreen} />
    <Tab.Screen name="Profile" component={ProfileScreen} />
  </Tab.Navigator>
);

const AppContent = () => {
  const {isAuthenticated, isLoading} = useAuth();

  console.log('App: isAuthenticated:', isAuthenticated, 'isLoading:', isLoading);

  if (isLoading) {
    return null; // You can add a loading screen here
  }

  return (
    <NavigationContainer>
      <StatusBar style="light" />
      {isAuthenticated ? <MainTabs key="main" /> : <AuthStack key="auth" />}
    </NavigationContainer>
  );
};

const App = () => {
  return (
    <AuthProvider>
      <AppContent />
    </AuthProvider>
  );
};

export default App;
