import React from 'react';
import './DownloadLoader.css';

const DownloadLoader = ({ onCancel }) => {
    return (
        <div className="downloader-container">
            <div className="downloader"></div>
            <div className="downloader-message">Downloading...</div>
            <button
                onClick={onCancel}
                className="mt-4 px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700"
            >
                Cancel
            </button>
        </div>
    );
};

export default DownloadLoader;
