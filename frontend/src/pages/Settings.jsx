import React, { useState } from 'react';
import { Settings as SettingsIcon, ShieldCheck, Cpu, HardDrive } from 'lucide-react';

export default function Settings() {
  const [aiProvider, setAiProvider] = useState('local');
  const [storageType, setStorageType] = useState('local');

  return (
    <div style={{ maxWidth: '800px', margin: '0 auto' }}>
      <div className="page-header">
        <div>
          <h1 className="page-title">Settings & System Status</h1>
          <p className="page-subtitle">Configure recommendation engine parameters & system options</p>
        </div>
      </div>

      <div className="glass-card" style={{ marginBottom: '1.5rem' }}>
        <h3 style={{ fontSize: '1.1rem', fontWeight: 800, color: 'white', marginBottom: '1.25rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          <Cpu size={18} color="#6366F1" />
          <span>AI Vision Provider</span>
        </h3>

        <div className="form-group">
          <label className="form-label">Classification Provider Mode</label>
          <select className="form-select" value={aiProvider} onChange={(e) => setAiProvider(e.target.value)}>
            <option value="local">Local Vision (Pillow + RGB Dominant Color Extractor - ₹0 Budget)</option>
            <option value="manual">Manual Entry Fallback (Rule-Based Metadata Form)</option>
          </select>
        </div>

        <p style={{ fontSize: '0.8rem', color: '#9CA3AF' }}>
          Configured provider auto-detects clothing colors and suggests attributes on upload without requiring paid APIs.
        </p>
      </div>

      {/* ₹0 Budget Audit Box */}
      <div className="glass-card" style={{
        background: 'rgba(16, 185, 129, 0.1)',
        borderColor: 'rgba(16, 185, 129, 0.3)'
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '0.75rem' }}>
          <ShieldCheck size={22} color="#10B981" />
          <h3 style={{ fontSize: '1.1rem', fontWeight: 800, color: 'white' }}>Zero Paid Dependencies Audit</h3>
        </div>

        <ul style={{ listStyle: 'none', display: 'flex', flexDirection: 'column', gap: '0.5rem', fontSize: '0.85rem', color: '#D1D5DB' }}>
          <li>✓ <strong>AI Models:</strong> 100% Offline / Local K-Means RGB & Rule-Based Heuristic Classifiers</li>
          <li>✓ <strong>Weather API:</strong> Free Open-Meteo API (Zero API key required)</li>
          <li>✓ <strong>Database:</strong> SQLite with SQLAlchemy (PostgreSQL production-ready)</li>
          <li>✓ <strong>Image Storage:</strong> Local Filesystem (`uploads/` directory) with S3/R2 abstraction layer</li>
          <li>✓ <strong>Recommendation Engine:</strong> Weighted Rule-Based Deterministic Matrix</li>
        </ul>
      </div>
    </div>
  );
}
