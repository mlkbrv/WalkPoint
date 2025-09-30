import React, {useState, useEffect} from 'react';
import {
  View,
  Text,
  StyleSheet,
  FlatList,
  TouchableOpacity,
  RefreshControl,
  Image,
} from 'react-native';
import {Ionicons} from '@expo/vector-icons';
import {LinearGradient} from 'expo-linear-gradient';
import {PromotionService} from '../services/PromotionService';

interface UserPromotion {
  user: {
    email: string;
    first_name: string;
    last_name: string;
  };
  promotion: {
    uuid: string;
    title: string;
    description: string;
    required_steps: number;
    partner: {
      name: string;
      description: string;
      icon: string;
    };
  };
  redeemed_at: string;
}

const MyRedemptionsScreen: React.FC = () => {
  const [redemptions, setRedemptions] = useState<UserPromotion[]>([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      const result = await PromotionService.getMyRedemptions();
      if (result.success) {
        setRedemptions(result.data);
      }
    } catch (error) {
      console.error('Error loading redemptions:', error);
    } finally {
      setLoading(false);
    }
  };

  const onRefresh = async () => {
    setRefreshing(true);
    await loadData();
    setRefreshing(false);
  };

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  const renderRedemption = ({item}: {item: UserPromotion}) => (
    <View style={styles.redemptionCard}>
      <View style={styles.redemptionHeader}>
        <View style={styles.partnerInfo}>
          {item.promotion.partner.icon && (
            <Image source={{uri: item.promotion.partner.icon}} style={styles.partnerIcon} />
          )}
          <View style={styles.partnerDetails}>
            <Text style={styles.partnerName}>{item.promotion.partner.name}</Text>
            <Text style={styles.redemptionDate}>
              Redeemed on {formatDate(item.redeemed_at)}
            </Text>
          </View>
        </View>
        <View style={styles.statusBadge}>
          <Ionicons name="checkmark-circle" size={16} color="#4CAF50" />
        </View>
      </View>

      <Text style={styles.promotionTitle}>{item.promotion.title}</Text>
      <Text style={styles.promotionDescription}>{item.promotion.description}</Text>

      <View style={styles.redemptionFooter}>
        <View style={styles.stepsInfo}>
          <Ionicons name="walk" size={16} color="#666" />
          <Text style={styles.stepsText}>
            {item.promotion.required_steps.toLocaleString()} steps used
          </Text>
        </View>
        <View style={styles.statusContainer}>
          <Text style={styles.statusText}>Redeemed</Text>
        </View>
      </View>
    </View>
  );

  if (loading) {
    return (
      <View style={styles.loadingContainer}>
        <Text>Loading your redemptions...</Text>
      </View>
    );
  }

  return (
    <View style={styles.container}>
      <LinearGradient
        colors={['#4CAF50', '#45a049']}
        style={styles.header}>
        <Text style={styles.title}>My Redemptions</Text>
        <Text style={styles.subtitle}>
          {redemptions.length} promotion{redemptions.length !== 1 ? 's' : ''} redeemed
        </Text>
      </LinearGradient>

      <FlatList
        data={redemptions}
        renderItem={renderRedemption}
        keyExtractor={item => `${item.promotion.uuid}-${item.redeemed_at}`}
        contentContainerStyle={styles.listContainer}
        refreshControl={
          <RefreshControl refreshing={refreshing} onRefresh={onRefresh} />
        }
        ListEmptyComponent={
          <View style={styles.emptyContainer}>
            <Ionicons name="bag-outline" size={64} color="#ccc" />
            <Text style={styles.emptyText}>No redemptions yet</Text>
            <Text style={styles.emptySubtext}>
              Start walking and redeem your first promotion!
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
  redemptionCard: {
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
  redemptionHeader: {
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
  redemptionDate: {
    fontSize: 12,
    color: '#666',
  },
  statusBadge: {
    alignItems: 'center',
    justifyContent: 'center',
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
  redemptionFooter: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  stepsInfo: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  stepsText: {
    fontSize: 14,
    color: '#666',
    marginLeft: 5,
  },
  statusContainer: {
    backgroundColor: '#E8F5E8',
    paddingHorizontal: 12,
    paddingVertical: 6,
    borderRadius: 12,
  },
  statusText: {
    fontSize: 12,
    color: '#4CAF50',
    fontWeight: 'bold',
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
    textAlign: 'center',
  },
});

export default MyRedemptionsScreen;