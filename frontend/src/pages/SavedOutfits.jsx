import React, { useEffect, useState } from 'react';
import { Heart } from 'lucide-react';
import { getSavedOutfits, submitOutfitFeedback } from '../services/api';
import OutfitCard from '../components/OutfitCard';

export default function SavedOutfits() {
  const [outfits, setOutfits] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadSaved() {
      try {
        setLoading(true);
        const data = await getSavedOutfits(1);
        setOutfits(data);
      } catch (err) {
        console.error('Failed loading saved outfits:', err);
      } finally {
        setLoading(false);
      }
    }
    loadSaved();
  }, []);

  const handleFeedback = async (fbData) => {
    try {
      await submitOutfitFeedback(fbData);
    } catch (err) {
      console.error('Feedback error:', err);
    }
  };

  return (
    <div>
      <div className="page-header">
        <div>
          <h1 className="page-title">Saved Outfits</h1>
          <p className="page-subtitle">Your collection of bookmarked and favorite outfit combinations</p>
        </div>
      </div>

      {loading ? (
        <div className="glass-card" style={{ textAlign: 'center', padding: '3rem' }}>
          <p style={{ color: '#9CA3AF' }}>Loading saved outfits...</p>
        </div>
      ) : outfits.length > 0 ? (
        <div className="outfit-grid">
          {outfits.map((outfit, idx) => (
            <OutfitCard key={idx} outfit={outfit} onFeedback={handleFeedback} />
          ))}
        </div>
      ) : (
        <div className="glass-card" style={{ textAlign: 'center', padding: '3rem' }}>
          <Heart size={36} color="#EC4899" style={{ marginBottom: '1rem' }} />
          <h3 style={{ color: 'white', fontWeight: 700, marginBottom: '0.5rem' }}>No Saved Outfits Yet</h3>
          <p style={{ color: '#9CA3AF', fontSize: '0.85rem' }}>
            Click the bookmark icon on any outfit recommendation to save it here for quick access.
          </p>
        </div>
      )}
    </div>
  );
}
