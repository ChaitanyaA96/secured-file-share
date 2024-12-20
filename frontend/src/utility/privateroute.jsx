
import React from 'react';
import { Navigate } from 'react-router-dom';
import { useSelector } from 'react-redux';

// PrivateRoute ensures only authenticated users can access its children.
const PrivateRoute = ({ children }) => {
  const isAuthenticated = useSelector((state) => state.auth.isAuthenticated);

  // Redirect to login if the user is not authenticated
  if (!isAuthenticated) {
    return <Navigate to="/login" />;
  }

  // Render children if authenticated
  return children;
};

export default PrivateRoute;
