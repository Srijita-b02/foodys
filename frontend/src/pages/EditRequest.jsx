import { useEffect, useState } from 'react'
import PageHeader from '../components/PageHeader'
import { apiRequest } from '../api'

function toLocalDateTimeValue(value) {
  const date = new Date(value)
  const localTime = new Date(date.getTime() - date.getTimezoneOffset() * 60000)
  return localTime.toISOString().slice(0, 16)
}

function EditRequest({ token, requestId, onCancel, onSaved }) {
  const [foodRequest, setFoodRequest] = useState(null)
  const [isLoading, setIsLoading] = useState(true)
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [message, setMessage] = useState('')

  useEffect(() => {
    let ignore = false

    apiRequest(`/requests/${requestId}`, { token })
      .then((data) => {
        if (!ignore) {
          setFoodRequest(data)
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
  }, [requestId, token])

  async function handleSubmit(event) {
    event.preventDefault()
    setMessage('')

    const form = new FormData(event.currentTarget)
    const neededBefore = new Date(form.get('neededBefore'))

    if (neededBefore <= new Date()) {
      setMessage('Needed-before time must be in the future.')
      return
    }

    setIsSubmitting(true)

    try {
      await apiRequest(`/requests/${requestId}`, {
        method: 'PUT',
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
        title="Edit food request"
        description="Update an open food request."
      />

      {isLoading && (
        <section className="form-card">
          <p className="empty-state">Loading request...</p>
        </section>
      )}

      {!isLoading && message && !foodRequest && (
        <p className="form-message form-error page-message" role="alert">
          {message}
        </p>
      )}

      {!isLoading && foodRequest && foodRequest.status !== 'open' && (
        <p className="form-message form-error page-message" role="alert">
          Only open food requests can be edited.
        </p>
      )}

      {!isLoading && foodRequest?.status === 'open' && (
        <section className="form-card">
          <form className="dashboard-form" onSubmit={handleSubmit}>
            <div>
              <label htmlFor="edit-request-food-name">Food name</label>
              <input
                id="edit-request-food-name"
                type="text"
                name="foodName"
                defaultValue={foodRequest.food_name}
                required
              />
            </div>

            <div className="form-grid">
              <div>
                <label htmlFor="edit-request-category">Food category</label>
                <select
                  id="edit-request-category"
                  name="category"
                  defaultValue={foodRequest.category}
                >
                  <option>Any suitable food</option>
                  <option>Cooked meal</option>
                  <option>Packaged food</option>
                  <option>Bakery</option>
                  <option>Produce</option>
                  <option>Other</option>
                </select>
              </div>

              <div>
                <label htmlFor="edit-request-quantity">Quantity required</label>
                <input
                  id="edit-request-quantity"
                  type="number"
                  name="quantity"
                  min="1"
                  defaultValue={foodRequest.quantity}
                  required
                />
              </div>
            </div>

            <div className="form-grid">
              <div>
                <label htmlFor="edit-request-unit">Unit</label>
                <input
                  id="edit-request-unit"
                  type="text"
                  name="unit"
                  defaultValue={foodRequest.unit}
                  required
                />
              </div>

              <div>
                <label htmlFor="edit-request-needed-before">
                  Needed before
                </label>
                <input
                  id="edit-request-needed-before"
                  type="datetime-local"
                  name="neededBefore"
                  defaultValue={toLocalDateTimeValue(
                    foodRequest.needed_before,
                  )}
                  required
                />
              </div>
            </div>

            <div>
              <label htmlFor="edit-request-location">Location</label>
              <input
                id="edit-request-location"
                type="text"
                name="location"
                defaultValue={foodRequest.location}
                required
              />
            </div>

            <div>
              <label htmlFor="edit-request-description">Description</label>
              <textarea
                id="edit-request-description"
                name="description"
                defaultValue={foodRequest.description || ''}
                rows="4"
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

export default EditRequest
