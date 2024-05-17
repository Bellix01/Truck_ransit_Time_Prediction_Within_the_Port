import { Link } from 'react-router-dom';
import './Home.css';
import logo from './fatuch.png'
const Home = () => {
  return (
    <div className="home">
      <div className="content">
        <div className="text-section">
          <h1>Reliable Truck Transit Times</h1>
          <p>Get accurate, real-time information on truck transit times within our port. Optimize your logistics and improve efficiency.</p>
          <Link to="/Eda">
            <button className="btn">Get Started</button>
          </Link>
        </div>
        <div className="image-placeholder">
        <a href="/">
							<img src={logo} alt="Your Logo" />
						</a>
            
          
        </div>
      </div>
    </div>
  );
};

export default Home;
