import PageHeader from '../components/PageHeader'
import StatusBadge from '../components/StatusBadge'

function Deliveries() {
  return (
    <>
      <PageHeader
        title="Deliveries"
        description="Track food from reservation to successful delivery."
      />

      <section className="content-card">
        <div className="list-row">
          <div>
            <strong>Vegetable meals · 20 servings</strong>
            <p>Restaurant → Hope Foundation</p>
          </div>

          <StatusBadge status="In transit" />
        </div>

        <div className="list-row">
          <div>
            <strong>Rice meals · 30 servings</strong>
            <p>Individual donor → Community Care</p>
          </div>

          <StatusBadge status="Delivered" />
        </div>
      </section>
    </>
  )
}

export default Deliveries