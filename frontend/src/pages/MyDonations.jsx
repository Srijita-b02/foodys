import PageHeader from '../components/PageHeader'
import StatusBadge from '../components/StatusBadge'

function MyDonations({ onNavigate }) {
  const donations = [
    {
      id: 1,
      food: 'Vegetable meals',
      quantity: '20 servings',
      date: 'Today · 5:00 PM',
      status: 'Available',
    },
    {
      id: 2,
      food: 'Bread & pastries',
      quantity: '12 servings',
      date: 'Today · 7:30 PM',
      status: 'Reserved',
    },
    {
      id: 3,
      food: 'Rice meals',
      quantity: '30 servings',
      date: 'Yesterday',
      status: 'Delivered',
    },
  ]

  return (
    <>
      <PageHeader
        title="My donations"
        description="Manage your current and previous food donations."
        action={() => onNavigate('donate')}
        actionLabel="New donation"
      />

      <section className="content-card">
        {donations.map((donation) => (
          <div className="list-row" key={donation.id}>
            <div>
              <strong>{donation.food}</strong>
              <p>
                {donation.quantity} · {donation.date}
              </p>
            </div>

            <StatusBadge status={donation.status} />
          </div>
        ))}
      </section>
    </>
  )
}

export default MyDonations