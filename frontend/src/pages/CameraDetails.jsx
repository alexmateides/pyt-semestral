import {useState, useEffect} from 'react';
import {useParams, useNavigate} from 'react-router-dom';
import axiosInstance from '../api/axiosInstance';
import NavBar from '../components/NavBar';
import Loader from '../components/Loader';

export default function CameraDetails() {
    const {name} = useParams();
    const navigate = useNavigate();
    const [lightOn, setLightOn] = useState(false);
    const [nightVisionOn, setNightVisionOn] = useState(false);
    const [streamUrl, setStreamUrl] = useState("");
    const [frame, setFrame] = useState(null);

    useEffect(() => {
        fetchStreamUrl();
        fetchLightStatus();
        fetchNightStatus();
    }, [name]);

    useEffect(() => {
        if (!streamUrl) return;

        const ws = new WebSocket(streamUrl);

        ws.onmessage = (event) => {
            console.log(event.data);
            setFrame(event.data);
        };

        ws.onerror = (error) => {
            console.error("WebSocket error:", error);
        };

        ws.onclose = () => {
            console.log("WebSocket connection closed");
        };

        return () => {
            ws.close();
        };
    }, [streamUrl]);

    const fetchStreamUrl = async () => {
        try {
            const response = await axiosInstance.get(`/tapo-320ws/stream/${name}`);
            setStreamUrl(response.data.streamUrl);
        } catch (error) {
            console.error(error);
        }
    };

    const fetchLightStatus = async () => {
        try {
            const response = await axiosInstance.get(`/tapo-320ws/light/${name}`);
            setLightOn(response.data.status);
        } catch (error) {
            console.error(error);
        }
    };

    const toggleLight = async () => {
        try {
            const response = await axiosInstance.post(`/tapo-320ws/light/${name}`);
            setLightOn(response.data.status);
        } catch (error) {
            console.error(error);
        }
    };

    const fetchNightStatus = async () => {
        try {
            const response = await axiosInstance.get(`/tapo-320ws/night/${name}`);
            setNightVisionOn(response.data.status);
        } catch (error) {
            console.error(error);
        }
    };

    const toggleNightVision = async () => {
        try {
            const response = await axiosInstance.post(`/tapo-320ws/night/${name}`);
            setNightVisionOn(response.data.status);
        } catch (error) {
            console.error(error);
        }
    };

    const startStopRecording = async () => {
        alert('Not implemented yet');
    };

    const goToRecordings = () => {
        navigate(`/recordings/${name}`);
    };

    return (
        <div className="min-h-screen bg-gray-100">
            <NavBar previous="camera"/>
            <div className="container mx-auto p-4">
                <h1 className="text-3xl font-bold mb-4">Camera: {name}</h1>

                {/* Camera controls */}
                <div className="flex gap-4">
                    <button
                        onClick={toggleLight}
                        className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700"
                    >
                        {lightOn ? 'Light ON' : 'Light OFF'}
                    </button>

                    <button
                        onClick={toggleNightVision}
                        className="bg-purple-600 text-white px-4 py-2 rounded hover:bg-purple-700"
                    >
                        {nightVisionOn ? 'Night ON' : 'Night OFF'}
                    </button>

                    <button
                        onClick={goToRecordings}
                        className="bg-gray-600 text-white px-4 py-2 rounded hover:bg-gray-700"
                    >
                        View Recordings
                    </button>

                    <button
                        onClick={startStopRecording}
                        className="bg-red-600 text-white px-4 py-2 rounded hover:bg-red-700"
                    >
                        Start/Stop Recording
                    </button>
                </div>

                {/* Stream view */}
                <div className="w-full h-400 bg-gray-100 text-white flex items-center justify-center mb-4">
                    {frame ? (
                        <img
                            src={frame}
                            alt="Live stream"
                            className="w-full h-full object-cover"
                            style={{width: '60%', height: '60%', objectFit: 'contain'}}
                        />
                    ) : (
                        <Loader/>
                    )}
                </div>
            </div>
        </div>
    );
}
