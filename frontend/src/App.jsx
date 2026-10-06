import { useState } from 'react'
import Login from './pages/Login'
import Register from './pages/Register'
import RoleSelection from './pages/RoleSelection'
import './App.css'

function App() {
  const [selectedRole, setSelectedRole] = useState(null)
  const [showRegister, setShowRegister] = useState(false)

  function returnToRoles() {
    setSelectedRole(null)
    setShowRegister(false)
  }

  if (!selectedRole) {
    return <RoleSelection onSelect={setSelectedRole} />
  }

  if (showRegister) {
    return <Register role={selectedRole} onBack={() => setShowRegister(false)} />
  }

  return (
    <Login
      role={selectedRole}
      onBack={returnToRoles}
      onRegister={() => setShowRegister(true)}
    />
  )
}

export default App
