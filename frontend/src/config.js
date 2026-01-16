// Centralized configuration for API and WebSocket URLs

// Centralized configuration for API and WebSocket URLs

// Railway Backend URL provided by user
// NOTE: User has DNS records for medpulse.com pointing to 6bb9sx7p.up.railway.app
// Ideally we should use the custom domain if available, but for now we stick to the provided railway link
// or allow easy switching.
const BACKEND_HOST = 'zonal-delight-production.up.railway.app';
// const BACKEND_HOST = 'api.medpulse.com'; // Future custom domain

// Determine if we are in production or development (you might want to use process.env.NODE_ENV)
// For now, we default to the Railway URL as requested, or fallback to localhost if needed.
// To switch back to local, you can change this or add environment variable logic.

const IS_PROD = true; // Set to true for Railway deployment

export const API_BASE_URL = IS_PROD
    ? `https://${BACKEND_HOST}/api`
    : 'http://localhost:8000/api';

export const WS_BASE_URL = IS_PROD
    ? `wss://${BACKEND_HOST}/ws`
    : 'ws://localhost:8003/ws';

export const VOICE_API_URL = IS_PROD
    ? `https://${BACKEND_HOST}`
    : 'http://localhost:8003';
