const API_BASE = '/api';

export async function fetchJson(endpoint, options = {}) {
  const res = await fetch(`${API_BASE}${endpoint}`, {
    headers: {
      'Content-Type': 'application/json',
      ...options.headers,
    },
    ...options,
  });

  if (!res.ok) {
    const errorData = await res.json().catch(() => ({}));
    throw new Error(errorData.detail || `HTTP Error ${res.status}`);
  }

  return res.json();
}

// User API
export const getUser = (userId = 1) => fetchJson(`/users/${userId}`);
export const updateUserProfile = (userId = 1, profileData) =>
  fetchJson(`/users/${userId}/profile`, {
    method: 'PUT',
    body: JSON.stringify(profileData),
  });

// Wardrobe API
export const getWardrobe = (params = {}) => {
  const query = new URLSearchParams(params).toString();
  return fetchJson(`/wardrobe?${query}`);
};

export const getWardrobeItem = (itemId) => fetchJson(`/wardrobe/${itemId}`);

export const createWardrobeItem = (itemData, userId = 1) =>
  fetchJson(`/wardrobe?user_id=${userId}`, {
    method: 'POST',
    body: JSON.stringify(itemData),
  });

export const createBatchWardrobeItems = (itemsData, userId = 1) =>
  fetchJson(`/wardrobe/batch?user_id=${userId}`, {
    method: 'POST',
    body: JSON.stringify(itemsData),
  });

export const updateWardrobeItem = (itemId, itemData) =>
  fetchJson(`/wardrobe/${itemId}`, {
    method: 'PUT',
    body: JSON.stringify(itemData),
  });

export const deleteWardrobeItem = (itemId) =>
  fetchJson(`/wardrobe/${itemId}`, {
    method: 'DELETE',
  });

export const uploadImage = async (file) => {
  const formData = new FormData();
  formData.append('file', file);

  const res = await fetch(`${API_BASE}/wardrobe/upload`, {
    method: 'POST',
    body: formData,
  });

  if (!res.ok) {
    const errText = await res.text().catch(() => '');
    let errMsg = `Upload failed with status ${res.status}`;
    try {
      const errJson = JSON.parse(errText);
      if (errJson.detail) errMsg = errJson.detail;
    } catch (e) {
      if (errText) errMsg = errText;
    }
    throw new Error(errMsg);
  }
  return res.json();
};

export const analyzeImage = (imageUrl) =>
  fetchJson(`/wardrobe/analyze?image_url=${encodeURIComponent(imageUrl)}`, {
    method: 'POST',
  });

// Recommendations API
export const getOutfitRecommendations = (recommendationReq) =>
  fetchJson(`/recommendations`, {
    method: 'POST',
    body: JSON.stringify(recommendationReq),
  });

export const getRecommendationsForItem = (itemId, userId = 1, occasion = 'Casual Outing') =>
  fetchJson(`/recommendations/item/${itemId}?user_id=${userId}&occasion=${encodeURIComponent(occasion)}`, {
    method: 'POST',
  });

// Feedback API
export const submitOutfitFeedback = (feedbackData) =>
  fetchJson(`/outfits/feedback`, {
    method: 'POST',
    body: JSON.stringify(feedbackData),
  });

export const getSavedOutfits = (userId = 1) =>
  fetchJson(`/outfits/saved?user_id=${userId}`);

// Shopping & Wardrobe Gaps API
export const getShoppingRecommendations = (userId = 1) =>
  fetchJson(`/shopping/recommendations?user_id=${userId}`);

// Weather API
export const getWeather = (location = 'New York') =>
  fetchJson(`/weather?location=${encodeURIComponent(location)}`);
