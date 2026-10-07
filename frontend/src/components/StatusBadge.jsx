function StatusBadge({ status }) {
  const className = status.toLowerCase().replaceAll(' ', '-')

  return (
    <span className={`status-badge status-${className}`}>
      {status}
    </span>
  )
}

export default StatusBadge