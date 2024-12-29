import { useState } from 'react';
import axiosInstance from '../api/axiosInstance';

export default function CameraForm({ camera, onClose }) {
    const [formData, setFormData] = useState({
        name: camera?.name || '',
        model: camera?.model || '',
        ip: camera?.ip || '',
        username: camera?.username || '',
        password: camera?.password || '',
        camera_username: camera?.camera_username || '',
        camera_password: camera?.camera_password || '',
    });

    const handleChange = (e) => {
        const { name, value } = e.target;
        setFormData((prev) => ({ ...prev, [name]: value }));
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        try {
            await axiosInstance.post('/camera', formData);
            onClose();
        } catch (error) {
            console.error(error);
        }
    };

    return (
        <div className="fixed top-0 left-0 w-full h-full bg-black bg-opacity-50 flex items-center justify-center">
            <form
                onSubmit={handleSubmit}
                className="bg-white p-6 rounded shadow-md w-full max-w-md"
            >
                <h2 className="text-xl font-semibold mb-4">
                    {camera ? 'Edit Camera' : 'Add Camera'}
                </h2>

                <div className="mb-4">
                    <label className="block mb-1 font-medium">Name</label>
                    <input
                        type="text"
                        name="name"
                        className="w-full border rounded px-2 py-1"
                        value={formData.name}
                        onChange={handleChange}
                        disabled={camera}
                    />
                </div>

                <div className="mb-4">
                    <label className="block mb-1 font-medium">Model</label>
                    <input
                        type="text"
                        name="model"
                        className="w-full border rounded px-2 py-1"
                        value={formData.model}
                        onChange={handleChange}
                    />
                </div>

                <div className="mb-4">
                    <label className="block mb-1 font-medium">IP</label>
                    <input
                        type="text"
                        name="ip"
                        className="w-full border rounded px-2 py-1"
                        value={formData.ip}
                        onChange={handleChange}
                    />
                </div>

                {/* Additional fields */}
                <div className="mb-4">
                    <label className="block mb-1 font-medium">Username</label>
                    <input
                        type="text"
                        name="username"
                        className="w-full border rounded px-2 py-1"
                        value={formData.username}
                        onChange={handleChange}
                    />
                </div>

                <div className="mb-4">
                    <label className="block mb-1 font-medium">Password</label>
                    <input
                        type="password"
                        name="password"
                        className="w-full border rounded px-2 py-1"
                        value={formData.password}
                        onChange={handleChange}
                    />
                </div>

                <div className="mb-4">
                    <label className="block mb-1 font-medium">Camera Username</label>
                    <input
                        type="text"
                        name="camera_username"
                        className="w-full border rounded px-2 py-1"
                        value={formData.camera_username}
                        onChange={handleChange}
                    />
                </div>

                <div className="mb-4">
                    <label className="block mb-1 font-medium">Camera Password</label>
                    <input
                        type="password"
                        name="camera_password"
                        className="w-full border rounded px-2 py-1"
                        value={formData.camera_password}
                        onChange={handleChange}
                    />
                </div>

                <div className="flex gap-2">
                    <button
                        type="submit"
                        className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700"
                    >
                        Save
                    </button>
                    <button
                        type="button"
                        onClick={onClose}
                        className="bg-gray-300 text-black px-4 py-2 rounded hover:bg-gray-400"
                    >
                        Cancel
                    </button>
                </div>
            </form>
        </div>
    );
}
