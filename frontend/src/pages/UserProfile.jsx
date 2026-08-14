import React, { useEffect, useState } from 'react';
import { User, CheckCircle, Save } from 'lucide-react';
import { getUser, updateUserProfile } from '../services/api';

const COLORS = ['white', 'black', 'blue', 'navy', 'grey', 'beige', 'brown', 'green', 'olive', 'red', 'burgundy', 'pink', 'yellow'];

export default function UserProfile() {
  const [profile, setProfile] = useState({
    height_cm: 178,
    weight_kg: 72,
    skin_tone: 'medium',
    preferred_fit: 'regular',
    preferred_styles: ['casual', 'smart_casual'],
    favorite_colors: ['white', 'blue', 'navy', 'grey', 'black'],
    disliked_colors: ['neon green'],
    location: 'New York'
  });
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    async function loadProfile() {
      try {
        const u = await getUser(1);
        if (u && u.profile) {
          setProfile({
            height_cm: u.profile.height_cm || 178,
            weight_kg: u.profile.weight_kg || 72,
            skin_tone: u.profile.skin_tone || 'medium',
            preferred_fit: u.profile.preferred_fit || 'regular',
            preferred_styles: u.profile.preferred_styles || ['casual'],
            favorite_colors: u.profile.favorite_colors || ['white', 'blue'],
            disliked_colors: u.profile.disliked_colors || [],
            location: u.profile.location || 'New York'
          });
        }
      } catch (err) {
        console.error('Failed loading profile:', err);
      }
    }
    loadProfile();
  }, []);

  const handleSave = async () => {
    try {
      setSaving(true);
      await updateUserProfile(1, profile);
      alert('Profile updated successfully!');
    } catch (err) {
      console.error('Save failed:', err);
      alert('Error updating profile');
    } finally {
      setSaving(false);
    }
  };

  const toggleFavColor = (c) => {
    const favs = profile.favorite_colors || [];
    const newFavs = favs.includes(c) ? favs.filter(x => x !== c) : [...favs, c];
    setProfile({ ...profile, favorite_colors: newFavs });
  };

  return (
    <div style={{ maxWidth: '800px', margin: '0 auto' }}>
      <div className="page-header">
        <div>
          <h1 className="page-title">Style Profile & Physique</h1>
          <p className="page-subtitle">Configure your physical attributes and style preferences for custom outfit scoring</p>
        </div>
      </div>

      <div className="glass-card">
        <h3 style={{ fontSize: '1.1rem', fontWeight: 800, color: 'white', marginBottom: '1.25rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          <User size={18} color="#6366F1" />
          <span>Physical & Silhouette Attributes</span>
        </h3>

        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '1rem', marginBottom: '1.5rem' }}>
          <div className="form-group">
            <label className="form-label">Height (cm)</label>
            <input
              type="number"
              className="form-input"
              value={profile.height_cm}
              onChange={(e) => setProfile({ ...profile, height_cm: parseFloat(e.target.value) })}
            />
          </div>

          <div className="form-group">
            <label className="form-label">Weight (kg)</label>
            <input
              type="number"
              className="form-input"
              value={profile.weight_kg}
              onChange={(e) => setProfile({ ...profile, weight_kg: parseFloat(e.target.value) })}
            />
          </div>

          <div className="form-group">
            <label className="form-label">Skin Tone</label>
            <select
              className="form-select"
              value={profile.skin_tone}
              onChange={(e) => setProfile({ ...profile, skin_tone: e.target.value })}
            >
              <option value="fair">Fair</option>
              <option value="medium">Medium</option>
              <option value="olive">Olive</option>
              <option value="dark">Dark</option>
              <option value="warm">Warm</option>
              <option value="cool">Cool</option>
            </select>
          </div>

          <div className="form-group">
            <label className="form-label">Preferred Fit</label>
            <select
              className="form-select"
              value={profile.preferred_fit}
              onChange={(e) => setProfile({ ...profile, preferred_fit: e.target.value })}
            >
              <option value="slim">Slim</option>
              <option value="regular">Regular</option>
              <option value="relaxed">Relaxed</option>
              <option value="oversized">Oversized</option>
            </select>
          </div>
        </div>

        <div className="form-group" style={{ marginBottom: '1.5rem' }}>
          <label className="form-label">Default City Location (For Weather)</label>
          <input
            type="text"
            className="form-input"
            value={profile.location}
            onChange={(e) => setProfile({ ...profile, location: e.target.value })}
          />
        </div>

        <div className="form-group" style={{ marginBottom: '1.5rem' }}>
          <label className="form-label">Favorite Colors (Boosts Outfit Score)</label>
          <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.5rem', marginTop: '0.5rem' }}>
            {COLORS.map(c => {
              const active = (profile.favorite_colors || []).includes(c);
              return (
                <button
                  key={c}
                  type="button"
                  className={`pill ${active ? 'active' : ''}`}
                  onClick={() => toggleFavColor(c)}
                  style={{ textTransform: 'capitalize' }}
                >
                  {c}
                </button>
              );
            })}
          </div>
        </div>

        <button className="btn btn-primary" style={{ width: '100%', padding: '0.85rem' }} disabled={saving} onClick={handleSave}>
          <Save size={18} />
          <span>{saving ? 'Saving Profile...' : 'Save Profile Preferences'}</span>
        </button>
      </div>
    </div>
  );
}
