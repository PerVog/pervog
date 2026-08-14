import React from 'react';
import { 
  Shirt, 
  Sparkles, 
  Compass, 
  ShoppingBag, 
  Heart, 
  User, 
  Settings as SettingsIcon, 
  PlusCircle,
  Sun,
  Layers
} from 'lucide-react';

const NAV_ITEMS = [
  { id: 'dashboard', label: 'Dashboard', icon: Compass },
  { id: 'generator', label: 'What Should I Wear?', icon: Sparkles },
  { id: 'item-match', label: 'Match an Item', icon: Layers },
  { id: 'wardrobe', label: 'My Wardrobe', icon: Shirt },
  { id: 'add-clothing', label: '+ Add Clothing', icon: PlusCircle },
  { id: 'saved-outfits', label: 'Saved Outfits', icon: Heart },
  { id: 'shopping', label: 'Wardrobe Gaps', icon: ShoppingBag },
  { id: 'profile', label: 'Style Profile', icon: User },
  { id: 'settings', label: 'Settings', icon: SettingsIcon },
];

export default function Sidebar({ activeTab, setActiveTab, isOpen, setIsOpen }) {
  return (
    <aside className={`sidebar ${isOpen ? 'open' : ''}`}>
      <div className="brand-header">
        <div className="brand-logo">A</div>
        <div>
          <h1 className="brand-title">AURA</h1>
          <span className="brand-badge">₹0 AI STYLIST</span>
        </div>
      </div>

      <ul className="nav-list">
        {NAV_ITEMS.map((item) => {
          const Icon = item.icon;
          const isActive = activeTab === item.id;
          return (
            <li key={item.id}>
              <a
                className={`nav-item ${isActive ? 'active' : ''}`}
                onClick={() => {
                  setActiveTab(item.id);
                  if (setIsOpen) setIsOpen(false);
                }}
              >
                <Icon className="nav-icon" />
                <span>{item.label}</span>
              </a>
            </li>
          );
        })}
      </ul>
    </aside>
  );
}
