import React, { useEffect } from 'react'
import { Navigate } from 'react-router-dom'
import { useSelector, useDispatch } from 'react-redux'
import { loadUser } from '../actions/auth'

const AdminRoute = ({ children }) => {
  const dispatch = useDispatch()
  const user = useSelector((state) => state.auth.user)
  const isAuthenticated = useSelector((state) => state.auth.isAuthenticated)

  useEffect(() => {
    if (isAuthenticated && !user) {
      dispatch(loadUser())
    }
  }, [dispatch, isAuthenticated, user])

  if (!isAuthenticated || user.role !== 'admin') {
    return <Navigate to="/" />
  }

  return children
}

export default AdminRoute
