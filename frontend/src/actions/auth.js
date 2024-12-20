import api from '../utility/axios'; // Import Axios instance with interceptors
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
} from './types';

// Helper function to handle and return errors
const returnErrors = (msg, status, id = null) => {
  return { type: AUTH_ERROR, msg, status, id };
};

// CHECK TOKEN & LOAD USER
export const loadUser = () => async (dispatch, getState) => {
  const config = tokenConfig(getState);
  try {
    const res = await api.get('auth/user/', config);
    dispatch({
      type: USER_LOADED,
      payload: res.data,
    });
  } catch (err) {
    dispatch(returnErrors(err.response?.data, err.response?.status));
    dispatch({ type: AUTH_ERROR });
  }
};

// LOGIN USER
export const login = (username, password) => async (dispatch) => {
  const body = JSON.stringify({ username, password });

  try {
    const res = await api.post('auth/login/', body);
    console.log(res.data);
    dispatch({ type: LOGIN_SUCCESS, payload: res.data });
    
    if (res.data.message && res.data.message.includes('MFA setup required')) {
      return { mfaSetupRequired: true, otpUrl: res.data.otp_url };
    } else if (res.data.message && res.data.message.includes('provide OTP')) {
      return { mfaRequired: true };
    }

   
  } catch (err) {
    dispatch({ type: LOGIN_FAIL });
    throw err;
  }
};

export const enableMFA = (otp) => async (dispatch) => {
  const body = JSON.stringify({ otp });

  try {
    const res = await api.post('auth/mfa/enable/', body);
    //dispatch({ type: 'ENABLE_MFA_SUCCESS', payload: res.data });
    return { success: true };
  } catch (err) {
    //dispatch({ type: 'ENABLE_MFA_FAIL' });
    throw err;
  }
};


// VERIFY MFA
export const verifyMFA = (otp) => async (dispatch, getState) => {
  const body = JSON.stringify({ otp });
  try {
    const res = await api.post('auth/login/otp/', body);
    
    dispatch({ type: VERIFY_MFA_SUCCESS, payload: res.data });
  } catch (err) {
    dispatch({ type: LOGIN_FAIL });
    throw err;
  }
};

// LOGOUT USER
export const logout = () => async (dispatch, getState) => {
  try {
    
    const refreshToken = getState().auth.refresh;
    if (!refreshToken) {
        throw new Error('Refresh token not found'); // Handle missing refresh token
    }
    
    const res = await api.post('auth/logout/', { refresh: refreshToken }, tokenConfig(getState));
    dispatch({ type: LOGOUT_SUCCESS });
  } catch (err) {
    dispatch(returnErrors(err.response?.data, err.response?.status));
  }
};

// REGISTER USER
export const register = ({ first_name, last_name, password, email }) => async (dispatch, getState) => {
  const body = JSON.stringify({ first_name, last_name, email, password });

  try {
    const res = await api.post('auth/register/', body, tokenConfig(getState));
    dispatch({ type: REGISTER_SUCCESS, payload: res.data });
  } catch (err) {
    dispatch({
      type: REGISTER_FAIL,
      payload: err.response?.data?.error || 'Registration failed. Please try again later.',
    });
  }
};

// UPDATE USER
export const updateUser = (data) => async (dispatch) => {
  try {
    const res = await api.patch('auth/update/', data);
    dispatch({ type: USER_UPDATE_SUCCESS, payload: res.data });
  } catch (err) {
    dispatch(returnErrors(err.response?.data, err.response?.status));
    dispatch({ type: USER_UPDATE_FAIL });
  }
};

// DELETE USER
export const deleteUser = () => async (dispatch) => {
  try {
    await api.post('auth/delete/');
    dispatch({ type: USER_DELETE });
  } catch (err) {
    dispatch(returnErrors(err.response?.data, err.response?.status));
  }
};

// TOKEN CONFIGURATION
export const tokenConfig = (getState) => {
  const access = getState().auth.access;
  const config = {
    headers: {
      'Content-Type': 'application/json',
    },
  };

  if (access) {
    config.headers['Authorization'] = `Bearer ${access}`;
  }

  return config;
};












































// // action funcs for auth

// // for requests
// import axios from 'axios';

// //import { createMessage, returnErrors } from "./messages";

// import {
//     USER_LOADED,
//     USER_LOADING,
//     USER_DELETE,
//     AUTH_ERROR,
//     LOGIN_SUCCESS,
//     LOGIN_FAIL,
//     LOGOUT_SUCCESS,
//     REGISTER_SUCCESS,
//     REGISTER_FAIL,
//     USER_UPDATE_SUCCESS,
//     USER_UPDATE_FAIL,
// } from './types';

// const returnErrors = (msg, status, id = null) => {
//     return {}
// };
// // // CHECK TOKEN & LOAD USER
// // export const loadUser = () => (dispatch, getState) => {
// //     // user loading
// //     dispatch({ type: USER_LOADING });

// //     // create request to load the user
// //     axios.get('http://localhost:8000/api/auth/user', tokenConfig(getState))
// //         .then(res => {
// //             dispatch({
// //                 type: USER_LOADED,
// //                 payload: res.data
// //             });
// //         })
// //         // if we are not authenticated, no token that matches, need to catch
// //         .catch(err => {
// //             // dispatch the error
// //             dispatch(returnErrors(err.response.data, err.response.status));
// //             // dispatch the type of error
// //             dispatch({
// //                 type: AUTH_ERROR
// //             })
// //         });
// // }


// export const login = (username, password) => async (dispatch) => {
//     const body = JSON.stringify({ username, password });
  
//     try {
//       const res = await axios.post('/auth/login/', body, tokenConfig(getState));
  
//       if (res.data.session_token) {
//         console.log(res.data);
//         return { mfaRequired: true, session_token: res.data.session_token };
//       }
//       console.log(res.data);
//       dispatch({ type: LOGIN_SUCCESS, payload: res.data });
//     } catch (err) {
//       dispatch({ type: LOGIN_FAIL });
//       throw err;
//     }
//   };


// export const verifyMFA = (session_token, otp) => async (dispatch) => {
// const body = JSON.stringify({ session_token, otp });
// console.log(session_token);
// console.log(otp);
// try {
//     const res = await axios.post('/auth/login/otp/', body, tokenConfig(getState));
//     console.log(res.data);
//     dispatch({ type: LOGIN_SUCCESS, payload: res.data });
// } catch (err) {
//     dispatch({ type: LOGIN_FAIL });
//     throw err;
// }
// };
  

// // LOGOUT USER
// export const logout = () => (dispatch, getState) => {

//     // create request to load the user
//     // need to pass in null as the body here
//     axios.post('/auth/logout/', null, tokenConfig(getState))
//         .then((res) => {
//             dispatch({
//                 type: LOGOUT_SUCCESS,
//             });
//         })
//         // if we are not authenticated, no token that matches, need to catch
//         .catch(err => {
//             // dispatch the error
//             dispatch(returnErrors(err.response.data, err.response.status));
//         });
// }


// export const register = ({ first_name, last_name, password, email }) => dispatch => {
//     // headers
//     const config = {
//         headers: {
//             'Content-Type': 'application/json',
//         }
//     }

//     // request body
//     //const body = JSON.stringify({ first_name, last_name, email, password });
//     const body = JSON.stringify({ email, password });

//     axios.post('/auth/register/', body, config)
//         .then((res) => {
//             dispatch({
//                 type: REGISTER_SUCCESS,
//                 payload: res.data
//             });
//             dispatch(createMessage({registerUser: msg}))
//         })
//         // if we are not authenticated, no token that matches, need to catch
//         .catch((err) => {
//             // dispatch the type of error
//             //console.log(err.response);
//             if(err.response){
//                 //dispatch(returnErrors(err.response.data,err.response.status))
//                 dispatch({
//                     type: REGISTER_FAIL,
//                     payload: err.response?.data?.error || "Registration failed. Please try again later.",
//                 })
//             }
//         });
// }

// // export const deleteUser = () => (dispatch, getState) => {
// //     // delete a user    
// //     axios.post('/api/auth/delete', null, tokenConfig(getState))
// //         .then(res => {
// //             dispatch(createMessage({ deleteUserSuccess: "Successfully deleted user. Redirecting..."}))
// //             setTimeout(()=>{
// //                 dispatch({
// //                     type: USER_DELETE,
// //                 });
// //             },2000)
// //         })
// //         .catch(err => {
// //             dispatch(returnErrors(err.response.data, err.response.status))
// //             dispatch(createMessage({ deleteUserFail: "Error deleting user. Try again later."}))
// //         })
// // }


// // export const updateUser = (data) => (dispatch, getState) => {
// //     /*
// //     Data assumes the following fields:
// //     username
// //     email
// //     first_name
// //     last_name
// //     password
// //     bio
// //     */

// //     axios.patch('/api/auth/update', data, tokenConfig(getState))
// //         .then(res => {
// //             if(res.data.msg != ""){
// //                 // then the backend is trying to tell us something
// //                 dispatch(createMessage({ updateUserBadOrg: res.data.msg }))
// //             }else{
// //                 // dispatch message
// //                 dispatch(createMessage({updateUser:"Update successful."}))
// //             }
// //             dispatch({
// //                 type: USER_UPDATE_SUCCESS,
// //                 payload: res.data
// //             });
// //         })
// //         .catch((err) => {
// //             // dispatch error
// //             // TO DO: 
// //             // MODIFY ERROR RETURN IN API
// //             console.log(err)
// //             if(err.response){
// //                 dispatch(returnErrors(err.response.data, err.response.status));
// //                 // type of error
// //                 dispatch(createMessage({ updateUserFail: err.response.data["message"] }))
// //                 dispatch({
// //                     type: USER_UPDATE_FAIL
// //                 })
// //             }
// //         });
// // };


// export const tokenConfig = (getState) => {
//     // Retrieve the access token from Redux state
//     const access = getState().auth.access;

//     // Create headers
//     const config = {
//         headers: {
//             'Content-Type': 'application/json',
//         },
//     };

//     // If an access token exists, add it to the Authorization header
//     if (access) {
//         config.headers['Authorization'] = `Bearer ${access}`;
//     }

//     return config;
// };