# WalkPoint Expo App

A React Native Expo application for tracking steps and redeeming promotions.

## Features

- **User Authentication**: Login and registration with JWT tokens
- **Step Tracking**: Track daily steps and view progress
- **Promotions**: Browse and redeem promotions from partners
- **Profile Management**: Update user profile information
- **Redemption History**: View past redemptions

## Prerequisites

- Node.js (>= 16)
- Expo CLI
- Expo Go app on your mobile device

## Installation

1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Install Expo CLI globally (if not already installed):
   ```bash
   npm install -g @expo/cli
   ```

## Configuration

Update the API base URL in `src/services/AuthService.ts`:
```typescript
const API_BASE_URL = 'http://your-django-server-url/api';
```

**Important**: For Expo Go, you need to use your computer's IP address instead of localhost. For example:
```typescript
const API_BASE_URL = 'http://192.168.1.100:8000/api';
```

## Running the App

1. Start the Expo development server:
   ```bash
   npm start
   ```

2. Open the Expo Go app on your mobile device

3. Scan the QR code that appears in your terminal or browser

4. The app will load on your device

## Alternative Running Methods

### Android
```bash
npm run android
```

### iOS
```bash
npm run ios
```

### Web
```bash
npm run web
```

## Project Structure

```
src/
├── screens/           # Screen components
│   ├── LoginScreen.tsx
│   ├── RegisterScreen.tsx
│   ├── HomeScreen.tsx
│   ├── StepTrackingScreen.tsx
│   ├── PromotionsScreen.tsx
│   ├── MyRedemptionsScreen.tsx
│   └── ProfileScreen.tsx
├── services/          # API services
│   ├── AuthService.ts
│   └── PromotionService.ts
└── components/        # Reusable components (if any)
```

## API Integration

The app integrates with the Django backend API:

- **Authentication**: `/api/users/`
- **Promotions**: `/api/core/`
- **Step Tracking**: `/api/users/steps/today/`

## Permissions

The app requires the following permissions (configured in app.json):
- Internet access
- Activity recognition (for step tracking)
- Location access (for step tracking)

## Development

To add new features or modify existing ones:

1. Create new screens in `src/screens/`
2. Add API services in `src/services/`
3. Update navigation in `App.tsx`
4. Test on both Android and iOS using Expo Go

## Troubleshooting

- Make sure the Django backend is running
- Check that the API base URL is correct and uses your computer's IP address
- Ensure all required permissions are granted
- Clear Expo cache: `expo start -c`
- Check that your mobile device and computer are on the same network

## Building for Production

To build the app for production:

```bash
# For Android
expo build:android

# For iOS
expo build:ios
```

## Expo Go Limitations

Note that some features might not work in Expo Go due to limitations:
- Some native modules might not be available
- Camera and image picker functionality might be limited
- Step tracking might require a physical device with proper sensors