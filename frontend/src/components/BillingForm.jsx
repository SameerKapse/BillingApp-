import React, { useState, useMemo } from 'react';
import { api } from '../api';
import { Plus, Trash2, Download, CheckCircle2, AlertCircle, RefreshCw } from 'lucide-react';

export default function BillingForm({ onBillCreated }) {
  const initialCustomerState = {
    customer_name: '',
    customer_email: '',
    customer_phone: '',
    customer_address: '',
    notes: 'Thank you for your business! Payment is due within 15 days.',
  };

  const initialItem = { name: '', qty: 1, unit_price: 0 };

  const [customer, setCustomer] = useState(initialCustomerState);
  const [items, setItems] = useState([initialItem]);
  const [taxRate, setTaxRate] = useState(10); // 10% default
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [lastCreatedBill, setLastCreatedBill] = useState(null);

  // Auto calculate totals
  const subtotal = useMemo(() => {
    return items.reduce((acc, item) => {
      const q = parseFloat(item.qty) || 0;
      const p = parseFloat(item.unit_price) || 0;
      return acc + q * p;
    }, 0);
  }, [items]);

  const taxAmount = useMemo(() => {
    return subtotal * ((parseFloat(taxRate) || 0) / 100);
  }, [subtotal, taxRate]);

  const grandTotal = useMemo(() => {
    return subtotal + taxAmount;
  }, [subtotal, taxAmount]);

  const handleCustomerChange = (e) => {
    setCustomer({ ...customer, [e.target.name]: e.target.value });
  };

  const handleItemChange = (index, field, value) => {
    const newItems = [...items];
    newItems[index][field] = value;
    setItems(newItems);
  };

  const addItemRow = () => {
    setItems([...items, { name: '', qty: 1, unit_price: 0 }]);
  };

  const removeItemRow = (index) => {
    if (items.length <= 1) return;
    setItems(items.filter((_, i) => i !== index));
  };

  const resetForm = () => {
    setCustomer(initialCustomerState);
    setItems([initialItem]);
    setTaxRate(10);
    setLastCreatedBill(null);
    setError('');
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLastCreatedBill(null);

    // Validation
    if (!customer.customer_name.trim()) {
      setError('Please provide a customer name.');
      return;
    }

    const validItems = items.filter((item) => item.name.trim() !== '');
    if (validItems.length === 0) {
      setError('Please add at least one item with a valid description.');
      return;
    }

    setLoading(true);

    try {
      const payload = {
        ...customer,
        tax_rate: parseFloat(taxRate) || 0,
        items: validItems.map((item) => ({
          name: item.name.trim(),
          qty: parseFloat(item.qty) || 1,
          unit_price: parseFloat(item.unit_price) || 0,
        })),
      };

      const result = await api.createBill(payload);
      setLastCreatedBill(result.bill);

      // Auto-trigger PDF download
      await api.downloadBill(result.bill.id, result.bill.invoice_number);

      if (onBillCreated) {
        onBillCreated(result.bill);
      }
    } catch (err) {
      setError(err.message || 'Failed to generate and save invoice');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      {lastCreatedBill && (
        <div className="alert alert-success" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <CheckCircle2 size={20} />
            <span>
              Invoice <b>{lastCreatedBill.invoice_number}</b> saved to database & downloaded successfully!
            </span>
          </div>
          <div style={{ display: 'flex', gap: '0.5rem' }}>
            <button
              type="button"
              className="btn btn-sm btn-secondary"
              onClick={() => api.downloadBill(lastCreatedBill.id, lastCreatedBill.invoice_number)}
            >
              <Download size={14} /> Download Again
            </button>
            <button type="button" className="btn btn-sm btn-secondary" onClick={resetForm}>
              <RefreshCw size={14} /> New Invoice
            </button>
          </div>
        </div>
      )}

      {error && (
        <div className="alert alert-error">
          <AlertCircle size={20} />
          <span>{error}</span>
        </div>
      )}

      <form onSubmit={handleSubmit}>
        <div className="card">
          <h3 className="card-title">Customer Details</h3>
          <div className="form-grid-2">
            <div className="form-group">
              <label>Customer Name *</label>
              <input
                type="text"
                name="customer_name"
                className="input-field"
                placeholder="e.g. John Doe / Acme Corp"
                value={customer.customer_name}
                onChange={handleCustomerChange}
                required
              />
            </div>
            <div className="form-group">
              <label>Customer Email</label>
              <input
                type="email"
                name="customer_email"
                className="input-field"
                placeholder="e.g. customer@example.com"
                value={customer.customer_email}
                onChange={handleCustomerChange}
              />
            </div>
          </div>

          <div className="form-grid-2">
            <div className="form-group">
              <label>Customer Phone</label>
              <input
                type="text"
                name="customer_phone"
                className="input-field"
                placeholder="e.g. +1 (555) 019-2834"
                value={customer.customer_phone}
                onChange={handleCustomerChange}
              />
            </div>
            <div className="form-group">
              <label>Billing Address</label>
              <input
                type="text"
                name="customer_address"
                className="input-field"
                placeholder="e.g. 456 Market St, Suite 100, Springfield"
                value={customer.customer_address}
                onChange={handleCustomerChange}
              />
            </div>
          </div>
        </div>

        <div className="card">
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
            <h3 className="card-title" style={{ margin: 0 }}>Invoice Items</h3>
            <button type="button" className="btn btn-secondary btn-sm" onClick={addItemRow}>
              <Plus size={16} /> Add Item Row
            </button>
          </div>

          <div className="table-wrapper">
            <table className="table">
              <thead>
                <tr>
                  <th style={{ width: '40%' }}>Item Description</th>
                  <th style={{ width: '15%' }}>Quantity</th>
                  <th style={{ width: '20%' }}>Unit Price ($)</th>
                  <th style={{ width: '20%' }}>Total ($)</th>
                  <th style={{ width: '5%', textAlign: 'center' }}>Action</th>
                </tr>
              </thead>
              <tbody>
                {items.map((item, index) => {
                  const lineTotal = ((parseFloat(item.qty) || 0) * (parseFloat(item.unit_price) || 0)).toFixed(2);
                  return (
                    <tr key={index}>
                      <td>
                        <input
                          type="text"
                          className="input-field"
                          placeholder="e.g. Web Development Services"
                          value={item.name}
                          onChange={(e) => handleItemChange(index, 'name', e.target.value)}
                          required
                        />
                      </td>
                      <td>
                        <input
                          type="number"
                          step="any"
                          min="0.01"
                          className="input-field"
                          value={item.qty}
                          onChange={(e) => handleItemChange(index, 'qty', e.target.value)}
                          required
                        />
                      </td>
                      <td>
                        <input
                          type="number"
                          step="0.01"
                          min="0"
                          className="input-field"
                          value={item.unit_price}
                          onChange={(e) => handleItemChange(index, 'unit_price', e.target.value)}
                          required
                        />
                      </td>
                      <td style={{ fontWeight: '600', color: '#1e3a8a' }}>
                        ${lineTotal}
                      </td>
                      <td style={{ textAlign: 'center' }}>
                        <button
                          type="button"
                          className="btn btn-danger btn-sm"
                          onClick={() => removeItemRow(index)}
                          disabled={items.length <= 1}
                          title="Delete item"
                        >
                          <Trash2 size={16} />
                        </button>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: '1fr 320px', gap: '2rem', alignItems: 'start' }}>
            <div>
              <div className="form-group" style={{ marginBottom: '1rem' }}>
                <label>Tax Rate (%)</label>
                <input
                  type="number"
                  step="0.1"
                  min="0"
                  max="100"
                  className="input-field"
                  style={{ maxWidth: '140px' }}
                  value={taxRate}
                  onChange={(e) => setTaxRate(e.target.value)}
                />
              </div>

              <div className="form-group">
                <label>Notes / Terms</label>
                <textarea
                  name="notes"
                  className="textarea-field"
                  value={customer.notes}
                  onChange={handleCustomerChange}
                  placeholder="Additional notes, payment instructions, etc."
                />
              </div>
            </div>

            <div className="totals-box">
              <div className="totals-row">
                <span>Subtotal:</span>
                <span>${subtotal.toFixed(2)}</span>
              </div>
              <div className="totals-row">
                <span>Tax ({taxRate}%):</span>
                <span>${taxAmount.toFixed(2)}</span>
              </div>
              <div className="totals-row grand-total">
                <span>Grand Total:</span>
                <span>${grandTotal.toFixed(2)}</span>
              </div>
            </div>
          </div>

          <div style={{ marginTop: '2rem', display: 'flex', justifyContent: 'flex-end', gap: '1rem' }}>
            <button type="button" className="btn btn-secondary" onClick={resetForm} disabled={loading}>
              Clear Form
            </button>
            <button type="submit" className="btn btn-primary" disabled={loading} style={{ minWidth: '220px' }}>
              {loading ? (
                'Saving & Generating PDF...'
              ) : (
                <>
                  <Download size={18} /> Save & Download Bill
                </>
              )}
            </button>
          </div>
        </div>
      </form>
    </div>
  );
}
