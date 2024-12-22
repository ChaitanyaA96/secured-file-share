// src/reducers/index.js
import { combineReducers } from '@reduxjs/toolkit'
import auth from './auth' // Import your authReducer
import file from './file'
const rootReducer = combineReducers({
  auth: auth,
  file: file,
})

export default rootReducer
