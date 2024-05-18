import React from 'react';
import { NavLink } from 'react-router-dom';
import './Footer.css'
const Footer = () => {
	return (
        <footer className="footer">
            <p>&copy; 2024 By Ammine & Fatima.</p>
        
            <ul className="footer-links">
                <li>
                    <NavLink to="/terms">Terms of Service</NavLink>
                </li>
                <li>
                    <NavLink to="/privacy">Privacy Policy</NavLink>
                </li>
                <li>
                    <NavLink to="/contact">Contact</NavLink>
                </li>
          
            </ul>
       
        </footer>
	);
};

export default Footer;