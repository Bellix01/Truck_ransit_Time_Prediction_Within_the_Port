import React from 'react';
import { Link } from 'react-router-dom';
import './Home.css';
import coolImage from './image.jpeg'; // Adjust the path as necessary

const Home = () => {
  return (
    <div className="container">
      <div className="content">
        <div className="text-section">
          <h1>Reliable Truck Transit Times</h1>
          <p>Get accurate, real-time information on truck transit times within our port. Optimize your logistics and improve efficiency.</p>
          <Link to="/Eda">
            <button className="btn">Get Started</button>
          </Link>
        </div>
        <div className="image-placeholder">
          <img src={coolImage} alt="Cool and Nice" className="image" />
        </div>
      </div>
      <div className="info-section">
        <div className="info-card">
          <h2>Transit Times</h2>
          <h3>Reliable and Efficient</h3>
          <p>Our port offers average truck transit times of just 2-3 hours, with a reliability rate of over 95%. We're committed to optimizing your logistics and keeping your supply chain moving.</p>
        </div>
        <div className="info-card">
          <h2>Port Location</h2>
          <h3>Strategically Located</h3>
          <p>Our port is situated in a prime location, with easy access to major highways and transportation hubs. This allows for seamless, efficient movement of goods in and out of the port.</p>
        </div>
      </div>
     
    </div>
  );
};

export default Home;
