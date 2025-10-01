import React, {useState, useEffect} from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  Alert,
  RefreshControl,
  PermissionsAndroid,
  Platform,
} from 'react-native';
import {Ionicons} from '@expo/vector-icons';
import {LinearGradient} from 'expo-linear-gradient';
import {AuthService} from '../services/AuthService';
import {StepTrackingService} from '../services/StepTrackingService';
import StepCounter from '../components/StepCounter';

interface DailyStep {
  date: string;
  steps: number;
}

const StepTrackingScreen: React.FC = () => {
  const [todaySteps, setTodaySteps] = useState(0);
  const [user, setUser] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [isTracking, setIsTracking] = useState(false);
  const [pedometerAvailable, setPedometerAvailable] = useState(false);
  const [realTimeSteps, setRealTimeSteps] = useState(0);

  useEffect(() => {
    loadData();
    checkPedometerAvailability();
  }, []);

  const checkPedometerAvailability = async () => {
    try {
      const available = await StepTrackingService.isAvailable();
      setPedometerAvailable(available);
      if (!available) {
        Alert.alert(
          'Step Tracking Not Available',
          'Step tracking is not available on this device. You can still manually add steps.'
        );
      }
    } catch (error) {
      console.error('Error checking pedometer availability:', error);
    }
  };

  const loadData = async () => {
    try {
      const [profileResult, stepsResult, deviceSteps] = await Promise.all([
        AuthService.getProfile(),
        AuthService.getTodaySteps(),
        pedometerAvailable ? StepTrackingService.getTodaySteps() : Promise.resolve(0),
      ]);

      if (profileResult.success) {
        setUser(profileResult.data);
      }

      // Always use device steps if pedometer is available
      if (pedometerAvailable) {
        setTodaySteps(deviceSteps);
      } else if (stepsResult.success) {
        setTodaySteps(stepsResult.data.steps);
      }
    } catch (error) {
      console.error('Error loading data:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleStepsUpdate = (steps: number) => {
    setRealTimeSteps(steps);
    // Update todaySteps if real-time tracking is active
    if (isTracking) {
      setTodaySteps(steps);
    }
  };

  const onRefresh = async () => {
    setRefreshing(true);
    await loadData();
    setRefreshing(false);
  };

  const handleStartTracking = async () => {
    if (!pedometerAvailable) {
      Alert.alert('Ошибка', 'Отслеживание шагов недоступно на этом устройстве');
      return;
    }

    try {
      const success = await StepTrackingService.startStepTracking(handleStepsUpdate);
      if (success) {
        setIsTracking(true);
        Alert.alert('Успех', 'Отслеживание шагов запущено!');
      } else {
        Alert.alert('Ошибка', 'Не удалось запустить отслеживание шагов');
      }
    } catch (error) {
      Alert.alert('Ошибка', 'Не удалось запустить отслеживание шагов');
    }
  };

  const handleStopTracking = async () => {
    try {
      await StepTrackingService.stopStepTracking();
      setIsTracking(false);
      Alert.alert('Успех', 'Отслеживание шагов остановлено!');
    } catch (error) {
      Alert.alert('Ошибка', 'Не удалось остановить отслеживание шагов');
    }
  };

  const handleAddSteps = () => {
    Alert.prompt(
      'Добавить шаги',
      'Введите количество шагов для добавления:',
      [
        {text: 'Отмена', style: 'cancel'},
        {
          text: 'Добавить',
          onPress: async (steps) => {
            if (steps && !isNaN(Number(steps))) {
              // Simulate steps for testing
              await StepTrackingService.simulateSteps(Number(steps));
              Alert.alert('Успех', 'Шаги успешно добавлены!');
              loadData();
            } else {
              Alert.alert('Ошибка', 'Пожалуйста, введите корректное число');
            }
          },
        },
      ],
      'plain-text',
      '',
      'numeric'
    );
  };

  const handleQuickAddSteps = async (steps: number) => {
    try {
      await StepTrackingService.simulateSteps(steps);
      loadData();
    } catch (error) {
      Alert.alert('Ошибка', 'Не удалось добавить шаги');
    }
  };

  const getProgressPercentage = () => {
    const dailyGoal = 10000; // Default daily goal
    return Math.min((todaySteps / dailyGoal) * 100, 100);
  };

  const getMotivationalMessage = () => {
    const percentage = getProgressPercentage();
    if (percentage >= 100) {
      return "🎉 Потрясающе! Вы достигли дневной цели!";
    } else if (percentage >= 75) {
      return "💪 Вы почти у цели! Продолжайте!";
    } else if (percentage >= 50) {
      return "👍 Отличный прогресс! Половина пути пройдена!";
    } else if (percentage >= 25) {
      return "🚶‍♂️ Хорошее начало! Продолжайте ходить!";
    } else {
      return "👟 Давайте двигаться! Каждый шаг имеет значение!";
    }
  };

  if (loading) {
    return (
      <View style={styles.loadingContainer}>
        <Text>Загрузка...</Text>
      </View>
    );
  }

  return (
    <ScrollView
      style={styles.container}
      refreshControl={
        <RefreshControl refreshing={refreshing} onRefresh={onRefresh} />
      }>
      <LinearGradient
        colors={['#4CAF50', '#45a049']}
        style={styles.header}>
        <Text style={styles.title}>Отслеживание шагов</Text>
        <Text style={styles.subtitle}>Отслеживайте свой ежедневный прогресс</Text>
      </LinearGradient>

      <View style={styles.statsContainer}>
        {/* Real-time Step Counter */}
        <StepCounter 
          onStepsUpdate={handleStepsUpdate}
          style={styles.stepCounterCard}
        />

        <View style={styles.mainStatCard}>
          <View style={styles.stepIcon}>
            <Ionicons name="walk" size={40} color="#4CAF50" />
          </View>
          <Text style={styles.stepNumber}>{todaySteps.toLocaleString()}</Text>
          <Text style={styles.stepLabel}>Шагов сегодня</Text>
          <View style={styles.progressContainer}>
            <View style={styles.progressBar}>
              <View
                style={[
                  styles.progressFill,
                  {width: `${getProgressPercentage()}%`},
                ]}
              />
            </View>
            <Text style={styles.progressText}>
              {Math.round(getProgressPercentage())}% от дневной цели
            </Text>
          </View>
        </View>

        <View style={styles.motivationCard}>
          <Ionicons name="fitness" size={24} color="#4CAF50" />
          <Text style={styles.motivationText}>
            {getMotivationalMessage()}
          </Text>
        </View>
      </View>

      <View style={styles.actionsContainer}>
        {pedometerAvailable && (
          <TouchableOpacity 
            style={[styles.actionButton, isTracking && styles.actionButtonActive]} 
            onPress={isTracking ? handleStopTracking : handleStartTracking}>
            <Ionicons name={isTracking ? "stop" : "play"} size={24} color="white" />
            <Text style={styles.actionButtonText}>
              {isTracking ? "Остановить отслеживание" : "Начать отслеживание"}
            </Text>
          </TouchableOpacity>
        )}

        <TouchableOpacity style={styles.actionButton} onPress={handleAddSteps}>
          <Ionicons name="add" size={24} color="white" />
          <Text style={styles.actionButtonText}>Добавить шаги</Text>
        </TouchableOpacity>

        <TouchableOpacity style={styles.actionButton} onPress={loadData}>
          <Ionicons name="refresh" size={24} color="white" />
          <Text style={styles.actionButtonText}>Обновить</Text>
        </TouchableOpacity>
      </View>

      {/* Quick Add Steps Buttons for Testing */}
      <View style={styles.quickAddContainer}>
        <Text style={styles.quickAddTitle}>🚶‍♂️ Быстрое добавление шагов (для тестирования)</Text>
        <View style={styles.quickAddButtons}>
          <TouchableOpacity 
            style={styles.quickAddButton} 
            onPress={() => handleQuickAddSteps(100)}>
            <Text style={styles.quickAddButtonText}>+100</Text>
          </TouchableOpacity>
          <TouchableOpacity 
            style={styles.quickAddButton} 
            onPress={() => handleQuickAddSteps(500)}>
            <Text style={styles.quickAddButtonText}>+500</Text>
          </TouchableOpacity>
          <TouchableOpacity 
            style={styles.quickAddButton} 
            onPress={() => handleQuickAddSteps(1000)}>
            <Text style={styles.quickAddButtonText}>+1000</Text>
          </TouchableOpacity>
          <TouchableOpacity 
            style={styles.quickAddButton} 
            onPress={() => handleQuickAddSteps(5000)}>
            <Text style={styles.quickAddButtonText}>+5000</Text>
          </TouchableOpacity>
        </View>
      </View>

      <View style={styles.infoContainer}>
        <View style={styles.infoCard}>
          <Ionicons name="trending-up" size={20} color="#2196F3" />
          <View style={styles.infoContent}>
            <Text style={styles.infoTitle}>Всего шагов</Text>
            <Text style={styles.infoValue}>
              {user?.total_steps?.toLocaleString() || 0}
            </Text>
          </View>
        </View>

        <View style={styles.infoCard}>
          <Ionicons name="star" size={20} color="#FF9800" />
          <View style={styles.infoContent}>
            <Text style={styles.infoTitle}>Доступные очки</Text>
            <Text style={styles.infoValue}>
              {user?.available_steps?.toLocaleString() || 0}
            </Text>
          </View>
        </View>
      </View>

      <View style={styles.tipsContainer}>
        <Text style={styles.tipsTitle}>💡 Советы для большего количества шагов</Text>
        <View style={styles.tipItem}>
          <Text style={styles.tipText}>• Используйте лестницу вместо лифта</Text>
        </View>
        <View style={styles.tipItem}>
          <Text style={styles.tipText}>• Паркуйтесь дальше от места назначения</Text>
        </View>
        <View style={styles.tipItem}>
          <Text style={styles.tipText}>• Делайте короткие прогулки каждый час</Text>
        </View>
        <View style={styles.tipItem}>
          <Text style={styles.tipText}>• Ходите во время телефонных разговоров</Text>
        </View>
      </View>
    </ScrollView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f5f5',
  },
  loadingContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
  header: {
    padding: 20,
    paddingTop: 40,
    alignItems: 'center',
  },
  title: {
    fontSize: 24,
    fontWeight: 'bold',
    color: 'white',
    marginBottom: 5,
  },
  subtitle: {
    fontSize: 16,
    color: 'rgba(255,255,255,0.8)',
  },
  statsContainer: {
    padding: 20,
    marginTop: -20,
  },
  stepCounterCard: {
    marginBottom: 20,
  },
  mainStatCard: {
    backgroundColor: 'white',
    padding: 30,
    borderRadius: 20,
    alignItems: 'center',
    marginBottom: 20,
    shadowColor: '#000',
    shadowOffset: {
      width: 0,
      height: 2,
    },
    shadowOpacity: 0.1,
    shadowRadius: 3.84,
    elevation: 5,
  },
  stepIcon: {
    width: 80,
    height: 80,
    borderRadius: 40,
    backgroundColor: '#f0f0f0',
    alignItems: 'center',
    justifyContent: 'center',
    marginBottom: 15,
  },
  stepNumber: {
    fontSize: 48,
    fontWeight: 'bold',
    color: '#4CAF50',
    marginBottom: 10,
  },
  stepLabel: {
    fontSize: 18,
    color: '#666',
    marginBottom: 20,
  },
  progressContainer: {
    width: '100%',
    alignItems: 'center',
  },
  progressBar: {
    width: '100%',
    height: 8,
    backgroundColor: '#e0e0e0',
    borderRadius: 4,
    marginBottom: 10,
  },
  progressFill: {
    height: '100%',
    backgroundColor: '#4CAF50',
    borderRadius: 4,
  },
  progressText: {
    fontSize: 14,
    color: '#666',
  },
  motivationCard: {
    backgroundColor: 'white',
    padding: 20,
    borderRadius: 15,
    flexDirection: 'row',
    alignItems: 'center',
    shadowColor: '#000',
    shadowOffset: {
      width: 0,
      height: 1,
    },
    shadowOpacity: 0.1,
    shadowRadius: 2,
    elevation: 3,
  },
  motivationText: {
    fontSize: 16,
    color: '#333',
    marginLeft: 15,
    flex: 1,
  },
  actionsContainer: {
    flexDirection: 'row',
    paddingHorizontal: 20,
    marginBottom: 20,
  },
  actionButton: {
    flex: 1,
    backgroundColor: '#4CAF50',
    padding: 15,
    borderRadius: 15,
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    marginHorizontal: 5,
  },
  actionButtonActive: {
    backgroundColor: '#f44336',
  },
  actionButtonText: {
    color: 'white',
    fontSize: 16,
    fontWeight: 'bold',
    marginLeft: 8,
  },
  infoContainer: {
    paddingHorizontal: 20,
    marginBottom: 20,
  },
  infoCard: {
    backgroundColor: 'white',
    padding: 15,
    borderRadius: 15,
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 10,
    shadowColor: '#000',
    shadowOffset: {
      width: 0,
      height: 1,
    },
    shadowOpacity: 0.1,
    shadowRadius: 2,
    elevation: 3,
  },
  infoContent: {
    marginLeft: 15,
    flex: 1,
  },
  infoTitle: {
    fontSize: 14,
    color: '#666',
    marginBottom: 5,
  },
  infoValue: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#333',
  },
  tipsContainer: {
    backgroundColor: 'white',
    margin: 20,
    padding: 20,
    borderRadius: 15,
    shadowColor: '#000',
    shadowOffset: {
      width: 0,
      height: 1,
    },
    shadowOpacity: 0.1,
    shadowRadius: 2,
    elevation: 3,
  },
  tipsTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 15,
  },
  tipItem: {
    marginBottom: 8,
  },
  tipText: {
    fontSize: 14,
    color: '#666',
    lineHeight: 20,
  },
  quickAddContainer: {
    backgroundColor: 'white',
    margin: 20,
    padding: 20,
    borderRadius: 15,
    shadowColor: '#000',
    shadowOffset: {
      width: 0,
      height: 1,
    },
    shadowOpacity: 0.1,
    shadowRadius: 2,
    elevation: 3,
  },
  quickAddTitle: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 15,
    textAlign: 'center',
  },
  quickAddButtons: {
    flexDirection: 'row',
    justifyContent: 'space-around',
    flexWrap: 'wrap',
  },
  quickAddButton: {
    backgroundColor: '#4CAF50',
    paddingHorizontal: 20,
    paddingVertical: 10,
    borderRadius: 20,
    margin: 5,
    minWidth: 70,
    alignItems: 'center',
  },
  quickAddButtonText: {
    color: 'white',
    fontSize: 16,
    fontWeight: 'bold',
  },
});

export default StepTrackingScreen;