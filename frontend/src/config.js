// Configuration for API endpoints
const config = {
  // Development environment
  development: {
    dianServiceUrl: 'http://localhost:8003',
    gatewayServiceUrl: 'http://localhost:8000'
  },
  // Production environment (Render deployment)
  production: {
    dianServiceUrl: 'https://excel-dian.onrender.com',
    gatewayServiceUrl: 'https://excel-dian.onrender.com' // For now, using the same URL since only DIAN service is deployed
  }
};

// Get current environment
const environment = process.env.NODE_ENV || 'development';

// Export the appropriate configuration
export const apiConfig = config[environment];

// Helper function to get the full URL for DIAN service endpoints
export const getDianServiceUrl = (endpoint) => {
  return `${apiConfig.dianServiceUrl}${endpoint}`;
};

// Helper function to get the full URL for gateway service endpoints
export const getGatewayServiceUrl = (endpoint) => {
  return `${apiConfig.gatewayServiceUrl}${endpoint}`;
}; 