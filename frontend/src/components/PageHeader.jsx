function PageHeader({ title, description, action, actionLabel }) {
  return (
    <header className="page-header">
      <div>
        <h1>{title}</h1>
        {description && <p>{description}</p>}
      </div>

      {action && (
        <button className="orange-button" onClick={action}>
          + {actionLabel}
        </button>
      )}
    </header>
  )
}

export default PageHeader