import React from 'react';
import { Heart, CheckCircle, EyeOff, Trash2 } from 'lucide-react';

const COLOR_MAP = {
  white: '#F8F9FA',
  black: '#212529',
  blue: '#0D6EFD',
  'light blue': '#ADD8E6',
  navy: '#0A192F',
  grey: '#6C757D',
  beige: '#D6C7B2',
  brown: '#795548',
  green: '#198754',
  olive: '#556B2F',
  red: '#DC3545',
  burgundy: '#800020',
  pink: '#E83E8C',
  yellow: '#FFC107',
  purple: '#800080',
  orange: '#FF8C00'
};

export default function WardrobeCard({ item, onToggleFavorite, onToggleAvailable, onDelete, onSelectForMatch }) {
  const colorHex = item.attributes?.color_hex || COLOR_MAP[item.attributes?.primary_color?.toLowerCase()] || '#888';

  return (
    <div className="wardrobe-card">
      <div className="wardrobe-img-wrapper">
        <img src={item.image_url} alt={item.title} className="wardrobe-img" />
        
        <button
          className={`favorite-btn ${item.is_favorite ? 'active' : ''}`}
          onClick={() => onToggleFavorite(item.id, !item.is_favorite)}
          title="Toggle Favorite"
        >
          <Heart size={18} fill={item.is_favorite ? 'currentColor' : 'none'} />
        </button>

        {!item.is_available && (
          <div style={{
            position: 'absolute',
            bottom: 0,
            left: 0,
            right: 0,
            background: 'rgba(239, 68, 68, 0.85)',
            color: 'white',
            textAlign: 'center',
            fontSize: '0.75rem',
            fontWeight: 700,
            padding: '2px 0'
          }}>
            UNAVAILABLE
          </div>
        )}
      </div>

      <div className="card-details">
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <h3 className="card-title" title={item.title}>{item.title}</h3>
          <span
            className="color-dot"
            style={{ backgroundColor: colorHex }}
            title={item.attributes?.primary_color || 'Color'}
          />
        </div>

        <div className="card-meta">
          <span className="badge">{item.category}</span>
          <span className="badge" style={{ textTransform: 'capitalize' }}>
            {item.attributes?.style || 'Casual'}
          </span>
        </div>

        <div style={{ display: 'flex', gap: '0.5rem', marginTop: '0.5rem' }}>
          {onSelectForMatch && (
            <button
              className="btn btn-secondary"
              style={{ flex: 1, padding: '0.35rem', fontSize: '0.75rem' }}
              onClick={() => onSelectForMatch(item)}
            >
              Match This
            </button>
          )}

          <button
            className="btn-icon"
            style={{ width: '28px', height: '28px' }}
            onClick={() => onToggleAvailable(item.id, !item.is_available)}
            title={item.is_available ? 'Mark Unavailable' : 'Mark Available'}
          >
            {item.is_available ? <CheckCircle size={14} color="#10B981" /> : <EyeOff size={14} color="#EF4444" />}
          </button>

          {onDelete && (
            <button
              className="btn-icon"
              style={{ width: '28px', height: '28px' }}
              onClick={() => onDelete(item.id)}
              title="Delete Item"
            >
              <Trash2 size={14} color="#9CA3AF" />
            </button>
          )}
        </div>
      </div>
    </div>
  );
}
