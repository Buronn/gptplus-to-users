import React from 'react';
import * as API from '../utils/api';
import * as ICON from '@fortawesome/free-solid-svg-icons'
import Feature from './feature';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'

const Navbar = (props) => {
    const handleLogout = () => {
        API.logout().then(() => {
            localStorage.setItem('token', '');
            window.location.href = '/';
        }).catch(err => console.log(err));
    }
    const showFeatures = () => {
        Feature();
    }
    return (
        <div>
            <nav class="navbar navbar-expand-lg navbar-light bg-light">
                <div class="container-fluid">
                    <div class="logo">
                        <img src="HC_PNG.webp" style={{ width: "276px", height: "71px" }} alt="ECS" width="100" height="50" />
                    </div>

                    <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarSupportedContent" aria-controls="navbarSupportedContent" aria-expanded="false" aria-label="Toggle navigation">
                        <span class="navbar-toggler-icon"></span>
                    </button>
                    <div class="collapse navbar-collapse" id="navbarSupportedContent">
                        <ul class="navbar-nav me-auto mb-2 mb-lg-0">

                        </ul>
                        <div class="d-flex">

                            {props.isLoggedIn ? (
                                <div>
                                    <button class="btn2 btn-outline-success my-2 m-2 my-sm-0" onClick={showFeatures}><FontAwesomeIcon icon={ICON.faInfoCircle} /></button>
                                    <button class="btn2 btn-outline-success" onClick={handleLogout}>Logout <FontAwesomeIcon icon={ICON.faSignOutAlt} /></button></div>
                            )
                                : null}

                        </div>
                    </div>
                </div>
            </nav>
        </div>
    )
}

export default Navbar;