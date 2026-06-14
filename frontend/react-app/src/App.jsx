import React, { useEffect, useState } from 'react'
import './styles.css'

const API_BASE = import.meta.env.VITE_API_BASE || 'http://localhost:8000'

export default function App() {
  const today = new Date().toISOString().split('T')[0]
  const [payPeriodPointValue, setPayPeriodPointValue] = useState(() => {
    try {
      const raw = localStorage.getItem('payPeriodPointValue')
      return raw ? Number(raw) : 0.007
    } catch (e) {
      return 0.007
    }
  })
  const [payPeriodSlot, setPayPeriodSlot] = useState(() => {
    try {
      const raw = localStorage.getItem('payPeriodSlot')
      if (raw === 'first' || raw === 'second') return raw
    } catch (e) {}
    const d = new Date()
    return d.getDate() <= 15 ? 'first' : 'second'
  })
  const [form, setForm] = useState({
    shift_date: today,
    role: 'driver',
    points: 0,
    hours: 0,
  })
  const [netPercent, setNetPercent] = useState(() => {
    try {
      const raw = localStorage.getItem('expectedNetPercent')
      return raw ? Number(raw) : 85
    } catch (e) {
      return 85
    }
  })
  const [rows, setRows] = useState([])
  const [editingId, setEditingId] = useState(null)
  const [editForm, setEditForm] = useState({})
  const [loading, setLoading] = useState(false)
  const [showAddForm, setShowAddForm] = useState(true)

  useEffect(() => {
    fetchThisMonth()
  }, [])

  // persist pay period settings locally so user edits survive reloads
  useEffect(() => {
    try {
      localStorage.setItem('payPeriodPointValue', String(payPeriodPointValue))
      localStorage.setItem('payPeriodSlot', payPeriodSlot)
      localStorage.setItem('expectedNetPercent', String(netPercent))
    } catch (e) {
      // ignore
    }
  }, [payPeriodPointValue, payPeriodSlot])

  async function postShift(payload) {
    const res = await fetch(`${API_BASE}/shifts/`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    })
    return res.json()
  }

  function lastDayOfMonth(year, monthIndex) {
    return new Date(year, monthIndex + 1, 0).getDate()
  }

  function getPayPeriodRangeForDate(d) {
    const date = new Date(d)
    const year = date.getFullYear()
    const month = date.getMonth() // 0-indexed
    if (date.getDate() <= 15) {
      const start = `${year}-${String(month + 1).padStart(2, '0')}-01`
      const end = `${year}-${String(month + 1).padStart(2, '0')}-15`
      return { start, end, label: `${year}-${String(month + 1).padStart(2, '0')} 1st–15th` }
    } else {
      const last = lastDayOfMonth(year, month)
      const start = `${year}-${String(month + 1).padStart(2, '0')}-16`
      const end = `${year}-${String(month + 1).padStart(2, '0')}-${String(last).padStart(2, '0')}`
      return { start, end, label: `${year}-${String(month + 1).padStart(2, '0')} 16th–${last}` }
    }
  }

  function buildRecentPayPeriods(count = 6) {
    const periods = []
    const now = new Date()
    // build periods backwards from current paycheck
    let cursor = getPayPeriodRangeForDate(now)
    for (let i = 0; i < count; i++) {
      periods.push(cursor)
      // move cursor to previous period: if current was first (1-15), previous is second of prior month
      const [y, m] = cursor.start.split('-')
      let year = Number(y)
      let month = Number(m) - 1 // 0-index
      if (cursor.start.endsWith('-01')) {
        // previous is prior month's 16th–end
        month = month - 1
        if (month < 0) { month = 11; year = year - 1 }
        const last = lastDayOfMonth(year, month)
        const start = `${year}-${String(month + 1).padStart(2, '0')}-16`
        const end = `${year}-${String(month + 1).padStart(2, '0')}-${String(last).padStart(2, '0')}`
        cursor = { start, end, label: `${year}-${String(month + 1).padStart(2, '0')} 16th–${last}` }
      } else {
        // cursor was 16th–end; previous is same month's 1-15
        const year2 = year
        const month2 = month
        const start = `${year2}-${String(month2 + 1).padStart(2, '0')}-01`
        const end = `${year2}-${String(month2 + 1).padStart(2, '0')}-15`
        cursor = { start, end, label: `${year2}-${String(month2 + 1).padStart(2, '0')} 1st–15th` }
      }
    }
    return periods
  }

  const [recentPeriods] = useState(() => buildRecentPayPeriods(12))
  const [selectedPeriodIndex, setSelectedPeriodIndex] = useState(0)

  async function fetchThisMonth(startArg, endArg) {
    setLoading(true)
    try {
      const now = new Date()
      let start, end
      if (startArg && endArg) {
        start = startArg
        end = endArg
      } else {
        // default to currently selected paycheck
        const p = recentPeriods[selectedPeriodIndex] || getPayPeriodRangeForDate(now)
        start = p.start
        end = p.end
      }
      const res = await fetch(`${API_BASE}/shifts/${start}/${end}`)
      const j = await res.json()
      setRows(j.rows || [])
    } catch (e) {
      console.error(e)
    }
    setLoading(false)
  }

  function getPayPeriodSlotForDate(dateStr) {
    const d = new Date(dateStr)
    if (isNaN(d)) return null
    return d.getDate() <= 15 ? 'first' : 'second'
  }

  function computeGrossForRow(r) {
    // prefer server-calculated when we are not overriding
    const isDriver = (r.role || (Number(r.tipped_hours||0) > 0 ? 'driver' : 'cashier')) === 'driver'
    const selectedPeriod = recentPeriods[selectedPeriodIndex]
    const displayedSlot = selectedPeriod ? (selectedPeriod.start && selectedPeriod.start.endsWith('-01') ? 'first' : 'second') : payPeriodSlot
    const inSelected = getPayPeriodSlotForDate(r.shift_date) === displayedSlot
    if (isDriver && inSelected) {
      const tips = Number(r.tipped_hours || 0)
      const pts = Number(r.points || 0)
      const pv = Number(payPeriodPointValue || 0)
      const untipped = Number(r.untipped_hours || 0)
      return tips * 5.5 + pts * pv + untipped * 15.0
    }
    // fallback to server value or compute from stored point_value
    if (typeof r.total_gross !== 'undefined') return r.total_gross
    const unt = Number(r.untipped_hours || 0)
    const tip = Number(r.tipped_hours || 0)
    const p = Number(r.points || 0)
    const pv2 = Number(r.point_value || payPeriodPointValue || 0)
    return unt * 15.0 + tip * 5.5 + p * pv2
  }

  async function deleteShift(id) {
    if (!id) return
    if (!window.confirm('Delete this shift?')) return
    try {
      const res = await fetch(`${API_BASE}/shifts/${id}`, { method: 'DELETE' })
      const j = await res.json()
      if (res.ok) {
        fetchThisMonth()
      } else {
        alert('Delete failed: ' + (j.detail || JSON.stringify(j)))
      }
    } catch (e) {
      console.error(e)
      alert('Delete failed: ' + e.message)
    }
  }

  async function updateShift(id, payload) {
    const res = await fetch(`${API_BASE}/shifts/${id}`, {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    })
    return res.json()
  }

  // Authentication removed for this iteration

  const onSubmit = async (e) => {
    e.preventDefault()
    const hoursVal = Number(form.hours || 0)
    const payload = {
      shift_date: form.shift_date,
      role: form.role,
      points: Number(form.points),
      tipped_hours: form.role === 'driver' ? hoursVal : 0,
      untipped_hours: form.role === 'cashier' ? hoursVal : 0,
      point_value: Number(payPeriodPointValue),
    }
    await postShift(payload)
    setForm({ ...form, shift_date: today, points: 0, hours: 0 })
    fetchThisMonth()
  }

  return (
    <div className="app-container">
      <h1 className="header">Pay Tracker</h1>

      <div className="controls">
        <div style={{ marginBottom: 8 }}>
          <button className="btn btn-primary" type="button" onClick={() => {
            setForm({ shift_date: today, role: 'driver', points: 0, hours: 0 })
            setShowAddForm(s => !s)
            // focus after render
            setTimeout(() => {
              const el = document.querySelector('.shift-form')
              if (el) {
                el.scrollIntoView({ behavior: 'smooth', block: 'center' })
                const inp = el.querySelector('input[type="date"]')
                if (inp) inp.focus()
              }
            }, 100)
          }}>{showAddForm ? 'Hide Add Shift' : 'Add Shift'}</button>
        </div>

        {showAddForm && (
          <form onSubmit={onSubmit} className="shift-form">
          <div className="form-row">
            <label>Date</label>
            <input className="input" type="date" value={form.shift_date} onChange={e => setForm({ ...form, shift_date: e.target.value })} required />
          </div>

          <div className="form-row">
            <label>Role</label>
            <select className="input" value={form.role} onChange={e => setForm({ ...form, role: e.target.value })}>
              <option value="driver">Driver</option>
              <option value="cashier">Cashier</option>
            </select>
          </div>

          {form.role === 'driver' && (
            <div className="form-row">
              <label>Points</label>
              <input className="input" placeholder="Points" type="number" value={form.points} onChange={e => setForm({ ...form, points: e.target.value })} />
            </div>
          )}

          <div className="form-row">
            <label>Hours</label>
            <input className="input" placeholder="Hours" type="number" step="0.25" value={form.hours} onChange={e => setForm({ ...form, hours: e.target.value })} />
          </div>

          <div className="form-actions">
            <button className="btn btn-primary" type="submit">Save</button>
            <button className="btn btn-secondary" type="button" onClick={fetchThisMonth}>Refresh</button>
          </div>
          </form>
        )}
        </div>

      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div>
          <h2>Shifts</h2>
          <div style={{ fontSize: 12, color: '#666' }}>{(recentPeriods[selectedPeriodIndex] || {}).label}</div>
        </div>
        <div style={{ display: 'flex', gap: 8, alignItems: 'center' }}>
          <label style={{ fontSize: 12 }}>Period</label>
          <select className="input" value={selectedPeriodIndex} onChange={e => { setSelectedPeriodIndex(Number(e.target.value)); setTimeout(() => fetchThisMonth(), 0) }}>
            {recentPeriods.map((p, idx) => (
              <option key={p.start + p.end} value={idx}>{p.label}</option>
            ))}
          </select>
        </div>
      </div>
      <div className="cards-row">
        <div className="summary-card">
          <strong>Cashier hours</strong>
          <div>{rows.reduce((s, r) => s + (Number(r.untipped_hours || 0)), 0)}</div>
        </div>
        <div className="summary-card">
          <strong>Driver hours</strong>
          <div>{rows.reduce((s, r) => s + (Number(r.tipped_hours || 0)), 0)}</div>
        </div>
        <div className="summary-card">
          <strong>Total hours</strong>
          <div>{rows.reduce((s, r) => s + (Number(r.tipped_hours || 0) + Number(r.untipped_hours || 0)), 0)}</div>
        </div>
        <div className="summary-card">
          <strong>Total gross</strong>
          <div>{rows.reduce((s, r) => s + computeGrossForRow(r), 0).toFixed(2)}</div>
        </div>
          <div className="summary-card">
            <strong>Expected net</strong>
            <div>{rows.reduce((s, r) => s + computeGrossForRow(r) * (netPercent/100), 0).toFixed(2)}</div>
          </div>
          <div className="summary-card">
            <strong>Dollars per point</strong>
            <div style={{ display: 'flex', gap: 8, alignItems: 'center' }}>
              <input className="input" type="number" step="0.0001" value={payPeriodPointValue} onChange={e => setPayPeriodPointValue(Number(e.target.value))} />
              <select className="input" value={payPeriodSlot} onChange={e => setPayPeriodSlot(e.target.value)}>
                <option value="first">1st–15th</option>
                <option value="second">16th–end</option>
              </select>
            </div>
          </div>
            <div className="summary-card">
              <strong>Expected net %</strong>
              <div style={{ display: 'flex', gap: 8, alignItems: 'center' }}>
                <input className="input" type="number" step="0.1" value={netPercent} onChange={e => setNetPercent(Number(e.target.value))} />
                <div style={{ paddingLeft: 4 }}>%</div>
              </div>
            </div>
      </div>

      {loading ? <div>Loading…</div> : (
        <table className="shifts-table">
          <thead>
            <tr>
              <th>Date</th>
              <th>Role</th>
              <th>Points</th>
              <th>Total Hours</th>
              <th>Total Gross</th>
              <th>Expected Net</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {rows.map(r => {
              const gross = computeGrossForRow(r)
              const totalHours = Number(r.tipped_hours || 0) + Number(r.untipped_hours || 0)
              const grossHr = totalHours > 0 ? (gross / totalHours).toFixed(2) : (0).toFixed(2)
              return (
                <tr key={r.id || r.shift_date}>
                  <td>
                    {editingId === r.id ? (
                      <input className="input" type="date" value={editForm.shift_date} onChange={e => setEditForm({ ...editForm, shift_date: e.target.value })} />
                    ) : (
                      r.shift_date
                    )}
                  </td>
                  <td>
                    {editingId === r.id ? (
                      <select className="input" value={editForm.role} onChange={e => setEditForm({ ...editForm, role: e.target.value })}>
                        <option value="driver">Driver</option>
                        <option value="cashier">Cashier</option>
                      </select>
                    ) : (
                      r.role || (Number(r.tipped_hours||0) > 0 ? 'driver' : 'cashier')
                    )}
                  </td>
                  <td>
                    {editingId === r.id ? (
                      <input className="input" type="number" value={editForm.points} onChange={e => setEditForm({ ...editForm, points: Number(e.target.value) })} />
                    ) : (
                      r.points || ''
                    )}
                  </td>
                  <td>
                    {editingId === r.id ? (
                      <input className="input" type="number" step="0.25" value={editForm.hours} onChange={e => setEditForm({ ...editForm, hours: Number(e.target.value) })} />
                    ) : (
                      `${totalHours}`
                    )}
                  </td>
                  <td>{gross}</td>
                  <td>{grossHr}</td>
                  <td>{(gross * (netPercent/100)).toFixed(2)}</td>
                  <td>
                    {editingId === r.id ? (
                      <>
                        <button className="btn btn-primary" onClick={async () => {
                          const hoursVal = Number(editForm.hours || 0)
                          const payload = {
                            shift_date: editForm.shift_date,
                            role: editForm.role,
                            points: Number(editForm.points || 0),
                            tipped_hours: editForm.role === 'driver' ? hoursVal : 0,
                            untipped_hours: editForm.role === 'cashier' ? hoursVal : 0,
                            point_value: Number(editForm.point_value ?? r.point_value ?? payPeriodPointValue),
                          }
                          await updateShift(r.id, payload)
                          setEditingId(null)
                          setEditForm({})
                          fetchThisMonth()
                        }}>Save</button>
                        <button className="btn btn-secondary" onClick={() => { setEditingId(null); setEditForm({}) }} style={{ marginLeft: 8 }}>Cancel</button>
                      </>
                    ) : (
                      <>
                        <button className="btn" onClick={() => { setEditingId(r.id); setEditForm({ shift_date: r.shift_date, role: r.role || (Number(r.tipped_hours||0) > 0 ? 'driver' : 'cashier'), points: r.points || 0, hours: (Number(r.tipped_hours||0) + Number(r.untipped_hours||0)), point_value: r.point_value }) }}>Edit</button>
                        <button className="btn btn-danger" onClick={() => deleteShift(r.id)} style={{ marginLeft: 8 }}>Delete</button>
                      </>
                    )}
                  </td>
                </tr>
              )
            })}
          </tbody>
        </table>
      )}
    </div>
  )
}
