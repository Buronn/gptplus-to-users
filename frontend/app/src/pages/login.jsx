import React, { useState, useEffect } from 'react';
import * as api from '../utils/api.jsx';
import "./login.css"

const Login = () => {
    const [user, setUser] = useState('');
    const [password, setPassword] = useState('');
    const [isSubmitting, setIsSubmitting] = useState(false);
    const [error, setError] = useState(false);

    useEffect(() => {
        const checkLogin = async () => {
            const res = await api.checkLogin();
            const data = await res.json();
            if (data.message === 'Check successful') {
                setIsSubmitting(true);
                if (data.username === 'admin')
                    window.location.href = '/admin';
                else
                    window.location.href = '/home';
            }
        };
        checkLogin();
    }, []);

    const handleSubmit = async (e) => {
        e.preventDefault();
        setIsSubmitting(true);

        try {
            const res = await api.login(user, password);
            const data = await res.json();
            if (data.token) {
                localStorage.setItem('token', data.token);
                localStorage.setItem('username', data.username);
                if (data.username === 'admin')
                    window.location.href = '/admin';
                else
                    window.location.href = '/home';
            } else {
                setIsSubmitting(false);
                setError(true);

                setTimeout(() => {
                    setError(false);
                }, 2000);
            }
        } catch (err) {
            console.log(err);
        }
    }

    return (
        <div className="login">
            <h1>ChatGPT Plus</h1>
            <form onSubmit={handleSubmit}>
                <input
                    type="text"
                    placeholder="Username"
                    required
                    value={user}
                    onChange={(e) => setUser(e.target.value)}
                    disabled={isSubmitting}
                />
                <input
                    type="password"
                    placeholder="Password"
                    required
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    disabled={isSubmitting}
                />
                <button
                    type="submit"
                    className="btn btn-primary btn-block btn-large"
                    disabled={isSubmitting}
                >
                    Join
                </button>
            </form>
            {error && (
                <span className="error-message">
                    Username or password incorrect
                </span>
            )}
        </div>
    );
}

export default Login;
