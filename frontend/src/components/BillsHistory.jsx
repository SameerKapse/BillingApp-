import React, { useState, useEffect } from 'react';
import { api } from '../api';
import { Download, Search, RefreshCw, FileText, AlertCircle } from 'lucide-react';

export default function BillsHistory() {
  const [bills, setBills] = useState([]);
  const [search, setSearch] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [downloadingId, setDownloadingId] = useState(null);

  const fetchBills = async (searchTerm = '') => {
    setLoading(true);
    setError('');
    try {
      const data = await api.getBills(searchTerm);
      setBills(data);
    } catch (err) {
      setError(err.message || 'Failed to load invoices');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchBills();
  }, []);

  const handleSearchSubmit = (e) => {
    e.preventDefault();
    fetchBills(search);
  };

  const handleDownload = async (bill) => {
    setDownloadingId(bill.id);
    try {
      await api.downloadBill(bill.id, bill.invoice_number);
    } catch (err) {
      alert('Error downloading invoice: ' + err.message);
    } finally {
      setDownloadingId(null);
    }
  };

  return (
    <div className="card">
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '1rem', marginBottom: '1.5rem' }}>
        <h3 className="card-title" style={{ margin: 0 }}>
          <FileText size={22} color="#2563eb" /> Saved Invoices History
        </h3>

        <div style={{ display: 'flex', gap: '0.75rem', alignItems: 'center' }}>
          <form onSubmit={handleSearchSubmit} style={{ display: 'flex', gap: '0.5rem' }}>
            <input
              type="text"
              className="input-field"
              placeholder="Search by invoice # or customer..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              style={{ width: '260px' }}
            />
            <button type="submit" className="btn btn-secondary btn-sm" title="Search">
              <Search size={16} />
            </button>
          </form>

          <button
            type="button"
            className="btn btn-secondary btn-sm"
            onClick={() => fetchBills(search)}
            title="Refresh list"
            disabled={loading}
          >
            <RefreshCw size={16} className={loading ? 'animate-spin' : ''} />
          </button>
        </div>
      </div>

      {error && (
        <div className="alert alert-error">
          <AlertCircle size={18} />
          <span>{error}</span>
        </div>
      )}

      {loading && bills.length === 0 ? (
        <div style={{ textAlign: 'center', padding: '3rem', color: '#6b7280' }}>
          Loading saved invoices from database...
        </div>
      ) : bills.length === 0 ? (
        <div style={{ textAlign: 'center', padding: '3rem', color: '#6b7280' }}>
          <FileText size={48} style={{ opacity: 0.3, marginBottom: '1rem' }} />
          <p>No invoices found. Generate your first invoice to see it here!</p>
        </div>
      ) : (
        <div className="table-wrapper">
          <table className="table">
            <thead>
              <tr>
                <th>Invoice #</th>
                <th>Customer</th>
                <th>Date</th>
                <th>Items Count</th>
                <th>Grand Total</th>
                <th>Status</th>
                <th style={{ textAlign: 'right' }}>Actions</th>
              </tr>
            </thead>
            <tbody>
              {bills.map((bill) => (
                <tr key={bill.id}>
                  <td style={{ fontWeight: '600', color: '#1e3a8a' }}>{bill.invoice_number}</td>
                  <td>
                    <div><b>{bill.customer_name}</b></div>
                    <div style={{ fontSize: '0.8rem', color: '#6b7280' }}>
                      {bill.customer_email || bill.customer_phone || 'No contact info'}
                    </div>
                  </td>
                  <td style={{ fontSize: '0.85rem', color: '#4b5563' }}>{bill.created_at}</td>
                  <td>{bill.items ? bill.items.length : 0} items</td>
                  <td style={{ fontWeight: '700', color: '#047857' }}>
                    ${parseFloat(bill.grand_total).toFixed(2)}
                  </td>
                  <td>
                    <span className="badge badge-success">Saved & Paid</span>
                  </td>
                  <td style={{ textAlign: 'right' }}>
                    <button
                      type="button"
                      className="btn btn-secondary btn-sm"
                      onClick={() => handleDownload(bill)}
                      disabled={downloadingId === bill.id}
                      title="Download Invoice PDF"
                    >
                      <Download size={14} />
                      {downloadingId === bill.id ? 'Downloading...' : 'PDF'}
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
