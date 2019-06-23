import Qs from 'qs';
import apiConfig from './api_config';

const axios = require('axios').create({
    baseURL: apiConfig.baseURL,
    timeout: apiConfig.timeout,
    withCredentials: true, // 允许跨域 cookie
    headers: {
        'X-Requested-With': 'x-requested-with',
        'X-System-ID': 1, // 系统ID
    },
    xsrfCookieName: '_xsrf',
    xsrfHeaderName: 'X-Xsrftoken',
    transformRequest: [function(data) {
        data = Qs.stringify(data);
        // console.log("transformRequest->", data);
        return data;
    }],
    transformResponse: [function(data) {
        let json = {};
        try {
            json = JSON.parse(data);
        } catch (e) {
            json = {};
        }
        return json;
    }],
});

// respone拦截
axios.interceptors.response.use(
    response => response,
    error => {
        console.log(error);  // for debug
        return Promise.reject(error);
    }
);

// get
export const doGet = (url, params, auth={}, timeout=apiConfig.timeout) => {
    return axios.get(url, {
        params: params,
        auth: auth,
        timeout: timeout,
    });
};

// put
export const doPut = (url, data) => {
    return axios({
        method: 'put',
        url: `/${url}`,
        data: data,
    });
};

// post
export const doPost = (url, data, timeout=apiConfig.timeout) => {
    return axios({
        method: 'post',
        url: `/${url}`,
        data: data,
        timeout: timeout
    });
};

// delete
export const doDelete = (url, data) => {
    return axios({
        method: 'delete',
        url: `/${url}`,
        data: data
    });
};