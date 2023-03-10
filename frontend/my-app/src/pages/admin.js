import React, { useEffect, useState } from 'react';
import * as api from '../utils/api.js';
import { DashboardDetails, Navbar } from '../components';
import Row from 'react-bootstrap/Row';
import Col from 'react-bootstrap/Col';
import Container from 'react-bootstrap/Container';
import './admin.css';
const Admin = () => {
	const [loggedIn, setLoggedIn] = useState(false);
	const [isOpen, setIsOpen] = useState(false);

	useEffect(() => {
		const checkLogin = async () => {
			const res = await api.checkLogin();
			if (res.status === 200) {
				setLoggedIn(true);
			}
			else {
				window.location.href = '/';
			}
		};
		checkLogin();
	}, []);

	return (
		<div className="adminPage">{
			loggedIn ? (

				<Container fluid>
					<Row>
						{isOpen && (
							<Col
								sm={12}
								md={2}
								className="text-bg-primary text-left"
								style={{ minHeight: '100vh' }}
							>
							</Col>
						)}

						<Col md={isOpen ? 10 : 12} sm={12}>
							<Container>
								<Navbar isOpen={isOpen} setIsOpen={setIsOpen} />
								<DashboardDetails />
							</Container>
						</Col>
					</Row>
				</Container>

			) : (
				<div class="loading">
					<svg version="1.2" height="300" width="600" xmlns="http://www.w3.org/2000/svg" viewport="0 0 60 60">
						<path id="pulsar" stroke="rgba(0,155,155,1)" fill="none" stroke-width="1" stroke-linejoin="round" d="M0,90L250,90Q257,60 262,87T267,95 270,88 273,92t6,35 7,-60T290,127 297,107s2,-11 10,-10 1,1 8,-10T319,95c6,4 8,-6 10,-17s2,10 9,11h210" />
						<use xlinkHref="#pulsar" x="0" y="0" fill="rgba(0,0,0,0)" stroke="rgba(0,155,155,.5)" stroke-width="1" />
						<use xlinkHref="#pulsar" x="0" y="0" fill="rgba(0,0,0,0)" stroke="rgba(0,155,155,.5)" stroke-width="1" />
						<use xlinkHref="#pulsar" x="0" y="0" fill="rgba(0,0,0,0)" stroke="rgba(0,155,155,.5)" stroke-width="1" />
						<use xlinkHref="#pulsar" x="0" y="0" fill="rgba(0,0,0,0)" stroke="rgba(0,155,155,.5)" stroke-width="1" />
					</svg>
				</div>
			)}
		</div >
	);
};

export default Admin;

