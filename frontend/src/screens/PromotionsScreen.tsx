import React, {useState, useEffect} from 'react';
import {
  View,
  Text,
  StyleSheet,
  FlatList,
  TouchableOpacity,
  Alert,
  RefreshControl,
  Image,
} from 'react-native';
import {Ionicons} from '@expo/vector-icons';
import {LinearGradient} from 'expo-linear-gradient';
import {PromotionService} from '../services/PromotionService';
import {AuthService} from '../services/AuthService';

interface Promotion {
  uuid: string;
  title: string;
  description: string;
  required_steps: number;
  partner: {
    name: string;
    description: string;
    icon: string;
  };
  is_active: boolean;
  max_redemptions_per_user: number;
}

const PromotionsScreen: React.FC = () => {
  const [promotions, setPromotions] = useState<Promotion[]>([]);
  const [user, setUser] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      const [promotionsResult, profileResult] = await Promise.all([
        PromotionService.getAllPromotions(),
        AuthService.getProfile(),
      ]);

      if (promotionsResult.success) {
        setPromotions(promotionsResult.data);
      }

      if (profileResult.success) {
        setUser(profileResult.data);
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

  const handlePurchasePromotion = async (promotion: Promotion) => {
    if ((user?.available_steps || 0) < promotion.required_steps) {
      Alert.alert(
        'Insufficient Steps',
        `You need ${promotion.required_steps.toLocaleString()} steps to redeem this promotion. You currently have ${user?.available_steps?.toLocaleString() || 0} steps.`
      );
      return;
    }

    Alert.alert(
      'Confirm Purchase',
      `Are you sure you want to redeem "${promotion.title}" for ${promotion.required_steps.toLocaleString()} steps?`,
      [
        {text: 'Cancel', style: 'cancel'},
        {
          text: 'Redeem',
          onPress: async () => {
            const result = await PromotionService.purchasePromotion(promotion.uuid);
            if (result.success) {
              Alert.alert('Success', 'Promotion redeemed successfully!');
              loadData(); // Refresh data
            } else {
              Alert.alert('Error', result.error);
            }
          },
        },
      ]
    );
  };

  const renderPromotion = ({item}: {item: Promotion}) => {
    const canRedeem = (user?.available_steps || 0) >= item.required_steps;
    
    return (
      <View style={styles.promotionCard}>
        <View style={styles.promotionHeader}>
          <View style={styles.partnerInfo}>
            {item.partner.icon && (
              <Image source={{uri: item.partner.icon}} style={styles.partnerIcon} />
            )}
            <View style={styles.partnerDetails}>
              <Text style={styles.partnerName}>{item.partner.name}</Text>
              <Text style={styles.partnerDescription}>{item.partner.description}</Text>
            </View>
          </View>
          <View style={styles.statusBadge}>
            <Ionicons name="checkmark-circle" size={16} color="#4CAF50" />
            <Text style={styles.statusText}>Active</Text>
          </View>
        </View>

        <Text style={styles.promotionTitle}>{item.title}</Text>
        <Text style={styles.promotionDescription}>{item.description}</Text>

        <View style={styles.promotionFooter}>
          <View style={styles.stepsInfo}>
            <Ionicons name="walk" size={16} color="#666" />
            <Text style={styles.requiredSteps}>
              {item.required_steps.toLocaleString()} steps
            </Text>
          </View>
          
          <TouchableOpacity
            style={[
              styles.redeemButton,
              !canRedeem && styles.redeemButtonDisabled,
            ]}
            onPress={() => handlePurchasePromotion(item)}
            disabled={!canRedeem}>
            <Text style={[
              styles.redeemButtonText,
              !canRedeem && styles.redeemButtonTextDisabled,
            ]}>
              {canRedeem ? 'Redeem' : 'Not Enough Steps'}
            </Text>
          </TouchableOpacity>
        </View>
      </View>
    );
  };

  if (loading) {
    return (
      <View style={styles.loadingContainer}>
        <Text>Loading promotions...</Text>
      </View>
    );
  }

  return (
    <View style={styles.container}>
      <LinearGradient
        colors={['#4CAF50', '#45a049']}
        style={styles.header}>
        <Text style={styles.title}>Promotions</Text>
        <Text style={styles.subtitle}>
          Available Points: {user?.available_steps?.toLocaleString() || 0}
        </Text>
      </LinearGradient>

      <FlatList
        data={promotions}
        renderItem={renderPromotion}
        keyExtractor={item => item.uuid}
        contentContainerStyle={styles.listContainer}
        refreshControl={
          <RefreshControl refreshing={refreshing} onRefresh={onRefresh} />
        }
        ListEmptyComponent={
          <View style={styles.emptyContainer}>
            <Ionicons name="gift-outline" size={64} color="#ccc" />
            <Text style={styles.emptyText}>No promotions available</Text>
            <Text style={styles.emptySubtext}>
              Check back later for new offers
            </Text>
          </View>
        }
      />
    </View>
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
  listContainer: {
    padding: 20,
  },
  promotionCard: {
    backgroundColor: 'white',
    padding: 20,
    borderRadius: 15,
    marginBottom: 15,
    shadowColor: '#000',
    shadowOffset: {
      width: 0,
      height: 2,
    },
    shadowOpacity: 0.1,
    shadowRadius: 3.84,
    elevation: 5,
  },
  promotionHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'flex-start',
    marginBottom: 15,
  },
  partnerInfo: {
    flexDirection: 'row',
    alignItems: 'center',
    flex: 1,
  },
  partnerIcon: {
    width: 40,
    height: 40,
    borderRadius: 20,
    marginRight: 10,
  },
  partnerDetails: {
    flex: 1,
  },
  partnerName: {
    fontSize: 14,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 2,
  },
  partnerDescription: {
    fontSize: 12,
    color: '#666',
  },
  statusBadge: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#E8F5E8',
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: 12,
  },
  statusText: {
    fontSize: 10,
    color: '#4CAF50',
    fontWeight: 'bold',
    marginLeft: 4,
  },
  promotionTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 10,
  },
  promotionDescription: {
    fontSize: 14,
    color: '#666',
    lineHeight: 20,
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
    fontSize: 14,
    color: '#666',
    marginLeft: 5,
  },
  redeemButton: {
    backgroundColor: '#4CAF50',
    paddingHorizontal: 20,
    paddingVertical: 10,
    borderRadius: 20,
  },
  redeemButtonDisabled: {
    backgroundColor: '#ccc',
  },
  redeemButtonText: {
    color: 'white',
    fontSize: 14,
    fontWeight: 'bold',
  },
  redeemButtonTextDisabled: {
    color: '#999',
  },
  emptyContainer: {
    alignItems: 'center',
    paddingVertical: 50,
  },
  emptyText: {
    fontSize: 18,
    color: '#666',
    marginTop: 15,
    marginBottom: 5,
  },
  emptySubtext: {
    fontSize: 14,
    color: '#999',
  },
});

export default PromotionsScreen;