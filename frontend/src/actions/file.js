import {
  SET_MY_FILES,
  SET_SHARED_WITH_ME,
  UPLOAD_FILE,
  SHARE_FILE,
} from './types';
import api from '../utility/axios'; // Import the Axios instance with interceptors

// Load My Files
export const loadMyFiles = () => async (dispatch, getState) => {
  try {
    const res = await api.get('files/my-files/', fileTokenConfig(getState));
    console.log("res", res);
    dispatch({ type: SET_MY_FILES, payload: res.data });
  } catch (err) {
    console.error('Error loading my files:', err);
  }
};

// Load Files Shared With Me
export const loadSharedWithMe = () => async (dispatch, getState) => {
  try {
    const res = await api.get('files/shared-with-me/', fileTokenConfig(getState));
    console.log("res", res);
    dispatch({ type: SET_SHARED_WITH_ME, payload: res.data });
  } catch (err) {
    console.error('Error loading shared files:', err);
  }
};

// Upload a File
export const uploadFile = (fileData) => async (dispatch, getState) => {
  try {
    const formData = new FormData();
    formData.append('file', fileData.get('file'));
    formData.append('description', fileData.get('description'));
    formData.append('name', fileData.get('name'));

    const res = await api.post('files/upload/', fileData, fileTokenConfig(getState));
    dispatch({ type: UPLOAD_FILE, payload: res.data });
  } catch (err) {
    console.error('Error uploading file:', err);
  }
};

// Download a File
export const downloadFile = (fileId, fileName) => async (dispatch, getState) => {
  try {
    const res = await api.get(`files/download/${fileId}/`, {
      ...fileTokenConfig(getState),
      responseType: 'blob', // Ensure binary data
    });

    // Create a Blob from the response data
    const fileBlob = new Blob([res.data], { type: res.headers['content-type'] });
    const url = window.URL.createObjectURL(fileBlob);

    // Trigger download with dynamic filename
    const link = document.createElement('a');
    link.href = url;
    link.setAttribute('download', fileName); // Use the provided filename
    document.body.appendChild(link);
    link.click();
    link.remove();

    dispatch({ type: DOWNLOAD_FILE, payload: res.data });
  } catch (err) {
    console.error('Error downloading file:', err);
  }
};


// Share a File
export const shareFile = (shareDetails) => async (dispatch, getState) => {
  try {
    console.log("shareDetails", shareDetails);
    const res = await api.post('files/share/', shareDetails, fileTokenConfig(getState));
    dispatch({ type: SHARE_FILE, payload: res.data });
  } catch (err) {
    console.error('Error sharing file:', err);
  }
};


// Helper function to set up config with token
const fileTokenConfig = (getState) => {
  const token = getState().auth.access;
  const config = {
    headers: {
      'Accept': 'application/json',
      'Content-Type': 'multipart/form-data',
    },
  };

  if (token) {
    config.headers['Authorization'] = `Token ${token}`;
  }

  return config;
};


//import axios from 'axios';

// import {
//   SET_MY_FILES,
//   SET_SHARED_WITH_ME,
//   UPLOAD_FILE,
//   SHARE_FILE,
// } from './types'


// // Load My Files
// export const loadMyFiles = () => async (dispatch, getState) => {
//   try {
//     const res = await axios.get('http://localhost:8000/api/files/my-files/', fileTokenConfig(getState));
//     dispatch({
//       type: SET_MY_FILES,
//       payload: res.data,
//     });
//   } catch (err) {
//     console.error('Error loading my files:', err);
//     throw err; // Propagate the error for further handling if needed
//   }
// };

// // Load Files Shared With Me
// export const loadSharedWithMe = () => async (dispatch, getState) => {
//   try {
//     const res = await axios.get('http://localhost:8000/api/files/shared-with-me/', fileTokenConfig(getState));
//     dispatch({
//       type: SET_SHARED_WITH_ME,
//       payload: res.data,
//     });
//   } catch (err) {
//     console.error('Error loading shared files:', err);
//     throw err;
//   }
// };

// // Upload a File
// export const uploadFile = (fileData) => async (dispatch, getState) => {
//   try {
//     const res = await axios.post('http://localhost:8000/api/files/upload/', fileData, fileTokenConfig(getState));
//     dispatch({
//       type: UPLOAD_FILE,
//       payload: res.data,
//     });
//   } catch (err) {
//     console.error('Error uploading file:', err);
//     throw err;
//   }
// };

// // Share a File
// export const shareFile = (shareDetails) => async (dispatch, getState) => {
//   try {
//     const res = await axios.post('http://localhost:8000/api/files/share/', shareDetails, fileTokenConfig(getState));
//     dispatch({
//       type: SHARE_FILE,
//       payload: res.data,
//     });
//   } catch (err) {
//     console.error('Error sharing file:', err);
//     throw err;
//   }
// };