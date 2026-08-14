import React, { useState } from 'react';
import { Sparkles, MapPin, Sun, CloudRain, RefreshCw } from 'lucide-react';
import { getOutfitRecommendations, submitOutfitFeedback } from '../services/api';
import OutfitCard from '../components/OutfitCard';

const OCCASIONS = [
  'Casual Outing', 'College', 'Office', 'Interview', 'Date',
  'Party', 'Wedding', 'Travel', 'Gym', 'Formal Event', 'Traditional Event'
];

export default function OutfitGenerator() {
  const [occasion, setOccasion] = useState('Casual Outing');
  const [useWeather, setUseWeather] = useState(true);
  const [manualTemp, setManualTemp] = useState(24);
  const [manualRain, setManualRain] = useState(false);
  const [outfits, setOutfits] = useState([]);
  const [loading, setLoading] = useState(false);
  const [generated, setGenerated] = useState(false);

  const handleGenerate = async () => {
    try {
      setLoading(true);
      const req = {
        user_id: 1,
        occasion: occasion,
        use_current_weather: useWeather,
        manual_temperature_c: useWeather ? null : parseFloat(manualTemp),
        manual_rain: useWeather ? null : manualRain,
        limit: 5,
      };

      const data = await getOutfitRecommendations(req);
      setOutfits(data);
      setGenerated(true);
    } catch (err) {
      console.error('Failed generating outfits:', err);
      alert('Could not generate outfits. Make sure you have clothing items in your wardrobe.');
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
          <h1 className="page-title">What Should I Wear?</h1>
          <p className="page-subtitle">Deterministic outfit recommendation engine powered by ₹0 local scoring rules</p>
        </div>
      </div>

      {/* Control Panel Glass Card */}
      <div className="glass-card" style={{ marginBottom: '2rem' }}>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(260px, 1fr))', gap: '1.25rem', alignItems: 'flex-end' }}>
          {/* Occasion Picker */}
          <div className="form-group" style={{ marginBottom: 0 }}>
            <label className="form-label">Where are you going?</label>
            <select className="form-select" value={occasion} onChange={(e) => setOccasion(e.target.value)}>
              {OCCASIONS.map(occ => <option key={occ} value={occ}>{occ}</option>)}
            </select>
          </div>

          {/* Weather Settings */}
          <div className="form-group" style={{ marginBottom: 0 }}>
            <label className="form-label">Weather Context</label>
            <div style={{ display: 'flex', gap: '0.5rem', alignItems: 'center' }}>
              <button
                type="button"
                className={`btn ${useWeather ? 'btn-primary' : 'btn-secondary'}`}
                style={{ flex: 1, padding: '0.65rem' }}
                onClick={() => setUseWeather(!useWeather)}
              >
                <MapPin size={16} />
                <span>{useWeather ? 'Using Live Forecast' : 'Manual Weather'}</span>
              </button>
            </div>
          </div>

          {!useWeather && (
            <div style={{ display: 'flex', gap: '0.75rem', alignItems: 'center' }}>
              <div className="form-group" style={{ flex: 1, marginBottom: 0 }}>
                <label className="form-label">Temp (°C)</label>
                <input
                  type="number"
                  className="form-input"
                  value={manualTemp}
                  onChange={(e) => setManualTemp(e.target.value)}
                />
              </div>

              <button
                type="button"
                className={`btn ${manualRain ? 'btn-primary' : 'btn-secondary'}`}
                style={{ alignSelf: 'flex-end' }}
                onClick={() => setManualRain(!manualRain)}
              >
                <CloudRain size={16} /> Rain
              </button>
            </div>
          )}

          <button
            className="btn btn-primary"
            style={{ padding: '0.75rem 1.5rem', height: '46px' }}
            disabled={loading}
            onClick={handleGenerate}
          >
            {loading ? <RefreshCw className="spin" size={18} /> : <Sparkles size={18} />}
            <span>{loading ? 'Generating Outfits...' : 'Generate Outfits'}</span>
          </button>
        </div>
      </div>

      {/* Results Section */}
      {loading ? (
        <div className="glass-card" style={{ textAlign: 'center', padding: '4rem' }}>
          <Sparkles size={36} color="#6366F1" style={{ marginBottom: '1rem', animation: 'spin 2s linear infinite' }} />
          <h3 style={{ color: 'white', fontWeight: 700 }}>Synthesizing Wardrobe Combinations...</h3>
          <p style={{ color: '#9CA3AF', fontSize: '0.85rem', marginTop: '0.5rem' }}>
            Evaluating color harmony, formality suitability, temperature comfort, and profile preferences.
          </p>
        </div>
      ) : generated && outfits.length > 0 ? (
        <div>
          <h2 style={{ fontSize: '1.35rem', fontWeight: 800, color: 'white', marginBottom: '1.25rem' }}>
            Top Recommended Outfits for {occasion}
          </h2>

          <div className="outfit-grid">
            {outfits.map((outfit, index) => (
              <OutfitCard key={index} outfit={outfit} onFeedback={handleFeedback} />
            ))}
          </div>
        </div>
      ) : generated ? (
        <div className="glass-card" style={{ textAlign: 'center', padding: '3rem' }}>
          <p style={{ color: '#9CA3AF' }}>No compatible outfits could be created with current closet items.</p>
        </div>
      ) : null}
    </div>
  );
}
