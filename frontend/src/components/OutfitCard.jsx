import React, { useState } from 'react';
import { ThumbsUp, ThumbsDown, Bookmark, Check, Sparkles, ShieldCheck } from 'lucide-react';

export default function OutfitCard({ outfit, onFeedback }) {
  const [feedbackState, setFeedbackState] = useState({
    liked: null,
    saved: outfit.is_saved || false,
    worn: false,
  });

  const handleAction = (type) => {
    let newLiked = feedbackState.liked;
    let newSaved = feedbackState.saved;
    let newWorn = feedbackState.worn;

    if (type === 'like') newLiked = newLiked === true ? null : true;
    if (type === 'dislike') newLiked = newLiked === false ? null : false;
    if (type === 'save') newSaved = !newSaved;
    if (type === 'worn') newWorn = !newWorn;

    setFeedbackState({ liked: newLiked, saved: newSaved, worn: newWorn });

    if (onFeedback && outfit.id) {
      onFeedback({
        outfit_id: outfit.id,
        user_id: 1,
        liked: newLiked,
        saved: newSaved,
        worn: newWorn,
      });
    }
  };

  return (
    <div className="glass-card" style={{ display: 'flex', flexDirection: 'column', height: '100%' }}>
      {/* Header & Score */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '1rem' }}>
        <div>
          <span className="badge" style={{ background: 'rgba(99, 102, 241, 0.2)', color: '#A5B4FC', marginBottom: '0.25rem' }}>
            {outfit.occasion}
          </span>
          <h3 style={{ fontSize: '1.15rem', fontWeight: 800, color: 'white' }}>{outfit.title}</h3>
          {outfit.weather_condition && (
            <p style={{ fontSize: '0.8rem', color: '#9CA3AF' }}>
              {outfit.weather_condition} ({outfit.temperature_c}°C)
            </p>
          )}
        </div>

        <div className="score-badge">
          <Sparkles size={16} />
          <span>{Math.round(outfit.score)}/100</span>
        </div>
      </div>

      {/* Outfit Items Grid */}
      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fit, minmax(75px, 1fr))',
        gap: '0.5rem',
        marginBottom: '1rem'
      }}>
        {outfit.items.map((it, idx) => (
          <div key={idx} style={{
            background: 'rgba(0,0,0,0.3)',
            borderRadius: '10px',
            padding: '6px',
            textAlign: 'center',
            border: '1px solid rgba(255,255,255,0.05)'
          }}>
            <img
              src={it.item.image_url}
              alt={it.item.title}
              style={{ width: '100%', height: '70px', objectFit: 'cover', borderRadius: '6px', marginBottom: '4px' }}
            />
            <div style={{ fontSize: '0.7rem', fontWeight: 700, color: 'white', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
              {it.item.title}
            </div>
            <div style={{ fontSize: '0.65rem', color: '#9CA3AF', textTransform: 'capitalize' }}>
              {it.role}
            </div>
          </div>
        ))}
      </div>

      {/* Why This Works Section */}
      <div style={{
        background: 'rgba(255,255,255,0.03)',
        border: '1px solid rgba(255,255,255,0.06)',
        borderRadius: '12px',
        padding: '0.85rem',
        marginBottom: '1.25rem',
        flex: 1
      }}>
        <div style={{ fontSize: '0.8rem', fontWeight: 700, color: '#A5B4FC', display: 'flex', alignItems: 'center', gap: '0.35rem', marginBottom: '0.5rem' }}>
          <ShieldCheck size={16} />
          <span>Why This Outfit Works</span>
        </div>

        <ul style={{ listStyle: 'none', display: 'flex', flexDirection: 'column', gap: '0.35rem' }}>
          {outfit.reasons && outfit.reasons.map((r, i) => (
            <li key={i} style={{ fontSize: '0.8rem', color: '#D1D5DB', display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
              <span>{r}</span>
            </li>
          ))}
        </ul>

        {/* Score Breakdown Bar */}
        {outfit.score_breakdown && (
          <div className="score-bar-group" style={{ marginTop: '0.75rem' }}>
            <div className="score-bar-item">
              <span>Color Harmony</span>
              <div className="score-bar-track">
                <div className="score-bar-fill" style={{ width: `${outfit.score_breakdown.color || 80}%` }} />
              </div>
              <span>{outfit.score_breakdown.color}%</span>
            </div>
            <div className="score-bar-item">
              <span>Weather Match</span>
              <div className="score-bar-track">
                <div className="score-bar-fill" style={{ width: `${outfit.score_breakdown.weather || 80}%` }} />
              </div>
              <span>{outfit.score_breakdown.weather}%</span>
            </div>
          </div>
        )}
      </div>

      {/* Actions */}
      <div style={{ display: 'flex', gap: '0.5rem', marginTop: 'auto' }}>
        <button
          className={`btn ${feedbackState.worn ? 'btn-primary' : 'btn-secondary'}`}
          style={{ flex: 1, padding: '0.5rem' }}
          onClick={() => handleAction('worn')}
        >
          <Check size={16} />
          <span>{feedbackState.worn ? 'Worn Today' : 'Wear This'}</span>
        </button>

        <button
          className={`btn-icon ${feedbackState.saved ? 'active' : ''}`}
          style={{ background: feedbackState.saved ? 'rgba(99, 102, 241, 0.3)' : undefined }}
          onClick={() => handleAction('save')}
          title="Save Outfit"
        >
          <Bookmark size={18} fill={feedbackState.saved ? 'currentColor' : 'none'} />
        </button>

        <button
          className={`btn-icon ${feedbackState.liked === true ? 'active' : ''}`}
          style={{ color: feedbackState.liked === true ? '#10B981' : undefined }}
          onClick={() => handleAction('like')}
          title="Like Outfit"
        >
          <ThumbsUp size={18} />
        </button>

        <button
          className={`btn-icon ${feedbackState.liked === false ? 'active' : ''}`}
          style={{ color: feedbackState.liked === false ? '#EF4444' : undefined }}
          onClick={() => handleAction('dislike')}
          title="Dislike Outfit"
        >
          <ThumbsDown size={18} />
        </button>
      </div>
    </div>
  );
}
