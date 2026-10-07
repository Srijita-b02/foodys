import PageHeader from '../components/PageHeader'
import StatusBadge from '../components/StatusBadge'

function NgoDashboard({ onNavigate }) {
  return (
    <>
      <PageHeader
        title="Overview"
        description="Manage requests, food reservations and deliveries."
        action={() => onNavigate('request')}
        actionLabel="New request"
      />

      <section className="stats-grid">
        <div className="stat-card">
          <span>Open requests</span>
          <strong>2</strong>
        </div>

        <div className="stat-card">
          <span>Reserved pickups</span>
          <strong>3</strong>
        </div>

        <div className="stat-card">
          <span>Received</span>
          <strong>18</strong>
        </div>
      </section>

      <section className="content-card">
        <div className="section-heading">
          <div>
            <h2>Recent requests</h2>
            <p>Your organization's latest activity.</p>
          </div>
        </div>

        <div className="list-row">
          <div>
            <strong>Meals for 25 people</strong>
            <p>Created today</p>
          </div>
          <StatusBadge status="Available" />
        </div>

        <div className="list-row">
          <div>
            <strong>15 packed meals</strong>
            <p>Created yesterday</p>
          </div>
          <StatusBadge status="Reserved" />
        </div>
      </section>
    </>
  )
}

export default NgoDashboard