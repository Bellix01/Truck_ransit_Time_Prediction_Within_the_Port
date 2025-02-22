import React from 'react';
import { NavLink } from 'react-router-dom';
import logo from './logo.png'
const NavBar = () => {
	return (
		// <div className="main-content">
			<nav>
				<div className="nav-items container">
					<div className="logo">
						<a href="/">
							<img src={logo} alt="Your Logo" />
						</a>
					</div>
					<ul>
						<li>
							<NavLink to="/">Home</NavLink>
						</li>
						<li>
							<NavLink to="/Prediction">Prediction</NavLink>
						</li>
						
						<li>
							<NavLink to="/Eda">EDA</NavLink>
						</li>
						<li>
							<NavLink to="/about">About</NavLink>
						</li>
					</ul>
				</div>
			</nav>
		// </div>
	);
};

export default NavBar;
