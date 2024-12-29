import React from 'react';
import './Loader.css';

const Loader = () => {
    return (
        <div className="loader-container">
            <div className="loader"></div>
            <div className="loader-message">Loading Stream...</div>
        </div>
    );
};

export default Loader;
