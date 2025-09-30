import React, {useState, useEffect} from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  RefreshControl,
  Alert,
} from 'react-native';
import {Ionicons} from '@expo/vector-icons';
import {LinearGradient} from 'expo-linear-gradient';
import {AuthService} from '../services/AuthService';
import {PromotionService} from '../services/PromotionService';

interface User {
  email: string;
  first_name: string;
  last_name: string;
  total_steps: number;
  available_steps: number;
  profile_pic?: string;
}

interface Promotion {
  uuid: string;
  title: string;
  description: string;
  required_steps: number;
  partner: {
    name: string;
    icon: string;
  };
}

const HomeScreen: React.FC = () => {
  const [user, setUser] = useState<User | null>(null);
  const [todaySteps, setTodaySteps] = useState(0);
  const [promotions, setPromotions] = useState<Promotion[]>([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      const [profileResult, stepsResult, promotionsResult] = await Promise.all([
        AuthService.getProfile(),
        AuthService.getTodaySteps(),
        PromotionService.getAllPromotions(),
      ]);

      if (profileResult.success) {
        setUser(profileResult.data);
      }

      if (stepsResult.success) {
        setTodaySteps(stepsResult.data.steps);
      }

      if (promotionsResult.success) {
        setPromotions(promotionsResult.data.slice(0, 3)); // Show only first 3
      }
    } catch (error) {
      console.error('Error loading data:', error);
    } finally {
      setLoading(false);
    }
  };

  const onRefresh = async () => {
    setRefreshing(true);
    await loadData();
    setRefreshing(false);
  };

  const handlePurchasePromotion = async (promotionUuid: string) => {
    const result = await PromotionService.purchasePromotion(promotionUuid);
    if (result.success) {
      Alert.alert('Success', 'Promotion purchased successfully!');
      loadData(); // Refresh data
    } else {
      Alert.alert('Error', result.error);
    }
  };

  if (loading) {
    return (
      <View style={styles.loadingContainer}>
        <Text>Loading...</Text>
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
        <View style={styles.welcomeSection}>
          <Text style={styles.welcomeText}>
            Welcome back, {user?.first_name || 'User'}!
          </Text>
          <Text style={styles.subtitle}>Keep walking to earn rewards</Text>
        </View>
      </LinearGradient>

      <View style={styles.statsContainer}>
        <View style={styles.statCard}>
          <View style={styles.statIcon}>
            <Ionicons name="walk" size={30} color="#4CAF50" />
          </View>
          <Text style={styles.statNumber}>{todaySteps.toLocaleString()}</Text>
          <Text style={styles.statLabel}>Steps Today</Text>
        </View>

        <View style={styles.statCard}>
          <View style={styles.statIcon}>
            <Ionicons name="trending-up" size={30} color="#2196F3" />
          </View>
          <Text style={styles.statNumber}>
            {user?.total_steps?.toLocaleString() || 0}
          </Text>
          <Text style={styles.statLabel}>Total Steps</Text>
        </View>

        <View style={styles.statCard}>
          <View style={styles.statIcon}>
            <Ionicons name="star" size={30} color="#FF9800" />
          </View>
          <Text style={styles.statNumber}>
            {user?.available_steps?.toLocaleString() || 0}
          </Text>
          <Text style={styles.statLabel}>Available Points</Text>
        </View>
      </View>

      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Featured Promotions</Text>
        {promotions.map(promotion => (
          <View key={promotion.uuid} style={styles.promotionCard}>
            <View style={styles.promotionHeader}>
              <Text style={styles.promotionTitle}>{promotion.title}</Text>
              <View style={styles.partnerBadge}>
                <Text style={styles.partnerText}>{promotion.partner.name}</Text>
              </View>
            </View>
            <Text style={styles.promotionDescription}>
              {promotion.description}
            </Text>
            <View style={styles.promotionFooter}>
              <View style={styles.stepsInfo}>
                <Ionicons name="walk" size={16} color="#666" />
                <Text style={styles.requiredSteps}>
                  {promotion.required_steps.toLocaleString()} steps required
                </Text>
              </View>
              <TouchableOpacity
                style={[
                  styles.purchaseButton,
                  (user?.available_steps || 0) < promotion.required_steps &&
                    styles.purchaseButtonDisabled,
                ]}
                onPress={() => handlePurchasePromotion(promotion.uuid)}
                disabled={
                  (user?.available_steps || 0) < promotion.required_steps
                }>
                <Text style={styles.purchaseButtonText}>Redeem</Text>
              </TouchableOpacity>
            </View>
          </View>
        ))}
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
  },
  welcomeSection: {
    alignItems: 'center',
  },
  welcomeText: {
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
    flexDirection: 'row',
    justifyContent: 'space-around',
    padding: 20,
    marginTop: -20,
  },
  statCard: {
    backgroundColor: 'white',
    padding: 20,
    borderRadius: 15,
    alignItems: 'center',
    flex: 1,
    marginHorizontal: 5,
    shadowColor: '#000',
    shadowOffset: {
      width: 0,
      height: 2,
    },
    shadowOpacity: 0.1,
    shadowRadius: 3.84,
    elevation: 5,
  },
  statIcon: {
    width: 50,
    height: 50,
    borderRadius: 25,
    backgroundColor: '#f0f0f0',
    alignItems: 'center',
    justifyContent: 'center',
    marginBottom: 10,
  },
  statNumber: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 5,
  },
  statLabel: {
    fontSize: 12,
    color: '#666',
  },
  section: {
    padding: 20,
  },
  sectionTitle: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 15,
  },
  promotionCard: {
    backgroundColor: 'white',
    padding: 15,
    borderRadius: 15,
    marginBottom: 15,
    shadowColor: '#000',
    shadowOffset: {
      width: 0,
      height: 1,
    },
    shadowOpacity: 0.1,
    shadowRadius: 2,
    elevation: 3,
  },
  promotionHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 10,
  },
  promotionTitle: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#333',
    flex: 1,
  },
  partnerBadge: {
    backgroundColor: '#f0f0f0',
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: 12,
  },
  partnerText: {
    fontSize: 12,
    color: '#666',
  },
  promotionDescription: {
    fontSize: 14,
    color: '#666',
    marginBottom: 15,
  },
  promotionFooter: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  stepsInfo: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  requiredSteps: {
    fontSize: 12,
    color: '#666',
    marginLeft: 5,
  },
  purchaseButton: {
    backgroundColor: '#4CAF50',
    paddingHorizontal: 20,
    paddingVertical: 8,
    borderRadius: 20,
  },
  purchaseButtonDisabled: {
    backgroundColor: '#ccc',
  },
  purchaseButtonText: {
    color: 'white',
    fontSize: 12,
    fontWeight: 'bold',
  },
});

export default HomeScreen;