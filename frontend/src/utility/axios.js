import axios from 'axios'
import Cookies from 'js-cookie'

// Create Axios instance
const api = axios.create({
  baseURL: '/api/',
  headers: {
    'Content-Type': 'application/json',
  },
  withCredentials: true,
})

let csrftoken = Cookies.get('csrfcookiename');
axios.defaults.withCredentials = true
axios.defaults.credentials = 'same-origin';
axios.defaults.headers.common['X-CSRFToken'] = csrftoken;

export default api
