// src/App.js
import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { Layout } from 'antd';
import NavBar from './components/navbar';
import Home from './components/home/homepage';
import { Typography } from 'antd';
import Login from './components/account/login';
const { Header, Content, Footer } = Layout;
import { Provider } from 'react-redux';
import store from './store';
import Register from './components/account/register';
import Dashboard from './components/dashboard/dashboard';
import PrivateRoute from './utility/privateroute';
import AdminRoute from './utility/adminroute';
import AdminPage from './components/admin/adminpage';
import User from './components/admin/user';
import File from './components/admin/file';

const App = () => {

  return (
    <Router>
          <NavBar />
          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/login" element={<Login />} />
            <Route path="/register" element={<Register />} />
            <Route path="/dashboard" element={<PrivateRoute><Dashboard /></PrivateRoute>} />
            <Route path="/admin" element={<AdminRoute><AdminPage /></AdminRoute>} />
            <Route path="/admin/users" element={<AdminRoute><User /></AdminRoute>} />
            <Route path="/admin/files" element={<AdminRoute><File /></AdminRoute>} />
          </Routes>
    </Router>
  );
};

export default App;
