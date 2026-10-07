import { useEffect, useState } from 'react'
import PageHeader from '../components/PageHeader'
import { apiRequest } from '../api'

function formatDate(value) {
  return new Intl.DateTimeFormat(undefined, {
    dateStyle: 'medium',
    timeStyle: 'short',
  }).format(new Date(value))
}

function AvailableFood({ token }) {
  const [donations, setDonations] = useState([])
  const [isLoading, setIsLoading] = useState(true)
  const [submittingId, setSubmittingId] = useState(null)
  const [message, setMessage] = useState('')
  const [isError, setIsError] = useState(false)

  useEffect(() => {
    let ignore = false

    apiRequest('/donations', { token })
      .then((data) => {
        if (!ignore) {
          setDonations(data)
        }
      })
      .catch((error) => {
        if (!ignore) {
          setIsError(true)
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
  }, [token])

  async function reserveDonation(event, donation) {
    event.preventDefault()
    setMessage('')
    setIsError(false)

    const form = new FormData(event.currentTarget)
    const allocatedQuantity = Number(form.get('allocatedQuantity'))
    const remaining = donation.remaining_quantity ?? donation.quantity

    if (allocatedQuantity <= 0 || allocatedQuantity > remaining) {
      setIsError(true)
      setMessage(`Enter a quantity between 1 and ${remaining}.`)
      return
    }

    setSubmittingId(donation.id)

    try {
      await apiRequest('/matches/reserve', {
        method: 'POST',
        token,
        body: {
          donation_id: donation.id,
          allocated_quantity: allocatedQuantity,
        },
      })

      const refreshed = await apiRequest('/donations', { token })
      setDonations(refreshed)
      setMessage(
        `${allocatedQuantity} ${donation.unit} reserved successfully. A delivery was assigned to you.`,
      )
    } catch (error) {
      setIsError(true)
      setMessage(error.message)
    } finally {
      setSubmittingId(null)
    }
  }

  return (
    <>
      <PageHeader
        title="Available food"
        description="Reserve available food for pickup and delivery."
      />

      {message && (
        <p
          className={`form-message ${isError ? 'form-error' : 'form-success'} page-message`}
          role={isError ? 'alert' : 'status'}
        >
          {message}
        </p>
      )}

      <section className="content-card">
        {isLoading && <p className="empty-state">Loading available food...</p>}

        {!isLoading && donations.length === 0 && (
          <p className="empty-state">No food is currently available.</p>
        )}

        {donations.map((donation) => {
          const remaining = donation.remaining_quantity ?? donation.quantity

          return (
            <div className="request-card" key={donation.id}>
              <div>
                <span className="small-label">{donation.category}</span>
                <h3>{donation.food_name}</h3>
                <p>
                  {remaining} of {donation.quantity} {donation.unit} remaining
                  {' · '}
                  {donation.pickup_address}
                </p>
                <p>Available until {formatDate(donation.expiry_time)}</p>
                {donation.description && <p>{donation.description}</p>}
              </div>

              <form
                className="match-form"
                onSubmit={(event) => reserveDonation(event, donation)}
              >
                <label htmlFor={`reserve-quantity-${donation.id}`}>
                  Quantity ({donation.unit})
                </label>
                <input
                  id={`reserve-quantity-${donation.id}`}
                  name="allocatedQuantity"
                  type="number"
                  min="1"
                  max={remaining}
                  defaultValue={remaining}
                  required
                />
                <button
                  className="orange-button"
                  type="submit"
                  disabled={submittingId === donation.id}
                >
                  {submittingId === donation.id ? 'Reserving...' : 'Reserve'}
                </button>
              </form>
            </div>
          )
        })}
      </section>
    </>
  )
}

export default AvailableFood
