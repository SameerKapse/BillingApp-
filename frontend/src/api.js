// In dev, Vite proxies /api to http://127.0.0.1:5000
// In production, Flask serves both /api and static files from the same origin
const BASE_URL = '';

async function request(endpoint, options = {}) {
  const defaultOptions = {
    headers: {
      'Content-Type': 'application/json',
    },
    credentials: 'include',
  };

  const response = await fetch(`${BASE_URL}${endpoint}`, {
    ...defaultOptions,
    ...options,
    headers: {
      ...defaultOptions.headers,
      ...options.headers,
    },
  });

  const contentType = response.headers.get('content-type');
  let data = null;
  if (contentType && contentType.includes('application/json')) {
    data = await response.json();
  }

  if (!response.ok) {
    const errorMsg = (data && data.error) || response.statusText || 'An unexpected error occurred';
    throw new Error(errorMsg);
  }

  return data;
}

export const api = {
  // Auth
  login: (username, password) =>
    request('/api/login', {
      method: 'POST',
      body: JSON.stringify({ username, password }),
    }),

  register: (username, password) =>
    request('/api/register', {
      method: 'POST',
      body: JSON.stringify({ username, password }),
    }),

  logout: () =>
    request('/api/logout', {
      method: 'POST',
    }),

  getMe: () => request('/api/me'),

  // Bills
  getBills: (search = '') => {
    const query = search ? `?search=${encodeURIComponent(search)}` : '';
    return request(`/api/bills${query}`);
  },

  createBill: (billData) =>
    request('/api/bills', {
      method: 'POST',
      body: JSON.stringify(billData),
    }),

  downloadBill: async (billId, invoiceNumber) => {
    const response = await fetch(`${BASE_URL}/api/bills/${billId}/download`, {
      credentials: 'include',
    });
    if (!response.ok) {
      throw new Error('Failed to download invoice PDF');
    }
    const blob = await response.blob();
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${invoiceNumber || 'invoice'}.pdf`;
    document.body.appendChild(a);
    a.click();
    a.remove();
    window.URL.revokeObjectURL(url);
  },
};
