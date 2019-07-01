import axios from 'axios'
import Qs from 'qs'
import { Message } from 'element-ui'

// create an axios instance
const service = axios.create({
  baseURL: 'http://192.168.56.101:7654', // url = base url + request url
  withCredentials: true, // send cookies when cross-domain requests
  timeout: 5000, // request timeout
  headers: {
    'X-Requested-With': 'x-requested-with',
    'X-System-ID': 1
  },
  xsrfCookieName: '_xsrf',
  transformRequest: [function(data) {
    data = Qs.stringify(data)
    // console.log("transformRequest->", data);
    return data
  }],
  xsrfHeaderName: 'X-Xsrftoken' 
})

// request interceptor
service.interceptors.request.use(
  config => {
    // do something before request is sent
    return config
  },
  error => {
    // do something with request error
    console.log(error) // for debug
    return Promise.reject(error)
  }
)

// response interceptor
service.interceptors.response.use(
  /**
   * If you want to get http information such as headers or status
   * Please return  response => response
  */

  /**
   * Determine the request status by custom code
   * Here is just an example
   * You can also judge the status by HTTP Status Code
   */
  response => {
    return response.data
  },
  error => {
    console.log('err' + error) // for debug
    Message({
      message: error.message,
      type: 'error',
      duration: 5 * 1000
    })
    return Promise.reject(error)
  }
)

export default service
