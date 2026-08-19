import React, { useState } from 'react';
import { Upload, Sparkles, CheckCircle, ArrowLeft, RefreshCw, Layers, HelpCircle, ShieldCheck, AlertTriangle } from 'lucide-react';
import { uploadImage, analyzeImage, createWardrobeItem, createBatchWardrobeItems } from '../services/api';

const CATEGORIES = [
  'Suit Jacket', 'Blazer', 'Dress Shirt', 'Casual Shirt', 'Shirt', 'T-Shirt', 'Polo Shirt', 'Hoodie', 'Sweater', 'Casual Jacket', 'Coat',
  'Suit Trousers', 'Formal Trousers', 'Loose Pants', 'Wide Leg Pants', 'Chinos', 'Jeans', 'Cargo Pants', 'Shorts', 'Joggers',
  'Formal Shoes', 'Oxford Shoes', 'Derby Shoes', 'Loafers', 'Sneakers', 'Running Shoes', 'Sandals', 'Slides', 'Boots',
  'Watch', 'Belt', 'Tie', 'Glasses', 'Hat', 'Bag'
];

const COLORS = [
  'navy', 'dark navy', 'black', 'charcoal', 'dark grey', 'grey', 'brown', 'dark brown', 'white', 'cream', 'beige', 'khaki',
  'blue', 'light blue', 'green', 'olive', 'red', 'burgundy', 'pink', 'yellow', 'orange', 'unknown'
];

const FIT_OPTIONS = ['skinny', 'slim', 'regular', 'straight', 'relaxed', 'oversized'];

export default function AddClothing({ setActiveTab }) {
  const [step, setStep] = useState('upload'); // 'upload' | 'review_single' | 'review_multi'
  const [file, setFile] = useState(null);
  const [previewUrl, setPreviewUrl] = useState('');
  const [analyzing, setAnalyzing] = useState(false);
  const [saving, setSaving] = useState(false);

  // Overall Outfit Context State
  const [overallOutfit, setOverallOutfit] = useState(null);

  // Single Item State (No hardcoded Casual Shirt / white defaults)
  const [metadata, setMetadata] = useState({
    region_id: 'region_1',
    title: '',
    category: '',
    subcategory: '',
    primary_color: '',
    color_hex: '#000000',
    pattern: 'unknown',
    material: 'unknown',
    fit: 'regular',
    style: 'casual',
    formality: 3,
    confidence: 0.0,
    needs_confirmation: false,
    crop_url: null,
    warmth: 1,
    occasions: ['casual'],
    condition: 'good'
  });

  // Multi-Item State
  const [multiItems, setMultiItems] = useState([]);

  const handleFileChange = (e) => {
    const selected = e.target.files[0];
    if (selected) {
      setFile(selected);
      setPreviewUrl(URL.createObjectURL(selected));
    }
  };

  const handleAnalyzeAndProceed = async () => {
    if (!file && !previewUrl) return;

    try {
      setAnalyzing(true);
      setMultiItems([]);
      setOverallOutfit(null);

      // 1. Upload to server
      const uploadRes = await uploadImage(file);
      const serverImageUrl = uploadRes.image_url;
      setPreviewUrl(serverImageUrl);

      // 2. Analyze image using Multi-Model Computer Vision Pipeline
      const analysisRes = await analyzeImage(serverImageUrl);
      
      console.log("RAW CLOTHING ANALYSIS RESPONSE:", JSON.stringify(analysisRes, null, 2));

      if (analysisRes.overall_outfit) {
        setOverallOutfit(analysisRes.overall_outfit);
      }

      if (analysisRes.is_multi_item && analysisRes.items && analysisRes.items.length > 1) {
        // Multi-item photo detected
        const formattedMulti = analysisRes.items.map((item, idx) => {
          const regionId = item.region_id || item.id || `region_${idx + 1}`;
          const itemTypeVal = item.garment_type || item.item_type?.value || 'unknown';
          const displayName = item.display_name || item.category || 'Clothing Item';
          const colorName = item.color?.primary || 'unknown';
          const formalityScore = item.formality?.value ?? item.formality?.score ?? 3;
          
          const validCropUrl = item.crop_url || item.image_url || null;
          const colorPrefix = colorName && colorName !== 'unknown' ? colorName.charAt(0).toUpperCase() + colorName.slice(1) : '';
          const itemTitle = item.title || (colorPrefix ? `${colorPrefix} ${displayName}` : displayName);

          return {
            id: regionId,
            region_id: regionId,
            selected: true,
            title: itemTitle,
            category: displayName,
            crop_url: validCropUrl,
            image_failed: false,
            metadata: {
              item_type: itemTypeVal,
              subcategory: displayName,
              primary_color: colorName,
              color_hex: item.color_hex || '#000000',
              pattern: item.pattern?.value || 'unknown',
              material: item.material?.value || 'unknown',
              fit: item.fit?.value || 'regular',
              style: item.style?.value || analysisRes.overall_outfit?.style || 'casual',
              formality: formalityScore,
              confidence: item.confidence || 0.0,
              needs_confirmation: item.needs_confirmation || false,
              warmth: 1,
              occasions: analysisRes.overall_outfit?.occasion || ['casual'],
              condition: 'good'
            }
          };
        });
        setMultiItems(formattedMulti);
        setStep('review_multi');

      } else {
        // Single item photo
        const primaryItem = (analysisRes.items && analysisRes.items[0]) || {};
        const displayName = primaryItem.display_name || primaryItem.category || 'Clothing Item';
        const colorName = primaryItem.color?.primary || 'unknown';
        const formalityScore = primaryItem.formality?.value ?? 3;
        const validCropUrl = primaryItem.crop_url || primaryItem.image_url || null;
        const colorPrefix = colorName && colorName !== 'unknown' ? colorName.charAt(0).toUpperCase() + colorName.slice(1) : '';
        const itemTitle = primaryItem.title || (colorPrefix ? `${colorPrefix} ${displayName}` : displayName);

        setMetadata({
          region_id: primaryItem.region_id || 'region_1',
          title: itemTitle,
          category: displayName,
          subcategory: displayName,
          primary_color: colorName,
          color_hex: primaryItem.color_hex || '#000000',
          pattern: primaryItem.pattern?.value || 'unknown',
          material: primaryItem.material?.value || 'unknown',
          fit: primaryItem.fit?.value || 'regular',
          style: primaryItem.style?.value || analysisRes.overall_outfit?.style || 'casual',
          formality: formalityScore,
          confidence: primaryItem.confidence || 0.0,
          needs_confirmation: primaryItem.needs_confirmation || false,
          crop_url: validCropUrl,
          warmth: 1,
          occasions: analysisRes.overall_outfit?.occasion || ['casual'],
          condition: 'good'
        });
        setStep('review_single');
      }
    } catch (err) {
      console.error('Analysis failed:', err);
      alert(`AI Analysis Error: ${err.message}`);
      setStep('upload');
    } finally {
      setAnalyzing(false);
    }
  };

  const handleSaveSingleItem = async () => {
    try {
      setSaving(true);
      await createWardrobeItem({
        title: metadata.title,
        category: metadata.category,
        image_url: metadata.crop_url || previewUrl,
        is_favorite: false,
        is_available: true,
        attributes: {
          subcategory: metadata.subcategory,
          primary_color: metadata.primary_color,
          color_hex: metadata.color_hex,
          pattern: metadata.pattern,
          material: metadata.material,
          fit: metadata.fit,
          style: metadata.style,
          formality: parseInt(metadata.formality),
          warmth: parseInt(metadata.warmth),
          occasions: metadata.occasions,
          condition: metadata.condition
        }
      }, 1);

      alert('Item added successfully to your digital wardrobe!');
      setActiveTab('wardrobe');
    } catch (err) {
      console.error('Failed saving wardrobe item:', err);
      alert('Error saving wardrobe item');
    } finally {
      setSaving(false);
    }
  };

  const handleSaveMultiBatch = async () => {
    const selected = multiItems.filter(it => it.selected);
    if (selected.length === 0) {
      alert('Please select at least one item to save');
      return;
    }

    try {
      setSaving(true);
      const itemsPayload = selected.map(item => ({
        title: item.title,
        category: item.category,
        image_url: item.crop_url || previewUrl,
        is_favorite: false,
        is_available: true,
        attributes: {
          subcategory: item.metadata.subcategory,
          primary_color: item.metadata.primary_color,
          color_hex: item.metadata.color_hex,
          pattern: item.metadata.pattern,
          material: item.metadata.material,
          fit: item.metadata.fit,
          style: item.metadata.style,
          formality: parseInt(item.metadata.formality),
          warmth: parseInt(item.metadata.warmth),
          occasions: item.metadata.occasions,
          condition: item.metadata.condition
        }
      }));

      await createBatchWardrobeItems(itemsPayload, 1);
      alert(`Successfully saved ${selected.length} clothing item(s) to your digital wardrobe!`);
      setActiveTab('wardrobe');
    } catch (err) {
      console.error('Failed batch saving wardrobe items:', err);
      alert('Error saving selected wardrobe items');
    } finally {
      setSaving(false);
    }
  };

  const toggleMultiSelect = (index) => {
    setMultiItems(prev => {
      const copy = [...prev];
      copy[index].selected = !copy[index].selected;
      return copy;
    });
  };

  const updateMultiItemField = (index, field, value) => {
    setMultiItems(prev => {
      const copy = [...prev];
      copy[index].metadata[field] = value;
      return copy;
    });
  };

  const updateMultiItemCategory = (index, newCat) => {
    setMultiItems(prev => {
      const copy = [...prev];
      copy[index].category = newCat;
      copy[index].metadata.subcategory = newCat;
      return copy;
    });
  };

  return (
    <div style={{ maxWidth: '1000px', margin: '0 auto' }}>
      <div className="page-header">
        <div>
          <h1 className="page-title">Add Wardrobe Items</h1>
          <p className="page-subtitle">Upload a photo to automatically detect and classify clothing items</p>
        </div>
      </div>

      {step === 'upload' ? (
        <div className="glass-card" style={{ padding: '3rem 2rem', textAlign: 'center' }}>
          <div style={{ maxWidth: '480px', margin: '0 auto', display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
            <div style={{
              width: '80px', height: '80px',
              background: 'rgba(99, 102, 241, 0.15)',
              border: '1px solid rgba(99, 102, 241, 0.3)',
              borderRadius: '20px',
              display: 'flex', alignItems: 'center', justifyContent: 'center',
              margin: '0 auto', color: '#6366F1'
            }}>
              <Upload size={38} />
            </div>

            <div>
              <h2 style={{ fontSize: '1.35rem', fontWeight: 800, color: 'white' }}>Upload Outfit or Item Photo</h2>
              <p style={{ fontSize: '0.875rem', color: '#9CA3AF', marginTop: '0.35rem' }}>
                Supports multi-item outfit photos and single clothing items
              </p>
            </div>

            <label style={{ display: 'block', cursor: 'pointer' }}>
              <input
                type="file"
                accept="image/*"
                style={{ display: 'none' }}
                onChange={handleFileChange}
              />
              <div style={{
                border: '2px dashed rgba(255, 255, 255, 0.15)',
                borderRadius: '16px',
                padding: '1.75rem',
                transition: 'all 0.2s ease',
                background: 'rgba(15, 23, 42, 0.5)'
              }}>
                {previewUrl ? (
                  <img src={previewUrl} alt="Preview" style={{ maxHeight: '240px', margin: '0 auto', borderRadius: '10px', objectFit: 'contain' }} />
                ) : (
                  <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem', color: '#9CA3AF' }}>
                    <p style={{ fontWeight: 600, color: '#818CF8' }}>Click to select photo or drag and drop</p>
                    <p style={{ fontSize: '0.75rem' }}>PNG, JPG, JPEG or WEBP</p>
                  </div>
                )}
              </div>
            </label>

            <button
              className="btn btn-primary"
              disabled={!file || analyzing}
              onClick={handleAnalyzeAndProceed}
              style={{ width: '100%', padding: '0.9rem', fontSize: '1rem', justifyContent: 'center' }}
            >
              {analyzing ? <RefreshCw className="spin" size={18} /> : <Sparkles size={18} />}
              <span>{analyzing ? 'Analyzing Multi-Model Vision Stack...' : 'Analyze & Detect Items'}</span>
            </button>
          </div>
        </div>
      ) : step === 'review_multi' ? (
        <div className="glass-card" style={{ padding: '1.5rem' }}>
          {/* Overall Outfit Banner */}
          {overallOutfit && (
            <div style={{
              background: 'linear-gradient(135deg, rgba(30, 41, 59, 0.8), rgba(15, 23, 42, 0.9))',
              border: '1px solid rgba(99, 102, 241, 0.4)',
              borderRadius: '14px',
              padding: '1.15rem 1.35rem',
              marginBottom: '1.5rem',
              display: 'flex',
              justifyContent: 'space-between',
              alignItems: 'center',
              flexWrap: 'wrap',
              gap: '1rem'
            }}>
              <div>
                <span className="badge" style={{ background: 'rgba(99, 102, 241, 0.25)', color: '#A5B4FC', marginBottom: '0.35rem' }}>
                  <ShieldCheck size={14} style={{ display: 'inline', marginRight: '4px' }} /> Full Outfit Context Detected
                </span>
                <h3 style={{ fontSize: '1.15rem', fontWeight: 800, color: 'white', marginTop: '0.25rem' }}>
                  Outfit Type: {overallOutfit.outfit_type.toUpperCase()} ({overallOutfit.style})
                </h3>
                <p style={{ fontSize: '0.85rem', color: '#9CA3AF', marginTop: '0.2rem' }}>
                  Formality Score: <strong style={{ color: '#34D399' }}>{overallOutfit.formality}/10</strong> • Confidence: {Math.round(overallOutfit.confidence * 100)}%
                </p>
              </div>
            </div>
          )}

          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem', flexWrap: 'wrap', gap: '1rem' }}>
            <div>
              <span className="badge" style={{ background: 'rgba(6, 182, 212, 0.2)', color: '#67E8F9', marginBottom: '0.25rem' }}>
                <Layers size={14} style={{ display: 'inline', marginRight: '4px' }} /> Multi-Item Photo Detected
              </span>
              <h2 style={{ fontSize: '1.35rem', fontWeight: 800, color: 'white', marginTop: '0.25rem' }}>Select Items to Add to Your Wardrobe</h2>
              <p style={{ fontSize: '0.85rem', color: '#9CA3AF', marginTop: '0.25rem' }}>
                Cropped pieces extracted from your uploaded photo. Check the items you want to keep.
              </p>
            </div>
            <button className="btn btn-secondary" onClick={() => setStep('upload')}>
              <ArrowLeft size={16} /> Upload Another
            </button>
          </div>

          {/* Multi Item Cards Responsive Grid */}
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(290px, 1fr))', gap: '1.25rem', marginBottom: '2rem' }}>
            {multiItems.map((item, idx) => (
              <div
                key={item.region_id}
                style={{
                  background: item.selected ? 'rgba(99, 102, 241, 0.15)' : 'rgba(22, 28, 41, 0.75)',
                  border: item.selected ? '2px solid #6366F1' : '1px solid var(--border-glass)',
                  borderRadius: '14px',
                  padding: '1.15rem',
                  transition: 'var(--transition)'
                }}
              >
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.85rem' }}>
                  <label style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', cursor: 'pointer', fontWeight: 700, color: 'white', fontSize: '0.95rem' }}>
                    <input
                      type="checkbox"
                      checked={item.selected}
                      onChange={() => toggleMultiSelect(idx)}
                      style={{ width: '18px', height: '18px', accentColor: '#6366F1' }}
                    />
                    <span>Include {item.category} ({item.region_id})</span>
                  </label>
                  <span className="color-dot" style={{ backgroundColor: item.metadata.color_hex }} title={item.metadata.primary_color} />
                </div>

                {item.crop_url && !item.image_failed ? (
                  <img
                    src={item.crop_url}
                    alt={item.title}
                    onError={() => {
                      console.error(`Crop loading error for ${item.region_id}: ${item.crop_url}`);
                      setMultiItems(prev => {
                        const copy = [...prev];
                        copy[idx].image_failed = true;
                        return copy;
                      });
                    }}
                    style={{
                      width: '100%',
                      height: '180px',
                      objectFit: 'contain',
                      background: 'rgba(0, 0, 0, 0.5)',
                      borderRadius: '10px',
                      marginBottom: '0.85rem'
                    }}
                  />
                ) : (
                  <div style={{
                    width: '100%',
                    height: '180px',
                    background: 'rgba(239, 68, 68, 0.12)',
                    border: '1px solid #EF4444',
                    borderRadius: '10px',
                    marginBottom: '0.85rem',
                    display: 'flex',
                    flexDirection: 'column',
                    alignItems: 'center',
                    justifyContent: 'center',
                    color: '#FCA5A5',
                    fontSize: '0.85rem',
                    fontWeight: 700,
                    gap: '0.35rem'
                  }}>
                    <AlertTriangle size={22} />
                    <span>Crop unavailable ({item.region_id})</span>
                  </div>
                )}

                {/* Styled Badges */}
                <div className="card-meta" style={{ marginBottom: '0.85rem', flexWrap: 'wrap', gap: '0.4rem' }}>
                  <span className="badge" style={{ background: 'rgba(99, 102, 241, 0.2)', color: '#A5B4FC', textTransform: 'capitalize' }}>
                    {item.metadata.style || 'Casual'}
                  </span>
                  <span className="badge" style={{ background: 'rgba(16, 185, 129, 0.2)', color: '#34D399' }}>
                    Formality: {item.metadata.formality}/10
                  </span>
                  <span className="badge" style={{ background: 'rgba(255,255,255,0.08)', color: '#9CA3AF' }}>
                    {Math.round((item.metadata.confidence || 0.0) * 100)}% Conf.
                  </span>
                </div>

                {item.metadata.needs_confirmation && (
                  <div style={{ background: 'rgba(234, 179, 8, 0.15)', border: '1px solid #EAB308', borderRadius: '8px', padding: '0.65rem', marginBottom: '0.85rem' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '0.35rem', color: '#FDE047', fontWeight: 600, fontSize: '0.8rem', marginBottom: '0.35rem' }}>
                      <HelpCircle size={14} /> Low Confidence Prediction — Select Fit:
                    </div>
                    <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.35rem' }}>
                      {FIT_OPTIONS.map(fitOpt => (
                        <button
                          key={fitOpt}
                          type="button"
                          onClick={() => updateMultiItemField(idx, 'fit', fitOpt)}
                          style={{
                            padding: '0.2rem 0.5rem',
                            fontSize: '0.75rem',
                            borderRadius: '4px',
                            background: item.metadata.fit === fitOpt ? '#6366F1' : 'rgba(255,255,255,0.1)',
                            color: 'white',
                            border: 'none',
                            cursor: 'pointer'
                          }}
                        >
                          {fitOpt}
                        </button>
                      ))}
                    </div>
                  </div>
                )}

                <div className="form-group" style={{ marginBottom: '0.65rem' }}>
                  <label className="form-label">Title</label>
                  <input
                    type="text"
                    className="form-input"
                    value={item.title}
                    onChange={(e) => {
                      const val = e.target.value;
                      setMultiItems(prev => {
                        const copy = [...prev];
                        copy[idx].title = val;
                        return copy;
                      });
                    }}
                  />
                </div>

                <div className="form-group" style={{ marginBottom: '0.65rem' }}>
                  <label className="form-label">Category</label>
                  <select
                    className="form-input"
                    value={item.category}
                    onChange={(e) => updateMultiItemCategory(idx, e.target.value)}
                  >
                    {CATEGORIES.map(cat => (
                      <option key={cat} value={cat}>{cat}</option>
                    ))}
                  </select>
                </div>

                <div className="form-group" style={{ marginBottom: '0.25rem' }}>
                  <label className="form-label">Color</label>
                  <select
                    className="form-input"
                    style={{ textTransform: 'capitalize' }}
                    value={item.metadata.primary_color}
                    onChange={(e) => updateMultiItemField(idx, 'primary_color', e.target.value)}
                  >
                    {COLORS.map(c => (
                      <option key={c} value={c}>{c}</option>
                    ))}
                  </select>
                </div>
              </div>
            ))}
          </div>

          <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '0.75rem', paddingTop: '1rem', borderTop: '1px solid var(--border-glass)' }}>
            <button className="btn btn-secondary" onClick={() => setStep('upload')}>Cancel</button>
            <button className="btn btn-primary" disabled={saving} onClick={handleSaveMultiBatch}>
              {saving ? <RefreshCw className="spin" size={16} /> : <CheckCircle size={16} />}
              <span>{saving ? 'Saving Selected Items...' : 'Add Selected Items to Wardrobe'}</span>
            </button>
          </div>
        </div>
      ) : (
        /* Single Item Review Screen */
        <div className="glass-card" style={{ padding: '1.5rem' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem' }}>
            <h2 style={{ fontSize: '1.35rem', fontWeight: 800, color: 'white' }}>Review & Save Wardrobe Item</h2>
            <button className="btn btn-secondary" onClick={() => setStep('upload')}>
              <ArrowLeft size={16} /> Upload Another
            </button>
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '1.5rem', marginBottom: '1.5rem' }}>
            <div>
              {metadata.crop_url ? (
                <img src={metadata.crop_url} alt={metadata.title} style={{ width: '100%', height: '280px', objectFit: 'contain', background: 'rgba(0,0,0,0.5)', borderRadius: '14px', border: '1px solid var(--border-glass)' }} />
              ) : (
                <img src={previewUrl} alt="Original" style={{ width: '100%', height: '280px', objectFit: 'contain', background: 'rgba(0,0,0,0.5)', borderRadius: '14px', border: '1px solid var(--border-glass)' }} />
              )}
            </div>

            <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
              <div className="form-group">
                <label className="form-label">Title</label>
                <input
                  type="text"
                  className="form-input"
                  value={metadata.title}
                  onChange={(e) => setMetadata({ ...metadata, title: e.target.value })}
                />
              </div>

              <div className="form-group">
                <label className="form-label">Category</label>
                <select
                  className="form-input"
                  value={metadata.category}
                  onChange={(e) => setMetadata({ ...metadata, category: e.target.value, subcategory: e.target.value })}
                >
                  {CATEGORIES.map(cat => (
                    <option key={cat} value={cat}>{cat}</option>
                  ))}
                </select>
              </div>

              <div className="form-group">
                <label className="form-label">Color</label>
                <select
                  className="form-input"
                  style={{ textTransform: 'capitalize' }}
                  value={metadata.primary_color}
                  onChange={(e) => setMetadata({ ...metadata, primary_color: e.target.value })}
                >
                  {COLORS.map(c => (
                    <option key={c} value={c}>{c}</option>
                  ))}
                </select>
              </div>
            </div>
          </div>

          <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '0.75rem', paddingTop: '1rem', borderTop: '1px solid var(--border-glass)' }}>
            <button className="btn btn-secondary" onClick={() => setStep('upload')}>Cancel</button>
            <button className="btn btn-primary" disabled={saving} onClick={handleSaveSingleItem}>
              {saving ? <RefreshCw className="spin" size={16} /> : <CheckCircle size={16} />}
              <span>{saving ? 'Saving...' : 'Save Item'}</span>
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
