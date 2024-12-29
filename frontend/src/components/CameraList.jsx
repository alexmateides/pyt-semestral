import { Link } from 'react-router-dom';

export default function CameraList({ cameras, onEdit, onDelete }) {
    return (
        <div className="bg-white p-4 rounded shadow">
            {cameras.length === 0 ? (
                <p>No cameras found.</p>
            ) : (
                <table className="w-full table-auto">
                    <thead>
                    <tr className="text-left">
                        <th className="px-4 py-2">Name</th>
                        <th className="px-4 py-2">Model</th>
                        <th className="px-4 py-2">IP</th>
                        <th className="px-4 py-2">Actions</th>
                    </tr>
                    </thead>
                    <tbody>
                    {cameras.map((cam) => (
                        <tr key={cam.name}>
                            <td className="border px-4 py-2">
                                <Link to={`/camera/${cam.name}`} className="text-blue-600 hover:underline">
                                    {cam.name}
                                </Link>
                            </td>
                            <td className="border px-4 py-2">{cam.model}</td>
                            <td className="border px-4 py-2">{cam.ip}</td>
                            <td className="border px-4 py-2 flex gap-2">
                                <button
                                    onClick={() => onEdit(cam)}
                                    className="bg-yellow-600 text-white px-2 py-1 rounded hover:bg-yellow-700"
                                >
                                    Edit
                                </button>
                                <button
                                    onClick={() => onDelete(cam.name)}
                                    className="bg-red-600 text-white px-2 py-1 rounded hover:bg-red-700"
                                >
                                    Delete
                                </button>
                            </td>
                        </tr>
                    ))}
                    </tbody>
                </table>
            )}
        </div>
    );
}
