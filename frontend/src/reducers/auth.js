/*
###############################################################################

Brief description: 
    This file handles a variety of different actions relating to 
authentication. This is mostly with login/logout and registration.

###############################################################################
*/

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
    REFRESH_SUCCESS
} from "../actions/types"

const initialState = {
    // token stored in local storage
    access: localStorage.getItem('access') || null,
    refresh: localStorage.getItem('refresh') || null,
    isAuthenticated: false,
    isMfaRequired: false,
    session_id: null,
    user: null
}

export default function(state=initialState, action){
    switch(action.type){
        case USER_LOADED:
            return {
                ...state,
                isAuthenticated: true,
                isLoading:false,
                user: action.payload
            }
        // case USER_UPDATE_SUCCESS:
        //     return {
        //         ...state,
        //         ...action.payload,
        //         isAuthenticated:true,
        //         isLoading:false,
        //     }
        case LOGIN_SUCCESS:
            return {
                ...state,
                isAuthenticated: false,
                isMfaRequired: true,
                session_id: action.session_id, // Set session_id
            };

        case VERIFY_MFA_SUCCESS:
            //localStorage.setItem('access', action.payload.access);
            //localStorage.setItem('refresh', action.payload.refresh);
            return {
                ...state,
                access: action.payload.access,
                refresh: action.payload.refresh,
                isAuthenticated: true,
                isMfaRequired: false,
                user: action.payload.user || state.user,
            };
        case REGISTER_SUCCESS:
            return {
                ...state,
                ...action.payload,
                isAuthenticated:false,
                isLoading:false,
                errorMessage: null,
            }
        case REGISTER_FAIL:
            
            return{
                ...state,
                user:null,
                isAuthenticated:false,
                isLoading:false,
                errorMessage: action.payload,
            }
        case LOGIN_FAIL:
            return{
                ...state,
                user:null,
                isAuthenticated:false,
                isLoading:false,
                isMfaRequired: false,
                session_id: null,
                errorMessage: action.payload,
            }
        case LOGOUT_SUCCESS:
            //localStorage.removeItem('access');
            //localStorage.removeItem('refresh');
            //localStorage.removeItem('session_id');
            return {
                ...state,
                access: null,
                refresh: null,
                isAuthenticated: false,
                isMfaRequired: false,
                session_id: null,
                user: null,
                errorMessage: null
            }
        case REFRESH_SUCCESS:
            console.log("REFRESH_SUCCESS", action.payload);
            return {
                ...state,
                access: action.payload.access,
                refresh: action.payload.refresh,
            }
        case USER_DELETE:
        default:
            console.warn(`Unhandled action type: ${action.type}`);
            return state;
    }
}
