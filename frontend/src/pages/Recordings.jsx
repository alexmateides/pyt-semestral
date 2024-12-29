import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import axiosInstance from '../api/axiosInstance';
import NavBar from '../components/NavBar';
import DownloadLoader from '../components/DownloadLoader';
import axios from 'axios';

export default function Recordings() {
    const { name } = useParams();
    const [startDate, setStartDate] = useState('');
    const [endDate, setEndDate] = useState('');
    const [recordings, setRecordings] = useState([]);
    const [selectedRecording, setSelectedRecording] = useState(null);
    const [loading, setLoading] = useState(false);
    const [cancelSource, setCancelSource] = useState(null);

    const calculateLastThreeDays = () => {
        const today = new Date();
        const threeDaysAgo = new Date();
        threeDaysAgo.setDate(today.getDate() - 3);

        const formatDate = (date) => date.toISOString().split('T')[0];

        return {
            startDate: formatDate(threeDaysAgo),
            endDate: formatDate(today),
        };
    };

    useEffect(() => {
        const { startDate, endDate } = calculateLastThreeDays();
        setStartDate(startDate);
        setEndDate(endDate);
        fetchRecordings(startDate, endDate);
    }, []);

    const fetchRecordings = async (start = startDate, end = endDate) => {
        try {
            const response = await axiosInstance.get(`/tapo-320ws/recordings/${name}`, {
                params: {
                    start_date: start,
                    end_date: end,
                },
            });
            setRecordings(response.data);
        } catch (error) {
            console.error(error);
        }
    };

    const handleCheckboxChange = (recordingId, recordingDate) => {
        if (selectedRecording?.id === recordingId && selectedRecording?.date === recordingDate) {
            setSelectedRecording(null);
        } else {
            setSelectedRecording({ id: recordingId, date: recordingDate });
        }
    };

    const handleDownload = async () => {
        if (!selectedRecording) {
            alert('Please select a recording to download.');
            return;
        }

        const { id, date } = selectedRecording;
        setLoading(true);

        const source = axios.CancelToken.source();
        setCancelSource(source);

        try {
            const response = await axiosInstance.post(
                `/tapo-320ws/recordings/download/${name}`,
                { date, id },
                {
                    responseType: 'blob',
                    cancelToken: source.token,
                }
            );

            const url = window.URL.createObjectURL(new Blob([response.data]));
            const link = document.createElement('a');
            link.href = url;
            link.setAttribute('download', `${name}_${date}_${id}.mp4`);
            document.body.appendChild(link);
            link.click();
            link.parentNode.removeChild(link);
            window.URL.revokeObjectURL(url);
        } catch (error) {
            if (axios.isCancel(error)) {
                console.log('Download cancelled');
            } else {
                console.error('Download failed', error);
                alert('Failed to initiate download');
            }
        } finally {
            setLoading(false);
            setCancelSource(null);
        }
    };

    const cancelDownload = () => {
        if (cancelSource) {
            cancelSource.cancel('Download cancelled by the user.');
            setLoading(false);
        }
    };

    return (
        <div className="min-h-screen bg-gray-100">
            {loading && <DownloadLoader onCancel={cancelDownload} />}
            <NavBar previous={`camera/${name}`} />
            <div className="container mx-auto p-4">
                <h1 className="text-3xl font-bold mb-4">Recordings for camera: {name}</h1>

                <div className="flex items-center gap-4 mb-4">
                    <div>
                        <label className="block mb-1">Start Date</label>
                        <input
                            type="date"
                            className="border rounded px-2 py-1"
                            value={startDate}
                            onChange={(e) => setStartDate(e.target.value)}
                        />
                    </div>

                    <div>
                        <label className="block mb-1">End Date</label>
                        <input
                            type="date"
                            className="border rounded px-2 py-1"
                            value={endDate}
                            onChange={(e) => setEndDate(e.target.value)}
                        />
                    </div>

                    <button
                        onClick={() => fetchRecordings()}
                        className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700 mt-5"
                    >
                        Fetch
                    </button>
                </div>

                {/* Legend */}
                <div className="flex items-center gap-4 mb-4">
                    <div className="flex items-center gap-2">
                        <div className="w-4 h-4 bg-green-500 rounded"></div>
                        <span>Downloaded on server</span>
                    </div>
                    <div className="flex items-center gap-2">
                        <div className="w-4 h-4 bg-orange-500 rounded"></div>
                        <span>On camera</span>
                    </div>
                </div>

                {/* Recordings */}
                <div className="bg-white p-4 rounded shadow">
                    {recordings.length === 0 ? (
                        <p>No recordings found</p>
                    ) : (
                        recordings.map((rec) => (
                            <div key={`${rec.id}-${rec.date}`} className="flex items-center mb-2">
                                <div
                                    className={`w-4 h-4 mr-2 rounded ${
                                        rec.downloaded ? 'bg-green-500' : 'bg-orange-500'
                                    }`}
                                ></div>
                                <input
                                    type="radio"
                                    checked={
                                        selectedRecording?.id === rec.id &&
                                        selectedRecording?.date === rec.date
                                    }
                                    onChange={() => handleCheckboxChange(rec.id, rec.date)}
                                    className="mr-2"
                                />
                                <span>
                                    {rec.date}
                                    ,- {rec.id}
                                </span>
                            </div>
                        ))
                    )}
                </div>

                {selectedRecording && (
                    <button
                        onClick={handleDownload}
                        className="bg-green-600 text-white px-4 py-2 rounded hover:bg-green-700 mt-4"
                    >
                        Download Selected
                    </button>
                )}
            </div>
        </div>
    );
}