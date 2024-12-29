import { Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

export default function NavBar({ previous }) {
    const { logout } = useAuth();

    return (
        <nav className="bg-white shadow-md mb-4">
            <div className="container mx-auto px-4 py-3 flex justify-between items-center">
                <div className="flex items-center">
                    {previous && previous.trim() !== "" && (
                        <Link
                            to={`/${previous}`}
                            className="text-gray-600 hover:text-gray-800 mr-4"
                        >
                            <svg
                                xmlns="http://www.w3.org/2000/svg"
                                className="h-6 w-6"
                                fill="none"
                                viewBox="0 0 24 24"
                                stroke="currentColor"
                            >
                                <path
                                    strokeLinecap="round"
                                    strokeLinejoin="round"
                                    strokeWidth={2}
                                    d="M15 19l-7-7 7-7"
                                />
                            </svg>
                        </Link>
                    )}
                    <div className="text-xl font-bold">
                        <Link to="/camera">Tapo 320WS</Link>
                    </div>
                </div>
                <button
                    onClick={logout}
                    className="bg-red-600 text-white px-4 py-2 rounded hover:bg-red-700"
                >
                    Logout
                </button>
            </div>
        </nav>
    );
}
