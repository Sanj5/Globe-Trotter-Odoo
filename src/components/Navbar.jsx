import { Link } from "react-router-dom";

const Navbar = () => {
  return (
    <nav className="navbar">
      <h1>Tourist Planner</h1>
      <div>
        <Link to="/">Home</Link>
        <Link to="/travel-planner">Planner</Link>
        <Link to="/saved-trips">Saved Trips</Link>
        <Link to="/profile">Profile</Link>
      </div>
    </nav>
  );
};

export default Navbar;
