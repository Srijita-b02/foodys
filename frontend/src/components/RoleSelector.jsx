const roles = ['Donor', 'NGO']

function RoleSelector({ value, onChange }) {
  return (
    <div className="role-selector" aria-label="Choose your role">
      {roles.map((role) => (
        <button
          className={value === role ? 'role-option active' : 'role-option'}
          key={role}
          type="button"
          aria-pressed={value === role}
          onClick={() => onChange(role)}
        >
          <span>{role}</span>
          <small>
            {role === 'Donor'
              ? 'Individual or restaurant'
              : 'NGO member or volunteer'}
          </small>
        </button>
      ))}
    </div>
  )
}

export default RoleSelector
