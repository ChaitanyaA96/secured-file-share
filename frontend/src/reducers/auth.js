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
  VERIFY_MFA_SUCCESS,
  REFRESH_SUCCESS,
} from '../actions/types'

const initialState = {
  // token stored in local storage
  access: localStorage.getItem('access') || null,
  refresh: localStorage.getItem('refresh') || null,
  isAuthenticated: !!localStorage.getItem('access') || false,
  isMfaRequired: false,
  user: null,
}

export default function (state = initialState, action) {
  switch (action.type) {
    case USER_LOADED:
      return {
        ...state,
        isAuthenticated: true,
        isLoading: false,
        user: action.payload,
      }
    case LOGIN_SUCCESS:
      return {
        ...state,
        isAuthenticated: false,
        isMfaRequired: true,
      }

    case VERIFY_MFA_SUCCESS:
      localStorage.setItem('access', action.payload.access)
      localStorage.setItem('refresh', action.payload.refresh)
      return {
        ...state,
        access: action.payload.access,
        refresh: action.payload.refresh,
        isAuthenticated: true,
        isMfaRequired: false,
        user: action.payload.user || state.user,
      }
    case REGISTER_SUCCESS:
      return {
        ...state,
        ...action.payload,
        isAuthenticated: false,
        isLoading: false,
        errorMessage: null,
      }
    case REGISTER_FAIL:
      return {
        ...state,
        user: null,
        isAuthenticated: false,
        isLoading: false,
        errorMessage: action.payload,
      }
    case LOGIN_FAIL:
      return {
        ...state,
        user: null,
        isAuthenticated: false,
        isLoading: false,
        isMfaRequired: false,
        errorMessage: action.payload,
      }
    case LOGOUT_SUCCESS:
      localStorage.removeItem('access')
      localStorage.removeItem('refresh')
      return {
        ...state,
        access: null,
        refresh: null,
        isAuthenticated: false,
        isMfaRequired: false,
        user: null,
        errorMessage: null,
      }
    case REFRESH_SUCCESS:
      return {
        ...state,
        access: action.payload.access,
        refresh: action.payload.refresh,
      }
    case USER_DELETE:
    default:
      return state
  }
}
