import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { useAuth } from './context/AuthContext';

import Login from './pages/Login';
import CameraDashboard from './pages/CameraDashboard';
import CameraDetails from './pages/CameraDetails';
import Recordings from './pages/Recordings';

function App() {
    const { isAuthenticated } = useAuth();

    return (
        <Router>
            <Routes>
                <Route path="/login" element={<Login />} />

                {/* Protected Routes */}
                {isAuthenticated ? (
                    <>
                        <Route path="/camera" element={<CameraDashboard />} />
                        <Route path="/camera/:name" element={<CameraDetails />} />
                        <Route path="/recordings/:name" element={<Recordings />} />
                        <Route path="*" element={<Navigate to="/camera" />} />
                    </>
                ) : (
                    <Route path="*" element={<Navigate to="/login" />} />
                )}
            </Routes>
        </Router>
    );
}

export default App;
