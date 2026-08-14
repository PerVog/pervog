import React, { useEffect, useState } from 'react';
import { ShoppingBag, TrendingUp, Sparkles, CheckCircle2 } from 'lucide-react';
import { getShoppingRecommendations } from '../services/api';

export default function ShoppingGaps() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadGaps() {
      try {
        setLoading(true);
        const res = await getShoppingRecommendations(1);
        setData(res);
      } catch (err) {
        console.error('Failed loading shopping recommendations:', err);
      } finally {
        setLoading(false);
      }
    }
    loadGaps();
  }, []);

  return (
    <div>
      <div className="page-header">
        <div>
          <h1 className="page-title">Wardrobe Gaps & Shopping Recommendations</h1>
          <p className="page-subtitle">Algorithmic analysis of essential missing pieces that unlock maximum outfit combinations</p>
        </div>
      </div>

      {loading ? (
        <div className="glass-card" style={{ textAlign: 'center', padding: '4rem' }}>
          <p style={{ color: '#9CA3AF' }}>Analyzing wardrobe gaps and outfit potential multipliers...</p>
        </div>
      ) : data ? (
        <div>
          <div className="glass-card" style={{
            background: 'linear-gradient(135deg, rgba(236, 72, 153, 0.15), rgba(99, 102, 241, 0.1))',
            borderColor: 'rgba(236, 72, 153, 0.3)',
            marginBottom: '2rem'
          }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
              <div style={{ width: '48px', height: '48px', borderRadius: '12px', background: 'rgba(236, 72, 153, 0.2)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                <TrendingUp size={24} color="#EC4899" />
              </div>
              <div>
                <h3 style={{ fontSize: '1.2rem', fontWeight: 800, color: 'white' }}>Wardrobe Versatility Index</h3>
                <p style={{ fontSize: '0.85rem', color: '#D1D5DB' }}>
                  Based on your {data.total_wardrobe_count} wardrobe items, adding these high-utility staples unlocks the highest number of new outfit combinations!
                </p>
              </div>
            </div>
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(320px, 1fr))', gap: '1.25rem' }}>
            {data.missing_gaps.map((gap, idx) => (
              <div key={idx} className="glass-card" style={{ display: 'flex', flexDirection: 'column', justifyContent: 'space-between' }}>
                <div>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.75rem' }}>
                    <span className="badge" style={{ background: 'rgba(99, 102, 241, 0.2)', color: '#A5B4FC' }}>
                      {gap.category}
                    </span>
                    <span className="badge" style={{
                      background: gap.usefulness_score === 'EXCELLENT' ? 'rgba(16, 185, 129, 0.2)' : 'rgba(245, 158, 11, 0.2)',
                      color: gap.usefulness_score === 'EXCELLENT' ? '#34D399' : '#FBBF24',
                      fontWeight: 800
                    }}>
                      {gap.usefulness_score} UTILITY
                    </span>
                  </div>

                  <h3 style={{ fontSize: '1.15rem', fontWeight: 800, color: 'white', marginBottom: '0.5rem' }}>
                    {gap.suggested_item}
                  </h3>

                  <p style={{ fontSize: '0.85rem', color: '#9CA3AF', marginBottom: '1.25rem' }}>
                    {gap.reason}
                  </p>
                </div>

                <div style={{
                  background: 'rgba(0,0,0,0.3)',
                  border: '1px solid rgba(255,255,255,0.06)',
                  borderRadius: '12px',
                  padding: '0.85rem'
                }}>
                  <div style={{ fontSize: '0.8rem', color: '#67E8F9', fontWeight: 700, display: 'flex', alignItems: 'center', gap: '0.35rem', marginBottom: '0.35rem' }}>
                    <Sparkles size={14} />
                    <span>Unlocks +{gap.potential_outfits_unlocked} New Outfit Combinations</span>
                  </div>
                  <p style={{ fontSize: '0.75rem', color: '#9CA3AF' }}>
                    Matches with {gap.compatible_tops_count} of your tops and {gap.compatible_bottoms_count} of your bottoms.
                  </p>
                </div>
              </div>
            ))}
          </div>
        </div>
      ) : null}
    </div>
  );
}
