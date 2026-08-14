import React, { useState } from 'react';
import Sidebar from './components/Sidebar';
import Dashboard from './pages/Dashboard';
import Wardrobe from './pages/Wardrobe';
import AddClothing from './pages/AddClothing';
import OutfitGenerator from './pages/OutfitGenerator';
import SelectItemMatch from './pages/SelectItemMatch';
import ShoppingGaps from './pages/ShoppingGaps';
import SavedOutfits from './pages/SavedOutfits';
import UserProfile from './pages/UserProfile';
import Settings from './pages/Settings';
import DebugAnalysis from './pages/DebugAnalysis';
import { Menu, X } from 'lucide-react';

export default function App() {
  const [activeTab, setActiveTab] = useState('dashboard');
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [selectedMatchItem, setSelectedMatchItem] = useState(null);

  const renderContent = () => {
    switch (activeTab) {
      case 'dashboard':
        return <Dashboard setActiveTab={setActiveTab} setSelectedMatchItem={setSelectedMatchItem} />;
      case 'generator':
        return <OutfitGenerator />;
      case 'item-match':
        return <SelectItemMatch selectedMatchItem={selectedMatchItem} setSelectedMatchItem={setSelectedMatchItem} />;
      case 'wardrobe':
        return <Wardrobe setActiveTab={setActiveTab} setSelectedMatchItem={setSelectedMatchItem} />;
      case 'add-clothing':
        return <AddClothing setActiveTab={setActiveTab} />;
      case 'saved-outfits':
        return <SavedOutfits />;
      case 'shopping':
        return <ShoppingGaps />;
      case 'profile':
        return <UserProfile />;
      case 'settings':
        return <Settings />;
      case 'debug-analysis':
        return <DebugAnalysis />;
      default:
        return <Dashboard setActiveTab={setActiveTab} setSelectedMatchItem={setSelectedMatchItem} />;
    }
  };

  return (
    <div className="app-container">
      {/* Sidebar for Desktop */}
      <Sidebar
        activeTab={activeTab}
        setActiveTab={setActiveTab}
        isOpen={sidebarOpen}
        setIsOpen={setSidebarOpen}
      />

      {/* Mobile Top Navbar */}
      <div className="mobile-nav">
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          <div className="brand-logo" style={{ width: '30px', height: '30px', fontSize: '0.9rem' }}>A</div>
          <span className="brand-title" style={{ fontSize: '1.1rem' }}>AURA</span>
        </div>

        <button className="btn-icon" onClick={() => setSidebarOpen(!sidebarOpen)}>
          {sidebarOpen ? <X size={20} /> : <Menu size={20} />}
        </button>
      </div>

      {/* Main Content Area */}
      <main className="main-content">
        {renderContent()}
      </main>
    </div>
  );
}
