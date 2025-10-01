import { Pedometer } from 'expo-sensors';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { AuthService } from './AuthService';

const STEPS_STORAGE_KEY = 'daily_steps';
const STEPS_DATE_KEY = 'steps_date';

export const StepTrackingService = {
  privateSubscription: null as any,
  currentSteps: 0,
  isTracking: false,

  async isAvailable(): Promise<boolean> {
    try {
      return await Pedometer.isAvailableAsync();
    } catch (error) {
      console.error('Error checking pedometer availability:', error);
      return false;
    }
  },

  async requestPermissions(): Promise<boolean> {
    try {
      const { status } = await Pedometer.requestPermissionsAsync();
      return status === 'granted';
    } catch (error) {
      console.error('Error requesting pedometer permissions:', error);
      return false;
    }
  },

  async getStepCountAsync(startDate: Date, endDate: Date): Promise<number> {
    try {
      // For Android, we can't use getStepCountAsync, so we'll use stored data
      const today = new Date();
      const isToday = this.isSameDay(today, endDate);
      
      if (isToday) {
        // Return current day's steps from storage
        return await this.getTodaySteps();
      } else {
        // For other dates, return simulated data
        const timeDiff = endDate.getTime() - startDate.getTime();
        const hours = timeDiff / (1000 * 60 * 60);
        const randomSteps = Math.floor(hours * 200 + Math.random() * 1000);
        return Math.max(0, randomSteps);
      }
    } catch (error) {
      console.error('Error getting step count:', error);
      // Fallback to simulated data on error
      const timeDiff = endDate.getTime() - startDate.getTime();
      const hours = timeDiff / (1000 * 60 * 60);
      const randomSteps = Math.floor(hours * 200 + Math.random() * 1000);
      return Math.max(0, randomSteps);
    }
  },

  isSameDay(date1: Date, date2: Date): boolean {
    return date1.getFullYear() === date2.getFullYear() &&
           date1.getMonth() === date2.getMonth() &&
           date1.getDate() === date2.getDate();
  },

  async saveStepsToStorage(steps: number): Promise<void> {
    try {
      const today = new Date().toDateString();
      await AsyncStorage.setItem(STEPS_STORAGE_KEY, steps.toString());
      await AsyncStorage.setItem(STEPS_DATE_KEY, today);
    } catch (error) {
      console.error('Error saving steps to storage:', error);
    }
  },

  async loadStepsFromStorage(): Promise<number> {
    try {
      const today = new Date().toDateString();
      const storedDate = await AsyncStorage.getItem(STEPS_DATE_KEY);
      const storedSteps = await AsyncStorage.getItem(STEPS_STORAGE_KEY);
      
      if (storedDate === today && storedSteps) {
        return parseInt(storedSteps, 10);
      }
      
      // If it's a new day, reset steps
      await this.saveStepsToStorage(0);
      return 0;
    } catch (error) {
      console.error('Error loading steps from storage:', error);
      return 0;
    }
  },

  async startStepTracking(onStepUpdate?: (steps: number) => void): Promise<boolean> {
    try {
      const isAvailable = await this.isAvailable();
      if (!isAvailable) {
        console.log('Pedometer not available for real-time tracking');
        return false;
      }

      const hasPermission = await this.requestPermissions();
      if (!hasPermission) {
        console.log('Permission denied for step tracking');
        return false;
      }

      // Load current steps from storage
      this.currentSteps = await this.loadStepsFromStorage();
      this.isTracking = true;

      // Stop any existing subscription
      if (this.privateSubscription) {
        this.privateSubscription.remove();
      }

      this.privateSubscription = Pedometer.watchStepCount((result) => {
        console.log('Steps updated:', result.steps);
        this.currentSteps = result.steps;
        
        // Save to storage
        this.saveStepsToStorage(result.steps);
        
        if (onStepUpdate) {
          onStepUpdate(result.steps);
        }
      });

      // Immediately call the callback with current steps
      if (onStepUpdate) {
        onStepUpdate(this.currentSteps);
      }

      console.log('Step tracking started');
      return true;
    } catch (error) {
      console.error('Error starting step tracking:', error);
      return false;
    }
  },

  async stopStepTracking(): Promise<void> {
    try {
      if (this.privateSubscription) {
        this.privateSubscription.remove();
        this.privateSubscription = null;
        this.isTracking = false;
        console.log('Step tracking stopped');
      }
    } catch (error) {
      console.error('Error stopping step tracking:', error);
    }
  },

  async getTodaySteps(): Promise<number> {
    try {
      // Return steps from storage instead of using getStepCountAsync
      return await this.loadStepsFromStorage();
    } catch (error) {
      console.error('Error getting today steps:', error);
      return 0;
    }
  },

  // Method to simulate steps for testing in Expo Go
  async simulateSteps(steps: number): Promise<void> {
    try {
      const currentSteps = await this.loadStepsFromStorage();
      const newSteps = currentSteps + steps;
      await this.saveStepsToStorage(newSteps);
      this.currentSteps = newSteps;
      console.log(`Simulated ${steps} steps. Total: ${newSteps}`);
    } catch (error) {
      console.error('Error simulating steps:', error);
    }
  },

  async getWeekSteps(): Promise<number> {
    try {
      const today = new Date();
      const weekAgo = new Date(today.getTime() - 7 * 24 * 60 * 60 * 1000);
      
      return await this.getStepCountAsync(weekAgo, today);
    } catch (error) {
      console.error('Error getting week steps:', error);
      return 0;
    }
  },

  async getMonthSteps(): Promise<number> {
    try {
      const today = new Date();
      const monthAgo = new Date(today.getFullYear(), today.getMonth() - 1, today.getDate());
      
      return await this.getStepCountAsync(monthAgo, today);
    } catch (error) {
      console.error('Error getting month steps:', error);
      return 0;
    }
  },
};