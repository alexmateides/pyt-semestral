import {useState, useEffect} from 'react';
import axiosInstance from '../api/axiosInstance';
import CameraList from '../components/CameraList';
import CameraForm from '../components/CameraForm';
import NavBar from '../components/NavBar';

export default function CameraDashboard() {
    const [cameras, setCameras] = useState([]);
    const [selectedCamera, setSelectedCamera] = useState(null);
    const [showForm, setShowForm] = useState(false);

    useEffect(() => {
        fetchCameras();
    }, []);

    const fetchCameras = async () => {
        try {
            const response = await axiosInstance.get('/camera');
            setCameras(response.data);
        } catch (error) {
            console.error(error);
        }
    };

    const handleAddCamera = () => {
        setSelectedCamera(null);
        setShowForm(true);
    };

    const handleEditCamera = (camera) => {
        setSelectedCamera(camera);
        setShowForm(true);
    };

    const handleDeleteCamera = async (cameraName) => {
        if (!window.confirm(`Are you sure you want to delete camera: ${cameraName}?`)) return;
        try {
            await axiosInstance.delete(`/camera?name=${cameraName}`);
            fetchCameras();
        } catch (error) {
            console.error(error);
        }
    };

    const handleFormClose = () => {
        setShowForm(false);
        fetchCameras();
    };

    return (
        <div className="min-h-screen bg-gray-100">
            <NavBar previous=""/>

            <div className="container mx-auto p-4">
                <div className="flex justify-between items-center mb-4">
                    <h1 className="text-3xl font-bold">Camera Dashboard</h1>
                    <button
                        onClick={handleAddCamera}
                        className="bg-green-600 text-white px-4 py-2 rounded hover:bg-green-700"
                    >
                        Add Camera
                    </button>
                </div>

                <CameraList
                    cameras={cameras}
                    onEdit={handleEditCamera}
                    onDelete={handleDeleteCamera}
                />

                {/* Camera Form */}
                {showForm && (
                    <CameraForm
                        camera={selectedCamera}
                        onClose={handleFormClose}
                    />
                )}
            </div>
        </div>
    );
}
