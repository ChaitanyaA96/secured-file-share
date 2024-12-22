import React, { useEffect, useState } from 'react'
import { Menu } from 'antd'
import { Link, useLocation } from 'react-router-dom'
import { useSelector, useDispatch } from 'react-redux'
import { loadUser } from '../actions/auth' // Import loadUser action
import Logout from './account/logout'

const NavBar = () => {
  const dispatch = useDispatch()
  const isAuthenticated = useSelector((state) => state.auth.isAuthenticated) // Authentication state
  const user = useSelector((state) => state.auth.user) // User details
  const location = useLocation() // Current location for `selectedKeys`
  const [selectedKey, setSelectedKey] = useState('home') // Track active menu item

  // Fetch user details when authenticated
  useEffect(() => {
    if (isAuthenticated && !user) {
      dispatch(loadUser())
    }
  }, [isAuthenticated, user, dispatch])

  // Update selected menu key based on location
  useEffect(() => {
    const currentPath = location.pathname.replace('/', '') || 'home'
    setSelectedKey(currentPath)
  }, [location])

  const adminLink = {
    key: 'admin',
    label: <Link to="/admin">Admin</Link>,
  }

  // Define menu items dynamically based on authentication state
  const items = isAuthenticated
    ? [
        {
          key: 'home',
          label: <Link to="/">Home</Link>,
        },
        {
          key: 'dashboard',
          label: <Link to="/dashboard">Dashboard</Link>,
        },
        user?.role === 'admin' && adminLink,
        {
          key: 'logout',
          label: <Logout />,
        },
        {
          key: 'username',
          label: (
            <span style={{ color: '#fff' }}>
              Welcome, {user?.first_name} {user?.last_name || 'User'}
            </span>
          ),
        },
      ]
    : [
        {
          key: 'home',
          label: <Link to="/">Home</Link>,
        },
        {
          key: 'login',
          label: <Link to="/login">Login</Link>,
        },
        {
          key: 'register',
          label: <Link to="/register">Register</Link>,
        },
      ]

  return (
    <Menu
      mode="horizontal"
      theme="dark"
      style={{ display: 'flex', justifyContent: 'flex-end' }}
      selectedKeys={[selectedKey]}
      items={items}
    />
  )
}

export default NavBar
