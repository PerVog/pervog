import React, { useEffect, useState } from 'react';
import { Sparkles, PlusCircle, Layers, Shirt, Sun, CloudRain, Wind, MapPin, ArrowRight } from 'lucide-react';
import { getWeather, getOutfitRecommendations, getWardrobe } from '../services/api';
import OutfitCard from '../components/OutfitCard';

export default function Dashboard({ setActiveTab, setSelectedMatchItem }) {
  const [weather, setWeather] = useState(null);
  const [todayOutfit, setTodayOutfit] = useState(null);
  const [itemCount, setItemCount] = useState(0);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadDashboard() {
      try {
        setLoading(true);
        // Load weather
        const wData = await getWeather('New York');
        setWeather(wData);

        // Load wardrobe items count
        const items = await getWardrobe({ user_id: 1 });
        setItemCount(items.length);

        if (items.length > 0) {
          // Fetch daily top recommendation
          const recs = await getOutfitRecommendations({
            user_id: 1,
            occasion: 'Casual Outing',
            use_current_weather: true,
            limit: 1,
          });
          if (recs && recs.length > 0) {
            setTodayOutfit(recs[0]);
          }
        }
      } catch (err) {
        console.error('Failed loading dashboard:', err);
      } finally {
        setLoading(false);
      }
    }
    loadDashboard();
  }, []);

  return (
    <div>
      <div className="page-header">
        <div>
          <h1 className="page-title">Welcome back, Alex</h1>
          <p className="page-subtitle">Your personalized ₹0 budget AI wardrobe assistant is active.</p>
        </div>

        <button className="btn btn-primary" onClick={() => setActiveTab('generator')}>
          <Sparkles size={18} />
          <span>What Should I Wear?</span>
        </button>
      </div>

      {/* Weather Widget & Quick Stats Banner */}
      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))',
        gap: '1.25rem',
        marginBottom: '2rem'
      }}>
        {/* Weather Card */}
        <div className="glass-card" style={{
          background: 'linear-gradient(135deg, rgba(99, 102, 241, 0.15), rgba(6, 182, 212, 0.1))',
          borderColor: 'rgba(99, 102, 241, 0.3)'
        }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', color: '#A5B4FC' }}>
              <MapPin size={18} />
              <span style={{ fontWeight: 700, fontSize: '0.9rem' }}>{weather?.location || 'New York'}</span>
            </div>
            <span className="badge" style={{ background: 'rgba(255,255,255,0.1)' }}>Live Forecast</span>
          </div>

          <div style={{ display: 'flex', alignItems: 'center', gap: '1.25rem', marginBottom: '1rem' }}>
            <Sun size={48} color="#F59E0B" />
            <div>
              <div style={{ fontSize: '2.25rem', fontWeight: 800, fontFamily: 'var(--font-heading)', color: 'white' }}>
                {weather?.temperature_c || 22}°C
              </div>
              <p style={{ color: '#D1D5DB', fontSize: '0.9rem' }}>{weather?.weather_condition || 'Sunny & Clear'}</p>
            </div>
          </div>

          <div style={{ display: 'flex', gap: '1.5rem', fontSize: '0.8rem', color: '#9CA3AF', marginBottom: '0.75rem' }}>
            <span style={{ display: 'flex', alignItems: 'center', gap: '0.35rem' }}>
              <CloudRain size={14} /> Rain: {weather?.rain_probability || 10}%
            </span>
            <span style={{ display: 'flex', alignItems: 'center', gap: '0.35rem' }}>
              <Wind size={14} /> Wind: {weather?.wind_speed_kmh || 12} km/h
            </span>
          </div>

          <p style={{ fontSize: '0.8rem', color: '#E5E7EB', background: 'rgba(0,0,0,0.3)', padding: '0.65rem 0.85rem', borderRadius: '8px' }}>
            💡 {weather?.advice || 'Mild pleasant temperature: light layering works great today.'}
          </p>
        </div>

        {/* Quick Actions Grid */}
        <div className="glass-card" style={{ display: 'flex', flexDirection: 'column', justifyContent: 'space-between' }}>
          <div>
            <h3 style={{ fontSize: '1.1rem', fontWeight: 700, color: 'white', marginBottom: '0.5rem' }}>Quick Actions</h3>
            <p style={{ fontSize: '0.85rem', color: '#9CA3AF', marginBottom: '1.25rem' }}>
              Manage your digital closet of {itemCount} items or get instant styling advice.
            </p>
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.75rem' }}>
            <button
              className="btn btn-secondary"
              style={{ justifyContent: 'flex-start', padding: '0.75rem 1rem' }}
              onClick={() => setActiveTab('add-clothing')}
            >
              <PlusCircle size={18} color="#6366F1" />
              <span>+ Add Clothing</span>
            </button>

            <button
              className="btn btn-secondary"
              style={{ justifyContent: 'flex-start', padding: '0.75rem 1rem' }}
              onClick={() => setActiveTab('generator')}
            >
              <Sparkles size={18} color="#EC4899" />
              <span>Generate Outfit</span>
            </button>

            <button
              className="btn btn-secondary"
              style={{ justifyContent: 'flex-start', padding: '0.75rem 1rem' }}
              onClick={() => setActiveTab('item-match')}
            >
              <Layers size={18} color="#06B6D4" />
              <span>Match an Item</span>
            </button>

            <button
              className="btn btn-secondary"
              style={{ justifyContent: 'flex-start', padding: '0.75rem 1rem' }}
              onClick={() => setActiveTab('wardrobe')}
            >
              <Shirt size={18} color="#10B981" />
              <span>My Wardrobe ({itemCount})</span>
            </button>
          </div>
        </div>
      </div>

      {/* Today's Top Outfit Recommendation */}
      <div style={{ marginBottom: '2rem' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.25rem' }}>
          <div>
            <h2 style={{ fontSize: '1.35rem', fontWeight: 800, color: 'white' }}>Today's Suggested Outfit</h2>
            <p style={{ fontSize: '0.85rem', color: '#9CA3AF' }}>Algorithmically picked for today's weather & casual outing</p>
          </div>

          <button
            className="btn btn-secondary"
            style={{ fontSize: '0.85rem' }}
            onClick={() => setActiveTab('generator')}
          >
            <span>See All Suggestions</span>
            <ArrowRight size={16} />
          </button>
        </div>

        {loading ? (
          <div className="glass-card" style={{ textAlign: 'center', padding: '3rem' }}>
            <p style={{ color: '#9CA3AF' }}>Generating today's optimal outfit score...</p>
          </div>
        ) : todayOutfit ? (
          <div style={{ maxWidth: '550px' }}>
            <OutfitCard outfit={todayOutfit} />
          </div>
        ) : (
          <div className="glass-card" style={{ textAlign: 'center', padding: '2.5rem' }}>
            <p style={{ color: '#9CA3AF', marginBottom: '1rem' }}>No wardrobe items uploaded yet.</p>
            <button className="btn btn-primary" onClick={() => setActiveTab('add-clothing')}>
              Upload Your First Clothing Item
            </button>
          </div>
        )}
      </div>
    </div>
  );
}
