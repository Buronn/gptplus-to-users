//Login component
import React, { useEffect } from 'react';
import * as api from '../utils/api.js';
import "./login.css"
process.env.NODE_TLS_REJECT_UNAUTHORIZED = "0"
const Login = () => {

    // Check if the user is already logged in

    useEffect(() => {
        const checkLogin = async () => {
            const res = await api.checkLogin();
            const data = await res.json();
            if (data.message === 'Check successful') {
                // Antes de haceer la petición, bloqueamos el botón de login y el input de contraseña y usuario
                document.getElementById('password').disabled = true;
                document.getElementById('user').disabled = true;
                document.getElementById('submit').disabled = true;
                // Cambiamos el color de fondo de los 3 inputs a uno un poco más oscuro
                document.getElementById('user').style.backgroundColor = '#2c3e50';
                document.getElementById('password').style.backgroundColor = '#2c3e50';
                document.getElementById('submit').style.backgroundColor = '#2c3e50';
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
        const user = document.getElementById('user').value;
        const password = document.getElementById('password').value;
        // Almacenamos el color actual del background de los 3 inputs
        const userBgColor = document.getElementById('user').style.backgroundColor;
        const passwordBgColor = document.getElementById('password').style.backgroundColor;
        const submitBgColor = document.getElementById('submit').style.backgroundColor;
        try {
            // Antes de haceer la petición, bloqueamos el botón de login y el input de contraseña y usuario
            document.getElementById('password').disabled = true;
            document.getElementById('user').disabled = true;
            document.getElementById('submit').disabled = true;
            // Cambiamos el color de fondo de los 3 inputs a uno un poco más oscuro
            document.getElementById('user').style.backgroundColor = '#2c3e50';
            document.getElementById('password').style.backgroundColor = '#2c3e50';
            document.getElementById('submit').style.backgroundColor = '#2c3e50';

            const res = await api.login(user, password);
            const data = await res.json(); // Espera a que se resuelva la promesa de la respuesta y extrae los datos de la respuesta
            if (data.token) {
                localStorage.setItem('token', data.token);
                localStorage.setItem('username', data.username);
                if (data.username === 'admin')
                    window.location.href = '/admin';
                else
                    window.location.href = '/home';
            } else {
                document.getElementById('password').disabled = false;
                document.getElementById('user').disabled = false;
                document.getElementById('submit').disabled = false;
                // Cambiamos el color de fondo de los 3 inputs a uno un poco más oscuro
                document.getElementById('user').style.backgroundColor = userBgColor;
                document.getElementById('password').style.backgroundColor = passwordBgColor;
                document.getElementById('submit').style.backgroundColor = submitBgColor;
                document.getElementById('error').style.display = 'block';

                await sleep(2000);
                document.getElementById('error').style.display = 'none';
            }
        } catch (err) {
            console.log(err);
        }
    }

    const sleep = (milliseconds) => {
        return new Promise(resolve => setTimeout(resolve, milliseconds))
    }


    return (
        <div className="login">
            <h1>ChatGPT Plus</h1>
            <form onSubmit={handleSubmit}>
                <input type="text" id="user" placeholder="Username" required="required" />
                <input type="password" id="password" placeholder="Password" required="required" />
                <button type="submit" id="submit" className="btn btn-primary btn-block btn-large">Join</button>
            </form>
            <span id="error" style={{
                display: 'none',
                color: 'white',
                fontSize: '0.7em',
                marginTop: '1em',
                marginBottom: '1em',
                textAlign: 'center',
                backgroundColor: '#ff6a7669',
                borderRadius: '5px',
                padding: '0.5em',
                width: '100%',
                boxSizing: 'border-box',
                border: '1px solid red'
            }}>Username or password incorrect</span>
        </div>
    );
}

export default Login;