import React, { useEffect, useState } from 'react';
import api from '../api/client';
import { useAuth } from '../context/AuthContext';

const emptyForm = {
  username: '',
  email: '',
  first_name: '',
  last_name: '',
  password: '',
  role: 'FACULTY',
};

export default function Users() {
  const { user: current } = useAuth();
  const [users, setUsers] = useState([]);
  const [form, setForm] = useState(emptyForm);
  const [showForm, setShowForm] = useState(false);
  const [editingId, setEditingId] = useState(null);
  const [error, setError] = useState('');

  function load() {
    api.get('/auth/users/').then((res) => setUsers(res.data.results ?? res.data));
  }

  useEffect(load, []);

  async function handleSubmit(e) {
    e.preventDefault();
    setError('');
    try {
      if (editingId) {
        const payload = { ...form };
        if (!payload.password) delete payload.password;
        await api.patch(`/auth/users/${editingId}/`, payload);
      } else {
        await api.post('/auth/users/', form);
      }
      setForm(emptyForm);
      setShowForm(false);
      setEditingId(null);
      load();
    } catch (err) {
      const data = err.response?.data;
      setError(typeof data === 'string' ? data : JSON.stringify(data || 'Could not save user.'));
    }
  }

  function startEdit(u) {
    setEditingId(u.id);
    setShowForm(true);
    setForm({
      username: u.username,
      email: u.email,
      first_name: u.first_name,
      last_name: u.last_name,
      password: '',
      role: u.role,
    });
  }

  function resetForm() {
    setShowForm(false);
    setEditingId(null);
    setForm(emptyForm);
  }

  async function patchUser(id, payload) {
    setError('');
    try {
      await api.patch(`/auth/users/${id}/`, payload);
      load();
    } catch (err) {
      const data = err.response?.data;
      setError(typeof data === 'string' ? data : JSON.stringify(data || 'Could not update user.'));
    }
  }

  async function deleteUser(id) {
    if (!window.confirm('Delete this user?')) return;
    setError('');
    try {
      await api.delete(`/auth/users/${id}/`);
      load();
    } catch (err) {
      const data = err.response?.data;
      setError(data?.detail || JSON.stringify(data || 'Could not delete user.'));
    }
  }

  return (
    <div className="p-8 max-w-5xl mx-auto">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-2xl font-bold text-slate-900">Users</h1>
          <p className="text-sm text-slate-500 mt-1">Assign Admin/Faculty roles and activate or deactivate accounts.</p>
        </div>
        <button
          type="button"
          onClick={() => { if (showForm) resetForm(); else setShowForm(true); }}
          className="bg-slate-900 text-white px-4 py-2 rounded text-sm font-semibold"
        >
          {showForm ? 'Cancel' : '+ Add user'}
        </button>
      </div>

      {error && <div className="bg-red-50 text-red-700 text-sm rounded p-3 mb-4">{error}</div>}

      {showForm && (
        <form onSubmit={handleSubmit} className="bg-white shadow rounded-lg p-6 mb-6 grid grid-cols-2 gap-4">
          <p className="col-span-2 text-sm font-semibold text-slate-700">{editingId ? 'Edit user' : 'New user'}</p>
          <input placeholder="First name" className="border rounded px-3 py-2 text-sm" value={form.first_name}
            onChange={(e) => setForm({ ...form, first_name: e.target.value })} required />
          <input placeholder="Last name" className="border rounded px-3 py-2 text-sm" value={form.last_name}
            onChange={(e) => setForm({ ...form, last_name: e.target.value })} required />
          <input placeholder="Username" className="border rounded px-3 py-2 text-sm" value={form.username}
            onChange={(e) => setForm({ ...form, username: e.target.value })} required />
          <input type="email" placeholder="Email" className="border rounded px-3 py-2 text-sm" value={form.email}
            onChange={(e) => setForm({ ...form, email: e.target.value })} required />
          <input type="password" placeholder={editingId ? 'New password (leave blank to keep)' : 'Password'}
            className="border rounded px-3 py-2 text-sm" value={form.password}
            onChange={(e) => setForm({ ...form, password: e.target.value })} minLength={editingId ? undefined : 8}
            required={!editingId} />
          <select className="border rounded px-3 py-2 text-sm" value={form.role}
            onChange={(e) => setForm({ ...form, role: e.target.value })} disabled={editingId === current?.id}>
            <option value="FACULTY">Faculty</option>
            <option value="ADMIN">Administrator</option>
          </select>
          <button type="submit" className="col-span-2 bg-slate-900 text-white py-2 rounded text-sm font-semibold">
            {editingId ? 'Update user' : 'Create user'}
          </button>
        </form>
      )}

      <div className="bg-white shadow rounded-lg divide-y">
        {users.map((u) => (
          <div key={u.id} className="flex flex-wrap items-center justify-between gap-3 p-4">
            <div>
              <p className="font-semibold text-slate-900">
                {u.first_name} {u.last_name} <span className="text-slate-400 font-normal">@{u.username}</span>
                {!u.is_active && <span className="ml-2 text-xs bg-slate-200 text-slate-600 px-2 py-0.5 rounded">Inactive</span>}
              </p>
              <p className="text-xs text-slate-500">{u.email}</p>
            </div>
            <div className="flex items-center gap-3">
              <select
                className="border rounded px-2 py-1 text-xs"
                value={u.role}
                disabled={u.id === current?.id}
                onChange={(e) => patchUser(u.id, { role: e.target.value })}
              >
                <option value="FACULTY">Faculty</option>
                <option value="ADMIN">Administrator</option>
              </select>
              <button
                type="button"
                onClick={() => patchUser(u.id, { is_active: !u.is_active })}
                className="text-xs text-slate-600 hover:underline"
              >
                {u.is_active ? 'Deactivate' : 'Activate'}
              </button>
              {u.id !== current?.id && (
                <>
                  <button type="button" onClick={() => startEdit(u)} className="text-xs text-slate-600 hover:underline">
                    Edit
                  </button>
                  <button type="button" onClick={() => deleteUser(u.id)} className="text-xs text-red-600 hover:underline">
                    Delete
                  </button>
                </>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
