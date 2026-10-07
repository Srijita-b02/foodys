import PageHeader from '../components/PageHeader'

function CreateRequest() {
  function handleSubmit(event) {
    event.preventDefault()
    console.log('Request submitted')
  }

  return (
    <>
      <PageHeader
        title="New food request"
        description="Tell nearby donors what your organization needs."
      />

      <section className="form-card">
        <form className="dashboard-form" onSubmit={handleSubmit}>
          <div>
            <label>Request title</label>
            <input
              type="text"
              name="title"
              placeholder="e.g. Meals for community dinner"
              required
            />
          </div>

          <div className="form-grid">
            <div>
              <label>Food type</label>
              <select name="foodType">
                <option>Any suitable food</option>
                <option>Cooked meals</option>
                <option>Packaged food</option>
                <option>Produce</option>
              </select>
            </div>

            <div>
              <label>Quantity required</label>
              <input type="number" name="quantity" min="1" required />
            </div>
          </div>

          <div>
            <label>Location</label>
            <input
              type="text"
              name="location"
              placeholder="Pickup / delivery area"
              required
            />
          </div>

          <div>
            <label>Required by</label>
            <input type="datetime-local" name="requiredBy" required />
          </div>

          <div>
            <label>Notes</label>
            <textarea
              name="notes"
              placeholder="Any dietary or collection information..."
              rows="4"
            />
          </div>

          <button className="orange-button form-submit" type="submit">
            Post request
          </button>
        </form>
      </section>
    </>
  )
}

export default CreateRequest