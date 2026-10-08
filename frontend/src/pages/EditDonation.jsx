import { useEffect, useState } from 'react'
import PageHeader from '../components/PageHeader'
import { apiRequest } from '../api'

function toLocalDateTimeValue(value) {
  const date = new Date(value)
  const localTime = new Date(date.getTime() - date.getTimezoneOffset() * 60000)
  return localTime.toISOString().slice(0, 16)
}

function EditDonation({ token, donationId, onCancel, onSaved }) {
  const [donation, setDonation] = useState(null)
  const [isLoading, setIsLoading] = useState(true)
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [message, setMessage] = useState('')

  useEffect(() => {
    let ignore = false

    apiRequest(`/donations/${donationId}`, { token })
      .then((data) => {
        if (!ignore) {
          setDonation(data)
        }
      })
      .catch((error) => {
        if (!ignore) {
          setMessage(error.message)
        }
      })
      .finally(() => {
        if (!ignore) {
          setIsLoading(false)
        }
      })

    return () => {
      ignore = true
    }
  }, [donationId, token])

  async function handleSubmit(event) {
    event.preventDefault()
    setMessage('')

    const form = new FormData(event.currentTarget)
    const preparedAt = new Date(form.get('preparedAt'))
    const expiryTime = new Date(form.get('expiryTime'))

    if (expiryTime <= preparedAt) {
      setMessage('Available-until time must be later than preparation time.')
      return
    }

    setIsSubmitting(true)

    try {
      await apiRequest(`/donations/${donationId}`, {
        method: 'PUT',
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

      onSaved()
    } catch (error) {
      setMessage(error.message)
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <>
      <PageHeader
        title="Edit donation"
        description="Update an available food donation."
      />

      {isLoading && (
        <section className="form-card">
          <p className="empty-state">Loading donation...</p>
        </section>
      )}

      {!isLoading && message && !donation && (
        <p className="form-message form-error page-message" role="alert">
          {message}
        </p>
      )}

      {!isLoading && donation && donation.status !== 'available' && (
        <p className="form-message form-error page-message" role="alert">
          Only available donations can be edited.
        </p>
      )}

      {!isLoading && donation?.status === 'available' && (
        <section className="form-card">
          <form className="dashboard-form" onSubmit={handleSubmit}>
            <div>
              <label htmlFor="edit-donation-food-name">Food name</label>
              <input
                id="edit-donation-food-name"
                type="text"
                name="foodName"
                defaultValue={donation.food_name}
                required
              />
            </div>

            <div className="form-grid">
              <div>
                <label htmlFor="edit-donation-category">Food category</label>
                <select
                  id="edit-donation-category"
                  name="category"
                  defaultValue={donation.category}
                >
                  <option>Cooked meal</option>
                  <option>Packaged food</option>
                  <option>Bakery</option>
                  <option>Produce</option>
                  <option>Other</option>
                </select>
              </div>

              <div>
                <label htmlFor="edit-donation-quantity">Quantity</label>
                <input
                  id="edit-donation-quantity"
                  type="number"
                  name="quantity"
                  min="1"
                  defaultValue={donation.quantity}
                  required
                />
              </div>
            </div>

            <div className="form-grid">
              <div>
                <label htmlFor="edit-donation-unit">Unit</label>
                <input
                  id="edit-donation-unit"
                  type="text"
                  name="unit"
                  defaultValue={donation.unit}
                  required
                />
              </div>

              <div>
                <label htmlFor="edit-donation-prepared-at">Prepared at</label>
                <input
                  id="edit-donation-prepared-at"
                  type="datetime-local"
                  name="preparedAt"
                  defaultValue={toLocalDateTimeValue(donation.prepared_at)}
                  required
                />
              </div>
            </div>

            <div>
              <label htmlFor="edit-donation-description">Description</label>
              <textarea
                id="edit-donation-description"
                name="description"
                defaultValue={donation.description || ''}
                rows="3"
              />
            </div>

            <div>
              <label htmlFor="edit-donation-pickup-address">
                Pickup address
              </label>
              <input
                id="edit-donation-pickup-address"
                type="text"
                name="pickupAddress"
                defaultValue={donation.pickup_address}
                required
              />
            </div>

            <div>
              <label htmlFor="edit-donation-expiry-time">
                Available until
              </label>
              <input
                id="edit-donation-expiry-time"
                type="datetime-local"
                name="expiryTime"
                defaultValue={toLocalDateTimeValue(donation.expiry_time)}
                required
              />
            </div>

            <div className="form-actions">
              <button
                className="orange-button"
                type="submit"
                disabled={isSubmitting}
              >
                {isSubmitting ? 'Saving changes...' : 'Save changes'}
              </button>

              <button
                className="secondary-button"
                type="button"
                disabled={isSubmitting}
                onClick={onCancel}
              >
                Back
              </button>
            </div>
          </form>

          {message && (
            <p className="form-message form-error" role="alert">
              {message}
            </p>
          )}
        </section>
      )}
    </>
  )
}

export default EditDonation
