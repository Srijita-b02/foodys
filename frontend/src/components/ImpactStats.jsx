import { useEffect, useState } from 'react'
import { apiRequest } from '../api'

function ImpactStats({ token }) {
  const [statistics, setStatistics] = useState(null)
  const [message, setMessage] = useState('')

  useEffect(() => {
    let ignore = false

    apiRequest('/statistics/impact', { token })
      .then((data) => {
        if (!ignore) {
          setStatistics(data)
        }
      })
      .catch((error) => {
        if (!ignore) {
          setMessage(error.message)
        }
      })

    return () => {
      ignore = true
    }
  }, [token])

  return (
    <section className="content-card">
      <div className="section-heading">
        <div>
          <h2>Community impact</h2>
          <p>Live totals calculated from completed database records.</p>
        </div>
      </div>

      {message && (
        <p className="form-message form-error" role="alert">
          {message}
        </p>
      )}

      <div className="stats-grid">
        <div className="stat-card">
          <span>Quantity delivered</span>
          <strong>{statistics?.delivered_quantity ?? '—'}</strong>
        </div>
        <div className="stat-card">
          <span>Completed deliveries</span>
          <strong>{statistics?.completed_deliveries ?? '—'}</strong>
        </div>
        <div className="stat-card">
          <span>Fulfilled requests</span>
          <strong>{statistics?.fulfilled_requests ?? '—'}</strong>
        </div>
      </div>
    </section>
  )
}

export default ImpactStats
