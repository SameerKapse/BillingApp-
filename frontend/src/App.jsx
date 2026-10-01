import React, { useState, useEffect } from 'react';
import { api } from './api';
import Login from './components/Login';
import BillingForm from './components/BillingForm';
import BillsHistory from './components/BillsHistory';
import { Receipt, History, LogOut, FilePlus2, User } from 'lucide-react';

export default function App() {
  const [currentUser, setCurrentUser] = useState(null);
  const [loadingUser, setLoadingUser] = useState(true);
  const [activeTab, setActiveTab] = useState('create'); // 'create' | 'history'

  useEffect(() => {
    const checkAuth = async () => {
      try {
        const res = await api.getMe();
        if (res.authenticated && res.user) {
          setCurrentUser(res.user);
        }
      } catch (err) {
        console.error('Auth check error:', err);
      } finally {
        setLoadingUser(false);
      }
    };
    checkAuth();
  }, []);

  const handleLogout = async () => {
    try {
      await api.logout();
    } catch (err) {
      console.error('Logout error:', err);
    }
    setCurrentUser(null);
  };

  if (loadingUser) {
    return (
      <div style={{ minHeight: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#6b7280' }}>
        Loading Billing System...
      </div>
    );
  }

  if (!currentUser) {
    return <Login onLoginSuccess={(user) => setCurrentUser(user)} />;
  }

  return (
    <div className="app-container">
      <header className="navbar">
        <div className="brand">
          <Receipt size={28} color="#2563eb" />
          <span>Billing Pro</span>
        </div>

        <div className="nav-links">
          <button
            className={`nav-btn ${activeTab === 'create' ? 'active' : ''}`}
            onClick={() => setActiveTab('create')}
          >
            <FilePlus2 size={18} /> Create Invoice
          </button>
          <button
            className={`nav-btn ${activeTab === 'history' ? 'active' : ''}`}
            onClick={() => setActiveTab('history')}
          >
            <History size={18} /> Invoices History
          </button>
        </div>

        <div className="user-profile">
          <div className="user-tag" style={{ display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
            <User size={14} />
            <span>{currentUser.username}</span>
          </div>
          <button
            type="button"
            className="btn btn-secondary btn-sm"
            onClick={handleLogout}
            title="Sign out"
          >
            <LogOut size={14} /> Logout
          </button>
        </div>
      </header>

      <main className="main-content">
        {activeTab === 'create' ? (
          <BillingForm onBillCreated={() => {}} />
        ) : (
          <BillsHistory />
        )}
      </main>
    </div>
  );
}
