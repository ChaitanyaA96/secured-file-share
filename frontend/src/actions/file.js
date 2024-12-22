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
    const fileConfig = fileTokenConfig(getState);
    fileConfig.headers['Content-Type'] = 'multipart/form-data'; 
    const formData = new FormData();
    formData.append('file', fileData.get('file'));
    formData.append('description', fileData.get('description'));
    formData.append('name', fileData.get('name'));

    const res = await api.post('files/upload/', formData, fileConfig);
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
export const shareFileAuthenticated = (shareDetails) => async (dispatch, getState) => {
  try {
    console.log("shareDetails", shareDetails);
    const res = await api.post('files/share/', shareDetails, fileTokenConfig(getState));
    dispatch({ type: SHARE_FILE, payload: res.data });
  } catch (err) {
    console.error('Error sharing file:', err);
  }
};

// Create a Public Share
export const shareFilePublic = (shareDetails) => async (dispatch, getState) => {
  // Expected shareDetails: { file_id: string, expires_in: string }
  try {
    const res = await api.post('files/share/public/', shareDetails, fileTokenConfig(getState));
    console.log('Public share created:', res.data);
    return res.data;
  } catch (err) {
    console.error('Error creating public share:', err);
  }
};

// Get Public Share Details
export const getPublicShareDetails = (shareDetails) => async (dispatch, getState) => {
  try {
    console.log(shareDetails)
    const url = `files/shared/public/details/?file_id=${shareDetails.file_id}`;
    const res = await api.get(url, fileTokenConfig(getState));
    return res.data;
  } catch (err) {
    console.error('Error getting public share details:', err);
  }
};

// Send an Email
export const sendEmail = (emailData) => async (dispatch, getState) => {
  // Expected emailData: { to: string, subject: string, message: string }
  try {
    console.log("emailData", emailData);
    const res = await api.post('files/send-email/', emailData, fileTokenConfig(getState));
    console.log('Email sent successfully:', res.data);
    return res.data;
  } catch (err) {
    console.error('Error sending email:', err);
  }
};

// Access Shared File (Authenticated User)
export const accessSharedFileAuthenticated = (sharedLink) => async (dispatch, getState) => {
  try {
    console.log("sharedLink", sharedLink);
    const fileConfig = fileTokenConfig(getState);
    fileConfig['responseType'] = 'blob';
    console.log("fileConfig", fileConfig);
    const res = await api.get(`files/shared/${sharedLink}/`, fileConfig);
    console.log("res", res);
    return res;
  } catch (err) {
    console.error('Error accessing shared file for authenticated user:', err);
  }
};


// Access Shared File (Public User)
export const accessSharedFilePublic = (sharedLink, passphrase = null) => async () => {
  try {
    const config = {
      headers: {
        'Accept': 'application/json',
      },
      params: {
        passphrase: passphrase,
      },
    };
    const res = await api.get(`files/shared/public/${sharedLink}/`, config);
    return res.data;
  } catch (err) {
    console.error('Error accessing shared file for public user:', err);
  }
};


// Helper function to set up config with token
const fileTokenConfig = (getState) => {
  const token = getState().auth.access;
  const config = {
    headers: {
      'Content-Type': 'application/json',
    },
  };

  if (token) {
    config.headers['Authorization'] = `Token ${token}`;
  }

  return config;
};