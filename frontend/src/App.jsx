import { useState } from 'react'

import Login from './pages/Login'
import Register from './pages/Register'

import DonorDashboard from './pages/DonorDashboard'
import CreateDonation from './pages/CreateDonation'
import MyDonations from './pages/MyDonations'
import BrowseRequests from './pages/BrowseRequests'

import NgoDashboard from './pages/NgoDashboard'
import CreateRequest from './pages/CreateRequest'
import MyRequests from './pages/MyRequests'
import AvailableFood from './pages/AvailableFood'

import Deliveries from './pages/Deliveries'
import Sidebar from './components/Sidebar'

import './App.css'

function App() {
  const [selectedRole, setSelectedRole] = useState('Donor')
  const [authPage, setAuthPage] = useState('login')

  // Temporary for frontend testing.
  // Later successful backend login will set this to true.
  const [loggedIn, setLoggedIn] = useState(false)

  const [currentPage, setCurrentPage] = useState('dashboard')

  function handleLogin() {
    setLoggedIn(true)
    setCurrentPage('dashboard')
  }

  function handleLogout() {
    setLoggedIn(false)
    setAuthPage('login')
    setCurrentPage('dashboard')
  }

  function renderPage() {
    if (selectedRole === 'Donor') {
      switch (currentPage) {
        case 'donate':
          return <CreateDonation />

        case 'donations':
          return <MyDonations onNavigate={setCurrentPage} />

        case 'requests':
          return <BrowseRequests />

        case 'deliveries':
          return <Deliveries />

        default:
          return <DonorDashboard onNavigate={setCurrentPage} />
      }
    }

    switch (currentPage) {
      case 'request':
        return <CreateRequest />

      case 'my-requests':
        return <MyRequests />

      case 'available':
        return <AvailableFood />

      case 'deliveries':
        return <Deliveries />

      default:
        return <NgoDashboard onNavigate={setCurrentPage} />
    }
  }

  if (!loggedIn) {
    if (authPage === 'register') {
      return (
        <Register
          role={selectedRole}
          onRoleChange={setSelectedRole}
          onLogin={() => setAuthPage('login')}
        />
      )
    }

    return (
      <Login
        role={selectedRole}
        onRoleChange={setSelectedRole}
        onRegister={() => setAuthPage('register')}
        onLogin={handleLogin}
      />
    )
  }

  return (
    <div className="dashboard-layout">
      <Sidebar
        role={selectedRole}
        activePage={currentPage}
        onNavigate={setCurrentPage}
        onLogout={handleLogout}
      />

      <main className="dashboard-main">
        {renderPage()}
      </main>
    </div>
  )
}

export default App