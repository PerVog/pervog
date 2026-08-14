import React, { useEffect, useState } from 'react';
import { Layers, Sparkles, RefreshCw } from 'lucide-react';
import { getWardrobe, getRecommendationsForItem, submitOutfitFeedback } from '../services/api';
import OutfitCard from '../components/OutfitCard';

export default function SelectItemMatch({ selectedMatchItem, setSelectedMatchItem }) {
  const [items, setItems] = useState([]);
  const [selectedItem, setSelectedItem] = useState(selectedMatchItem || null);
  const [outfits, setOutfits] = useState([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    async function loadItems() {
      try {
        const data = await getWardrobe({ user_id: 1 });
        setItems(data);
        if (!selectedItem && data.length > 0) {
          setSelectedItem(data[0]);
        }
      } catch (err) {
        console.error('Failed loading wardrobe items:', err);
      }
    }
    loadItems();
  }, []);

  useEffect(() => {
    if (selectedItem) {
      fetchItemMatches(selectedItem.id);
    }
  }, [selectedItem]);

  const fetchItemMatches = async (itemId) => {
    try {
      setLoading(true);
      const data = await getRecommendationsForItem(itemId, 1, 'Casual Outing');
      setOutfits(data);
    } catch (err) {
      console.error('Failed loading item matches:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleFeedback = async (fbData) => {
    try {
      await submitOutfitFeedback(fbData);
    } catch (err) {
      console.error('Feedback failed:', err);
    }
  };

  return (
    <div>
      <div className="page-header">
        <div>
          <h1 className="page-title">Match an Item</h1>
          <p className="page-subtitle">Pick any piece from your closet to find compatible items & scored outfit combinations</p>
        </div>
      </div>

      {/* Item Selector Dropdown / Grid */}
      <div className="glass-card" style={{ marginBottom: '2rem' }}>
        <h3 style={{ fontSize: '1rem', fontWeight: 700, color: 'white', marginBottom: '1rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          <Layers size={18} color="#06B6D4" />
          <span>Select Anchor Wardrobe Piece</span>
        </h3>

        <div className="form-group" style={{ marginBottom: '1.25rem' }}>
          <select
            className="form-select"
            value={selectedItem?.id || ''}
            onChange={(e) => {
              const found = items.find(it => it.id === parseInt(e.target.value));
              if (found) setSelectedItem(found);
            }}
          >
            {items.map(it => (
              <option key={it.id} value={it.id}>
                {it.title} ({it.category} • {it.attributes?.primary_color || 'color'})
              </option>
            ))}
          </select>
        </div>

        {selectedItem && (
          <div style={{ display: 'flex', alignItems: 'center', gap: '1.25rem', background: 'rgba(0,0,0,0.3)', padding: '1rem', borderRadius: '14px', border: '1px solid var(--border-glass)' }}>
            <img src={selectedItem.image_url} alt={selectedItem.title} style={{ width: '80px', height: '80px', objectFit: 'cover', borderRadius: '10px' }} />
            <div>
              <span className="badge" style={{ background: 'rgba(6, 182, 212, 0.2)', color: '#67E8F9', marginBottom: '0.25rem' }}>
                {selectedItem.category}
              </span>
              <h4 style={{ fontSize: '1.1rem', fontWeight: 800, color: 'white' }}>{selectedItem.title}</h4>
              <p style={{ fontSize: '0.85rem', color: '#9CA3AF', textTransform: 'capitalize' }}>
                Primary Color: {selectedItem.attributes?.primary_color} • Fit: {selectedItem.attributes?.fit || 'regular'} • Style: {selectedItem.attributes?.style || 'casual'}
              </p>
            </div>
          </div>
        )}
      </div>

      {/* Scored Matches Results */}
      {loading ? (
        <div className="glass-card" style={{ textAlign: 'center', padding: '3rem' }}>
          <RefreshCw className="spin" size={24} color="#06B6D4" style={{ marginBottom: '0.5rem' }} />
          <p style={{ color: '#9CA3AF' }}>Finding compatible tops, bottoms, shoes & accessories...</p>
        </div>
      ) : outfits.length > 0 ? (
        <div>
          <h2 style={{ fontSize: '1.35rem', fontWeight: 800, color: 'white', marginBottom: '1.25rem' }}>
            Outfits Styled Around "{selectedItem?.title}"
          </h2>

          <div className="outfit-grid">
            {outfits.map((outfit, index) => (
              <OutfitCard key={index} outfit={outfit} onFeedback={handleFeedback} />
            ))}
          </div>
        </div>
      ) : (
        <div className="glass-card" style={{ textAlign: 'center', padding: '3rem' }}>
          <p style={{ color: '#9CA3AF' }}>No compatible matching combinations found in closet.</p>
        </div>
      )}
    </div>
  );
}
