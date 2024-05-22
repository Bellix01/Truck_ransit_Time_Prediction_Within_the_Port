import { lazy, Suspense } from 'react';
import { Routes, Route } from 'react-router-dom';
import NavBar from './Components/NavBar';
import Footer from './Components/Footer';

        
const Home = lazy(() => import('./Pages/Home'));
const About = lazy(() => import('./Pages/About'));
const Eda = lazy(() => import('./Pages/Eda'));
const Prediction = lazy(() => import('./Pages/Prediction'));
const Details = lazy(() => import('./Pages/Details'));
const NoMatch = lazy(() => import('./Components/NoMatch'));

const App = () => {
	return (
		<>
		<div className="wrapper">
			<NavBar />
			<div className="main-content">
			<Suspense fallback={<div className="container">Loading...</div>}>
				<Routes>
					<Route path="/" element={<Home />} />
					<Route path="/about" element={<About />} />
					<Route path="/Eda" element={<Eda />} />
					<Route path="/Prediction" element={<Prediction />} />
					<Route path="/products/:slug" element={<Details />} />
					<Route path="*" element={<NoMatch />} />
				</Routes>
			</Suspense>
			</div>
			<Footer />
		</div>
		</>
	);
};

export default App;
