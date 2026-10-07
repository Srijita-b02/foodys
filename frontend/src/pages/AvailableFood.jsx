import PageHeader from '../components/PageHeader'

function AvailableFood() {
  return (
    <>
      <PageHeader
        title="Available food"
        description="Surplus food currently available from donors."
      />

      <section className="content-card">
        <div className="request-card">
          <div>
            <span className="small-label">AVAILABLE TODAY</span>
            <h3>20 vegetable meals</h3>
            <p>Restaurant donor · Adyar · Available until 6:30 PM</p>
          </div>

          <button className="orange-button">Reserve</button>
        </div>

        <div className="request-card">
          <div>
            <span className="small-label">AVAILABLE TODAY</span>
            <h3>12 bakery items</h3>
            <p>Individual donor · T. Nagar · Available until 8:00 PM</p>
          </div>

          <button className="orange-button">Reserve</button>
        </div>
      </section>
    </>
  )
}

export default AvailableFood