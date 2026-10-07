function Sidebar({ role, activePage, onNavigate, onLogout }) {
  const donorItems = [
    ['dashboard', 'Overview'],
    ['donate', 'New donation'],
    ['donations', 'My donations'],
    ['requests', 'Food requests'],
    ['deliveries', 'Deliveries'],
  ]

  const ngoItems = [
    ['dashboard', 'Overview'],
    ['request', 'New request'],
    ['my-requests', 'My requests'],
    ['available', 'Available food'],
    ['deliveries', 'Deliveries'],
  ]

  const items = role === 'Donor' ? donorItems : ngoItems

  return (
    <aside className="sidebar">
      <div>
        <div className="brand">
          <span className="brand-mark">FD</span>
          <span>Foodys</span>
        </div>

        <p className="sidebar-label">{role}</p>

        <nav>
          {items.map(([page, label]) => (
            <button
              key={page}
              className={`nav-item ${
                activePage === page ? 'active' : ''
              }`}
              onClick={() => onNavigate(page)}
            >
              {label}
            </button>
          ))}
        </nav>
      </div>

      <button className="logout-button" onClick={onLogout}>
        Sign out
      </button>
    </aside>
  )
}

export default Sidebar