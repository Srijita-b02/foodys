import PageHeader from '../components/PageHeader'

function BrowseRequests() {
  return (
    <>
      <PageHeader
        title="Food requests"
        description="Requests posted by NGOs that may match your surplus food."
      />

      <section className="content-card">
        <div className="request-card">
          <div>
            <span className="small-label">COMMUNITY MEAL</span>
            <h3>Meals needed for 25 people</h3>
            <p>Hope Foundation · Adyar</p>
          </div>

          <button className="outline-button">Respond</button>
        </div>

        <div className="request-card">
          <div>
            <span className="small-label">FOOD REQUEST</span>
            <h3>15 packed meals required</h3>
            <p>Community Care · T. Nagar</p>
          </div>

          <button className="outline-button">Respond</button>
        </div>
      </section>
    </>
  )
}

export default BrowseRequests