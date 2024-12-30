import api from '../utility/axios' // Import Axios instance with interceptors
import {
  USER_LOADED,
  USER_LOADING,
  USER_DELETE,
  AUTH_ERROR,
  LOGIN_SUCCESS,
  LOGIN_FAIL,
  LOGOUT_SUCCESS,
  REGISTER_SUCCESS,
  REGISTER_FAIL,
  USER_UPDATE_SUCCESS,
  USER_UPDATE_FAIL,
  VERIFY_MFA_SUCCESS,
} from './types'

// Helper function to handle and return errors
const returnErrors = (msg, status, id = null) => {
  return { type: AUTH_ERROR, msg, status, id }
}

// CHECK TOKEN & LOAD USER
export const loadUser = () => async (dispatch, getState) => {
  const config = tokenConfig(getState)
  try {
    const res = await api.get('auth/user/', config)
    dispatch({
      type: USER_LOADED,
      payload: res.data,
    })
  } catch (err) {
    dispatch(returnErrors(err.response?.data, err.response?.status))
    dispatch({ type: AUTH_ERROR })
  }
}

// LOGIN USER
export const login = (username, password) => async (dispatch) => {
  const body = JSON.stringify({ username, password })

  try {
    const res = await api.post('auth/login/', body)
    dispatch({ type: LOGIN_SUCCESS, payload: res.data })

    if (res.data.message && res.data.message.includes('MFA setup required')) {
      return { mfaSetupRequired: true, otpUrl: res.data.otp_url }
    } else if (res.data.message && res.data.message.includes('provide OTP')) {
      return { mfaRequired: true }
    }
  } catch (err) {
    dispatch({ type: LOGIN_FAIL })
    throw err
  }
}

export const enableMFA = (otp) => async (dispatch) => {
  const body = JSON.stringify({ otp })

  try {
    const res = await api.post('auth/mfa/enable/', body)
    return { success: true }
  } catch (err) {
    throw err
  }
}

// VERIFY MFA
export const verifyMFA = (otp) => async (dispatch, getState) => {
  const body = JSON.stringify({ otp })
  try {
    const res = await api.post('auth/login/otp/', body)

    dispatch({ type: VERIFY_MFA_SUCCESS, payload: res.data })
    return {success: true}
  } catch (err) {
    dispatch({ type: LOGIN_FAIL })
    throw err
  }
}

// LOGOUT USER
export const logout = () => async (dispatch, getState) => {
  try {
    const res = await api.post(
      'auth/logout/',
      tokenConfig(getState),
    )
    dispatch({ type: LOGOUT_SUCCESS })
  } catch (err) {
    dispatch(returnErrors(err.response?.data, err.response?.status))
  }
}

// REGISTER USER
export const register =
  ({ first_name, last_name, password, email }) =>
  async (dispatch, getState) => {
    const body = JSON.stringify({ first_name, last_name, email, password })

    try {
      const res = await api.post('auth/register/', body, tokenConfig(getState))
      dispatch({ type: REGISTER_SUCCESS, payload: res.data })
    } catch (err) {
      dispatch({
        type: REGISTER_FAIL,
        payload:
          err.response?.data?.error ||
          'Registration failed. Please try again later.',
      })
    }
  }

// UPDATE USER
export const updateUser = (data) => async (dispatch) => {
  try {
    const res = await api.patch('auth/update/', data)
    dispatch({ type: USER_UPDATE_SUCCESS, payload: res.data })
  } catch (err) {
    dispatch(returnErrors(err.response?.data, err.response?.status))
    dispatch({ type: USER_UPDATE_FAIL })
  }
}

// DELETE USER
export const deleteUser = () => async (dispatch) => {
  try {
    await api.post('auth/delete/')
    dispatch({ type: USER_DELETE })
  } catch (err) {
    dispatch(returnErrors(err.response?.data, err.response?.status))
  }
}

// TOKEN CONFIGURATION
export const tokenConfig = (getState) => {
  const access = getState().auth.access
  const config = {
    headers: {
      'Content-Type': 'application/json',
    },
  }

  return config
}
