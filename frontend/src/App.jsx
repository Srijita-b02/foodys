import { useState } from 'react'
import Login from './pages/Login'
import Register from './pages/Register'
import './App.css'

function App() {
  const [selectedRole, setSelectedRole] = useState('Donor')
  const [showRegister, setShowRegister] = useState(false)

  if (showRegister) {
    return (
      <Register
        role={selectedRole}
        onRoleChange={setSelectedRole}
        onLogin={() => setShowRegister(false)}
      />
    )
  }

  return (
    <Login
      role={selectedRole}
      onRoleChange={setSelectedRole}
      onRegister={() => setShowRegister(true)}
    />
  )
}

export default App
