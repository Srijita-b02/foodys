import PageHeader from '../components/PageHeader'
import StatusBadge from '../components/StatusBadge'

function DonorDashboard({ onNavigate }) {
  return (
    <>
      <PageHeader
        title="Overview"
        description="A quick look at your food sharing activity."
        action={() => onNavigate('donate')}
        actionLabel="New donation"
      />

      <section className="stats-grid">
        <div className="stat-card">
          <span>Active donations</span>
          <strong>3</strong>
        </div>

        <div className="stat-card">
          <span>Reserved</span>
          <strong>1</strong>
        </div>

        <div className="stat-card">
          <span>Delivered</span>
          <strong>12</strong>
        </div>
      </section>

      <section className="content-card">
        <div className="section-heading">
          <div>
            <h2>Recent donations</h2>
            <p>Your latest food listings.</p>
          </div>

          <button
            className="text-button"
            onClick={() => onNavigate('donations')}
          >
            View all
          </button>
        </div>

        <div className="list-row">
          <div>
            <strong>Vegetable meals</strong>
            <p>20 servings · Today, 5:00 PM</p>
          </div>

          <StatusBadge status="Available" />
        </div>

        <div className="list-row">
          <div>
            <strong>Bread & pastries</strong>
            <p>12 servings · Today, 7:30 PM</p>
          </div>

          <StatusBadge status="Reserved" />
        </div>
      </section>
    </>
  )
}

export default DonorDashboard