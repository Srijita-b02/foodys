import { useState } from 'react'
import PageHeader from '../components/PageHeader'
import { apiRequest } from '../api'

function CreateDonation({ token }) {
  const [message, setMessage] = useState('')
  const [isError, setIsError] = useState(false)
  const [isSubmitting, setIsSubmitting] = useState(false)

  async function handleSubmit(event) {
    event.preventDefault()
    setMessage('')
    setIsError(false)

    const formElement = event.currentTarget
    const form = new FormData(formElement)
    const preparedAt = new Date(form.get('preparedAt'))
    const expiryTime = new Date(form.get('expiryTime'))

    if (expiryTime <= preparedAt) {
      setIsError(true)
      setMessage('Available-until time must be later than preparation time.')
      return
    }

    setIsSubmitting(true)

    try {
      await apiRequest('/donations', {
        method: 'POST',
        token,
        body: {
          food_name: form.get('foodName').trim(),
          description: form.get('description').trim() || null,
          category: form.get('category'),
          quantity: Number(form.get('quantity')),
          unit: form.get('unit').trim(),
          prepared_at: preparedAt.toISOString(),
          expiry_time: expiryTime.toISOString(),
          pickup_address: form.get('pickupAddress').trim(),
        },
      })

      formElement.reset()
      setMessage('Donation created successfully.')
    } catch (error) {
      setIsError(true)
      setMessage(error.message)
    } finally {
      setIsSubmitting(false)
    }
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
            <label htmlFor="donation-food-name">Food name</label>
            <input
              id="donation-food-name"
              type="text"
              name="foodName"
              placeholder="e.g. Vegetable meals"
              required
            />
          </div>

          <div className="form-grid">
            <div>
              <label htmlFor="donation-category">Food category</label>
              <select id="donation-category" name="category">
                <option>Cooked meal</option>
                <option>Packaged food</option>
                <option>Bakery</option>
                <option>Produce</option>
                <option>Other</option>
              </select>
            </div>

            <div>
              <label htmlFor="donation-quantity">Quantity</label>
              <input
                id="donation-quantity"
                type="number"
                name="quantity"
                min="1"
                placeholder="20"
                required
              />
            </div>
          </div>

          <div className="form-grid">
            <div>
              <label htmlFor="donation-unit">Unit</label>
              <input
                id="donation-unit"
                type="text"
                name="unit"
                placeholder="e.g. servings, packets or kg"
                required
              />
            </div>

            <div>
              <label htmlFor="donation-prepared-at">Prepared at</label>
              <input
                id="donation-prepared-at"
                type="datetime-local"
                name="preparedAt"
                required
              />
            </div>
          </div>

          <div>
            <label htmlFor="donation-description">Description</label>
            <textarea
              id="donation-description"
              name="description"
              placeholder="Food details, packaging or allergen information"
              rows="3"
            />
          </div>

          <div>
            <label htmlFor="donation-pickup-address">Pickup address</label>
            <input
              id="donation-pickup-address"
              type="text"
              name="pickupAddress"
              placeholder="Area or address"
              required
            />
          </div>

          <div>
            <label htmlFor="donation-expiry-time">Available until</label>
            <input
              id="donation-expiry-time"
              type="datetime-local"
              name="expiryTime"
              required
            />
          </div>

          <button
            className="orange-button form-submit"
            type="submit"
            disabled={isSubmitting}
          >
            {isSubmitting ? 'Creating donation...' : 'Create donation'}
          </button>
        </form>

        {message && (
          <p
            className={`form-message ${isError ? 'form-error' : 'form-success'}`}
            role={isError ? 'alert' : 'status'}
          >
            {message}
          </p>
        )}
      </section>
    </>
  )
}

export default CreateDonation
