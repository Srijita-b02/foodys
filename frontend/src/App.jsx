import { useEffect, useState } from 'react'

import Login from './pages/Login'
import Register from './pages/Register'

import DonorDashboard from './pages/DonorDashboard'
import CreateDonation from './pages/CreateDonation'
import EditDonation from './pages/EditDonation'
import MyDonations from './pages/MyDonations'
import BrowseRequests from './pages/BrowseRequests'

import NgoDashboard from './pages/NgoDashboard'
import CreateRequest from './pages/CreateRequest'
import EditRequest from './pages/EditRequest'
import MyRequests from './pages/MyRequests'
import AvailableFood from './pages/AvailableFood'

import Deliveries from './pages/Deliveries'
import Sidebar from './components/Sidebar'
import {
  apiRequest,
  clearSession,
  loadSession,
  saveSession,
} from './api'

import './App.css'

function App() {
  const [initialSession] = useState(loadSession)
  const [selectedRole, setSelectedRole] = useState(
    initialSession?.user.role === 'ngo' ? 'NGO' : 'Donor',
  )
  const [authPage, setAuthPage] = useState('login')
  const [authNotice, setAuthNotice] = useState('')
  const [token, setToken] = useState(initialSession?.token || null)
  const [currentUser, setCurrentUser] = useState(initialSession?.user || null)
  const [restoringSession, setRestoringSession] = useState(Boolean(initialSession))
  const [currentPage, setCurrentPage] = useState('dashboard')
  const [editingDonationId, setEditingDonationId] = useState(null)
  const [editingRequestId, setEditingRequestId] = useState(null)

  useEffect(() => {
    if (!initialSession) {
      return
    }

    apiRequest('/auth/me', { token: initialSession.token })
      .then((user) => {
        saveSession(initialSession.token, user)
        setCurrentUser(user)
        setSelectedRole(user.role === 'ngo' ? 'NGO' : 'Donor')
      })
      .catch(() => {
        clearSession()
        setToken(null)
        setCurrentUser(null)
        setAuthNotice('Your session expired. Please sign in again.')
      })
      .finally(() => setRestoringSession(false))
  }, [initialSession])

  function handleLogin(loginResponse) {
    saveSession(loginResponse.access_token, loginResponse.user)
    setToken(loginResponse.access_token)
    setCurrentUser(loginResponse.user)
    setSelectedRole(loginResponse.user.role === 'ngo' ? 'NGO' : 'Donor')
    setAuthNotice('')
    setCurrentPage('dashboard')
    setEditingDonationId(null)
    setEditingRequestId(null)
  }

  function handleLogout() {
    clearSession()
    setToken(null)
    setCurrentUser(null)
    setAuthPage('login')
    setAuthNotice('')
    setCurrentPage('dashboard')
    setEditingDonationId(null)
    setEditingRequestId(null)
  }

  function handleRegistered() {
    setAuthNotice('Registration successful. You can now sign in.')
    setAuthPage('login')
  }

  function handleEditDonation(donationId) {
    setEditingDonationId(donationId)
    setCurrentPage('edit-donation')
  }

  function leaveEditDonation() {
    setEditingDonationId(null)
    setCurrentPage('donations')
  }

  function handleEditRequest(requestId) {
    setEditingRequestId(requestId)
    setCurrentPage('edit-request')
  }

  function leaveEditRequest() {
    setEditingRequestId(null)
    setCurrentPage('my-requests')
  }

  function renderPage() {
    if (selectedRole === 'Donor') {
      switch (currentPage) {
        case 'donate':
          return <CreateDonation token={token} />

        case 'donations':
          return (
            <MyDonations
              token={token}
              onNavigate={setCurrentPage}
              onEdit={handleEditDonation}
            />
          )

        case 'edit-donation':
          return editingDonationId ? (
            <EditDonation
              token={token}
              donationId={editingDonationId}
              onCancel={leaveEditDonation}
              onSaved={leaveEditDonation}
            />
          ) : (
            <MyDonations
              token={token}
              onNavigate={setCurrentPage}
              onEdit={handleEditDonation}
            />
          )

        case 'requests':
          return <BrowseRequests token={token} canRespond />

        default:
          return <DonorDashboard token={token} onNavigate={setCurrentPage} />
      }
    }

    switch (currentPage) {
      case 'request':
        return <CreateRequest token={token} />

      case 'my-requests':
        return (
          <MyRequests
            token={token}
            onNavigate={setCurrentPage}
            onEdit={handleEditRequest}
          />
        )

      case 'edit-request':
        return editingRequestId ? (
          <EditRequest
            token={token}
            requestId={editingRequestId}
            onCancel={leaveEditRequest}
            onSaved={leaveEditRequest}
          />
        ) : (
          <MyRequests
            token={token}
            onNavigate={setCurrentPage}
            onEdit={handleEditRequest}
          />
        )

      case 'requests':
        return <BrowseRequests token={token} canRespond={false} />

      case 'available':
        return <AvailableFood token={token} />

      case 'deliveries':
        return <Deliveries token={token} />

      default:
        return (
          <NgoDashboard token={token} onNavigate={setCurrentPage} />
        )
    }
  }

  if (restoringSession) {
    return (
      <main className="session-loading" aria-live="polite">
        Restoring your session...
      </main>
    )
  }

  if (!currentUser || !token) {
    if (authPage === 'register') {
      return (
        <Register
          role={selectedRole}
          onRoleChange={setSelectedRole}
          onLogin={() => {
            setAuthNotice('')
            setAuthPage('login')
          }}
          onRegistered={handleRegistered}
        />
      )
    }

    return (
      <Login
        role={selectedRole}
        onRoleChange={setSelectedRole}
        notice={authNotice}
        onRegister={() => {
          setAuthNotice('')
          setAuthPage('register')
        }}
        onLogin={handleLogin}
      />
    )
  }

  return (
    <div className="dashboard-layout">
      <Sidebar
        role={currentUser.role === 'ngo' ? 'NGO' : 'Donor'}
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
