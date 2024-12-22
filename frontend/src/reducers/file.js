import {
  SET_MY_FILES,
  SET_SHARED_WITH_ME,
  UPLOAD_FILE,
  SHARE_FILE,
} from '../actions/types'

const initialState = {
  myFiles: [],
  sharedWithMe: [],
}

const fileReducer = (state = initialState, action) => {
  switch (action.type) {
    case SET_MY_FILES:
      return { ...state, myFiles: action.payload }
    case SET_SHARED_WITH_ME:
      return { ...state, sharedWithMe: action.payload }
    case UPLOAD_FILE:
      return { ...state, myFiles: [...state.myFiles, action.payload] }
    case SHARE_FILE:
      return state
    default:
      return state
  }
}

export default fileReducer
