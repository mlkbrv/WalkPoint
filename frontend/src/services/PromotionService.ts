import api from './AuthService';

export const PromotionService = {
  async getAllPromotions() {
    try {
      const response = await api.get('/core/promotions/all/');
      return {success: true, data: response.data};
    } catch (error: any) {
      return {
        success: false,
        error: error.response?.data || 'Failed to fetch promotions',
      };
    }
  },

  async getPromotionDetail(promotionId: string) {
    try {
      const response = await api.get(`/core/promotions/${promotionId}/`);
      return {success: true, data: response.data};
    } catch (error: any) {
      return {
        success: false,
        error: error.response?.data || 'Failed to fetch promotion details',
      };
    }
  },

  async purchasePromotion(promotionUuid: string) {
    try {
      const response = await api.post('/core/promotions/purchase/', {
        promotion_uuid: promotionUuid,
      });
      return {success: true, data: response.data};
    } catch (error: any) {
      return {
        success: false,
        error: error.response?.data || 'Failed to purchase promotion',
      };
    }
  },

  async getMyRedemptions() {
    try {
      const response = await api.get('/core/promotions/my-redemptions/');
      return {success: true, data: response.data};
    } catch (error: any) {
      return {
        success: false,
        error: error.response?.data || 'Failed to fetch redemptions',
      };
    }
  },
};