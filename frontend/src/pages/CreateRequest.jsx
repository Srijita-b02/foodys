import { useState } from 'react'
import PageHeader from '../components/PageHeader'
import { apiRequest } from '../api'

function CreateRequest({ token }) {
  const [message, setMessage] = useState('')
  const [isError, setIsError] = useState(false)
  const [isSubmitting, setIsSubmitting] = useState(false)

  async function handleSubmit(event) {
    event.preventDefault()
    setMessage('')
    setIsError(false)

    const formElement = event.currentTarget
    const form = new FormData(formElement)
    const neededBefore = new Date(form.get('neededBefore'))

    if (neededBefore <= new Date()) {
      setIsError(true)
      setMessage('Needed-before time must be in the future.')
      return
    }

    setIsSubmitting(true)

    try {
      await apiRequest('/requests', {
        method: 'POST',
        token,
        body: {
          food_name: form.get('foodName').trim(),
          category: form.get('category'),
          quantity: Number(form.get('quantity')),
          unit: form.get('unit').trim(),
          description: form.get('description').trim() || null,
          location: form.get('location').trim(),
          needed_before: neededBefore.toISOString(),
        },
      })

      formElement.reset()
      setMessage('Food request created successfully.')
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
        title="New food request"
        description="Tell nearby donors what food is needed."
      />

      <section className="form-card">
        <form className="dashboard-form" onSubmit={handleSubmit}>
          <div>
            <label htmlFor="request-food-name">Food name</label>
            <input
              id="request-food-name"
              type="text"
              name="foodName"
              placeholder="e.g. Meals for a community dinner"
              required
            />
          </div>

          <div className="form-grid">
            <div>
              <label htmlFor="request-category">Food category</label>
              <select id="request-category" name="category">
                <option>Any suitable food</option>
                <option>Cooked meal</option>
                <option>Packaged food</option>
                <option>Bakery</option>
                <option>Produce</option>
                <option>Other</option>
              </select>
            </div>

            <div>
              <label htmlFor="request-quantity">Quantity required</label>
              <input
                id="request-quantity"
                type="number"
                name="quantity"
                min="1"
                required
              />
            </div>
          </div>

          <div className="form-grid">
            <div>
              <label htmlFor="request-unit">Unit</label>
              <input
                id="request-unit"
                type="text"
                name="unit"
                placeholder="e.g. servings, packets or kg"
                required
              />
            </div>

            <div>
              <label htmlFor="request-needed-before">Needed before</label>
              <input
                id="request-needed-before"
                type="datetime-local"
                name="neededBefore"
                required
              />
            </div>
          </div>

          <div>
            <label htmlFor="request-location">Location</label>
            <input
              id="request-location"
              type="text"
              name="location"
              placeholder="Pickup or delivery area"
              required
            />
          </div>

          <div>
            <label htmlFor="request-description">Description</label>
            <textarea
              id="request-description"
              name="description"
              placeholder="Dietary, packaging or collection information"
              rows="4"
            />
          </div>

          <button
            className="orange-button form-submit"
            type="submit"
            disabled={isSubmitting}
          >
            {isSubmitting ? 'Posting request...' : 'Post request'}
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

export default CreateRequest
