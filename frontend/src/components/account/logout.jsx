import React from 'react'
import { useDispatch } from 'react-redux'
import { logout } from '../../actions/auth' // Import the logout action
import { Button } from 'antd'
import { useNavigate } from 'react-router-dom'

const Logout = () => {
  const dispatch = useDispatch()
  const navigate = useNavigate()

  // Handle logout
  const handleLogout = () => {
    dispatch(logout()) // Dispatch the logout action
    navigate('/login') // Redirect to the login page
  }

  return (
    <Button type="primary" danger onClick={handleLogout}>
      Logout
    </Button>
  )
}

export default Logout
