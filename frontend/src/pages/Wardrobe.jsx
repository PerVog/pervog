import React, { useEffect, useState } from 'react';
import { Search, Filter, Plus, Heart, CheckCircle } from 'lucide-react';
import { getWardrobe, updateWardrobeItem, deleteWardrobeItem } from '../services/api';
import WardrobeCard from '../components/WardrobeCard';

const CATEGORIES = [
  'All', 'Shirt', 'T-Shirt', 'Polo', 'Hoodie', 'Sweater', 'Jacket', 'Coat',
  'Pants', 'Jeans', 'Shorts', 'Trousers', 'Shoes', 'Sneakers', 'Boots', 'Watch', 'Belt'
];

export default function Wardrobe({ setActiveTab, setSelectedMatchItem }) {
  const [items, setItems] = useState([]);
  const [selectedCategory, setSelectedCategory] = useState('All');
  const [search, setSearch] = useState('');
  const [onlyFavorites, setOnlyFavorites] = useState(false);
  const [loading, setLoading] = useState(true);

  const loadWardrobe = async () => {
    try {
      setLoading(true);
      const params = { user_id: 1 };
      if (selectedCategory !== 'All') params.category = selectedCategory;
      if (search) params.search = search;
      if (onlyFavorites) params.is_favorite = true;

      const data = await getWardrobe(params);
      setItems(data);
    } catch (err) {
      console.error('Failed loading wardrobe:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadWardrobe();
  }, [selectedCategory, onlyFavorites]);

  const handleSearchSubmit = (e) => {
    e.preventDefault();
    loadWardrobe();
  };

  const handleToggleFavorite = async (id, isFav) => {
    try {
      await updateWardrobeItem(id, { is_favorite: isFav });
      setItems(items.map(it => it.id === id ? { ...it, is_favorite: isFav } : it));
    } catch (err) {
      console.error('Failed toggling favorite:', err);
    }
  };

  const handleToggleAvailable = async (id, isAvail) => {
    try {
      await updateWardrobeItem(id, { is_available: isAvail });
      setItems(items.map(it => it.id === id ? { ...it, is_available: isAvail } : it));
    } catch (err) {
      console.error('Failed toggling availability:', err);
    }
  };

  const handleDelete = async (id) => {
    if (!window.confirm('Delete this wardrobe item?')) return;
    try {
      await deleteWardrobeItem(id);
      setItems(items.filter(it => it.id !== id));
    } catch (err) {
      console.error('Failed deleting item:', err);
    }
  };

  const handleSelectForMatch = (item) => {
    if (setSelectedMatchItem) {
      setSelectedMatchItem(item);
      setActiveTab('item-match');
    }
  };

  return (
    <div>
      <div className="page-header">
        <div>
          <h1 className="page-title">Digital Wardrobe</h1>
          <p className="page-subtitle">{items.length} items in your closet</p>
        </div>

        <button className="btn btn-primary" onClick={() => setActiveTab('add-clothing')}>
          <Plus size={18} />
          <span>+ Add Clothing</span>
        </button>
      </div>

      {/* Search & Action Bar */}
      <div style={{ display: 'flex', gap: '1rem', flexWrap: 'wrap', marginBottom: '1.25rem' }}>
        <form onSubmit={handleSearchSubmit} style={{ flex: 1, minWidth: '240px', display: 'flex', gap: '0.5rem' }}>
          <div style={{ position: 'relative', flex: 1 }}>
            <Search size={18} style={{ position: 'absolute', left: '12px', top: '50%', transform: 'translateY(-50%)', color: '#9CA3AF' }} />
            <input
              type="text"
              placeholder="Search by title or color..."
              className="form-input"
              style={{ paddingLeft: '2.5rem' }}
              value={search}
              onChange={(e) => setSearch(e.target.value)}
            />
          </div>
          <button type="submit" className="btn btn-secondary">Search</button>
        </form>

        <button
          className={`btn ${onlyFavorites ? 'btn-primary' : 'btn-secondary'}`}
          onClick={() => setOnlyFavorites(!onlyFavorites)}
        >
          <Heart size={18} fill={onlyFavorites ? 'currentColor' : 'none'} />
          <span>Favorites</span>
        </button>
      </div>

      {/* Category Filter Pills */}
      <div className="filter-pills">
        {CATEGORIES.map((cat) => (
          <button
            key={cat}
            className={`pill ${selectedCategory === cat ? 'active' : ''}`}
            onClick={() => setSelectedCategory(cat)}
          >
            {cat}
          </button>
        ))}
      </div>

      {/* Items Grid */}
      {loading ? (
        <div className="glass-card" style={{ textAlign: 'center', padding: '3rem' }}>
          <p style={{ color: '#9CA3AF' }}>Loading digital wardrobe items...</p>
        </div>
      ) : items.length === 0 ? (
        <div className="glass-card" style={{ textAlign: 'center', padding: '3rem' }}>
          <p style={{ color: '#9CA3AF', marginBottom: '1rem' }}>No items match your filter criteria.</p>
          <button className="btn btn-primary" onClick={() => { setSelectedCategory('All'); setSearch(''); setOnlyFavorites(false); }}>
            Reset Filters
          </button>
        </div>
      ) : (
        <div className="wardrobe-grid">
          {items.map((item) => (
            <WardrobeCard
              key={item.id}
              item={item}
              onToggleFavorite={handleToggleFavorite}
              onToggleAvailable={handleToggleAvailable}
              onDelete={handleDelete}
              onSelectForMatch={handleSelectForMatch}
            />
          ))}
        </div>
      )}
    </div>
  );
}
