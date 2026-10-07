import PageHeader from '../components/PageHeader'
import StatusBadge from '../components/StatusBadge'

function MyRequests() {
  return (
    <>
      <PageHeader
        title="My requests"
        description="Track food requests made by your organization."
      />

      <section className="content-card">
        <div className="list-row">
          <div>
            <strong>Meals for 25 people</strong>
            <p>Required today · 7:00 PM</p>
          </div>
          <StatusBadge status="Available" />
        </div>

        <div className="list-row">
          <div>
            <strong>15 packed meals</strong>
            <p>Required tomorrow · 12:00 PM</p>
          </div>
          <StatusBadge status="Reserved" />
        </div>
      </section>
    </>
  )
}

export default MyRequests