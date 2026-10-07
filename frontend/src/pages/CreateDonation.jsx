import PageHeader from '../components/PageHeader'

function CreateDonation() {
  function handleSubmit(event) {
    event.preventDefault()
    console.log('Donation submitted')
  }

  return (
    <>
      <PageHeader
        title="New donation"
        description="List surplus food for nearby NGOs."
      />

      <section className="form-card">
        <form className="dashboard-form" onSubmit={handleSubmit}>
          <div>
            <label>Food name</label>
            <input
              type="text"
              name="foodName"
              placeholder="e.g. Vegetable meals"
              required
            />
          </div>

          <div className="form-grid">
            <div>
              <label>Food type</label>
              <select name="foodType">
                <option>Cooked meal</option>
                <option>Packaged food</option>
                <option>Bakery</option>
                <option>Produce</option>
                <option>Other</option>
              </select>
            </div>

            <div>
              <label>Quantity / servings</label>
              <input
                type="number"
                name="quantity"
                min="1"
                placeholder="20"
                required
              />
            </div>
          </div>

          <div>
            <label>Allergens</label>
            <input
              type="text"
              name="allergens"
              placeholder="e.g. Dairy, nuts — or None"
            />
          </div>

          <div>
            <label>Pickup location</label>
            <input
              type="text"
              name="location"
              placeholder="Area or address"
              required
            />
          </div>

          <div>
            <label>Available until</label>
            <input type="datetime-local" name="expiry" required />
          </div>

          <button className="orange-button form-submit" type="submit">
            Create donation
          </button>
        </form>
      </section>
    </>
  )
}

export default CreateDonation