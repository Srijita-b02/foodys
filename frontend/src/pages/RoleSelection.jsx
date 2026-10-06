const roles = [
  {
    name: 'Donor',
    icon: '○',
    description: 'Share safe surplus food with nearby communities.',
  },
  {
    name: 'NGO',
    icon: '♡',
    description: 'Find available food and request what people need.',
  },
  {
    name: 'Volunteer',
    icon: '→',
    description: 'Help move food from donors to organizations.',
  },
]

function RoleSelection({ onSelect }) {
  return (
    <main className="page role-page">
      <section className="intro">
        <p className="eyebrow">SDG 2 · ZERO HUNGER</p>
        <h1>Choose how you want to help.</h1>
        <p className="intro-copy">
          One community connecting surplus food with the people who need it.
        </p>
      </section>

      <section className="role-grid" aria-label="Choose your role">
        {roles.map((role) => (
          <button
            className="role-card"
            key={role.name}
            onClick={() => onSelect(role.name)}
            type="button"
          >
            <span className="role-icon" aria-hidden="true">
              {role.icon}
            </span>
            <span className="role-name">{role.name}</span>
            <span className="role-description">{role.description}</span>
            <span className="role-action">Continue →</span>
          </button>
        ))}
      </section>

      <p className="impact-note">
        Every successful delivery is one step towards zero hunger.
      </p>
    </main>
  )
}

export default RoleSelection
