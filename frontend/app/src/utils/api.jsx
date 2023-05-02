import { CONFIG } from '../config.jsx';

const headers = {
    'Content-Type': 'application/json',
    'Accept': 'application/json',
    'X-Auth-Token': localStorage.getItem('token')
};

export function login(user, password) {
    return fetch(CONFIG.API_BASE_URL + '/login', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            username: user,
            password: password
        })
    })
}

export function logout() {
    // Delete localstorage token
    localStorage.removeItem('token');
    localStorage.removeItem('username');
    return fetch(CONFIG.API_BASE_URL + '/logout', {
        method: 'POST',
        headers: headers
    })
}

export function users() {
    return fetch(CONFIG.API_BASE_URL + '/users', {
        method: 'GET',
        headers: headers
    })
}

export function register(username, password) {
    return fetch(CONFIG.API_BASE_URL + '/register', {
        method: 'POST',
        headers: headers,
        body: JSON.stringify({
            username: username,
            password: password
        })
    })
}

export function changePassword(password, new_password) {
    return fetch(CONFIG.API_BASE_URL + '/change-password', {
        method: 'PUT',
        headers: headers,
        body: JSON.stringify({
            password: password,
            new_password: new_password
        })
    })
}

export function deleteUser(id) {
    return fetch(CONFIG.API_BASE_URL + '/delete-user', {
        method: 'POST',
        headers: headers,
        body: JSON.stringify({
            id: id
        })
    })
}

export function checkLogin() {
    return fetch(CONFIG.API_BASE_URL + '/check-login', {
        method: 'GET',
        headers: headers
    })
}

export function getConversations() {
    return fetch(CONFIG.API_BASE_URL + '/conversations', {
        method: 'GET',
        headers: headers
    })
}

export function getMessages(conversationId) {
    return fetch(CONFIG.API_BASE_URL + '/messages/' + conversationId, {
        method: 'GET',
        headers: headers
    })
}

export function iframeUrl() {
    return fetch(CONFIG.API_BASE_URL + '/metabase', {
        method: 'GET',
        headers: headers
    })
}

export function sendMessage(conversationId, childId, message) {
    return fetch(CONFIG.API_BASE_URL + '/messages', {
        method: 'POST',
        headers: headers,
        body: JSON.stringify({
            conversation_id: conversationId,
            parent_message_id: childId,
            message: message
        })
    })
}

export function changeTitle(conversationId, title) {
    return fetch(CONFIG.API_BASE_URL + '/change-title', {
        method: 'PUT',
        headers: headers,
        body: JSON.stringify({
            conversation_id: conversationId,
            title: title
        })
    })
}

export function createConversation(title) {
    return fetch(CONFIG.API_BASE_URL + '/conversations', {
        method: 'POST',
        headers: headers,
        body: JSON.stringify({
            message: title
        })
    })
}

export function deleteConversation(conversationId) {
    return fetch(CONFIG.API_BASE_URL + '/conversations/' + conversationId, {
        method: 'DELETE',
        headers: headers
    })
}