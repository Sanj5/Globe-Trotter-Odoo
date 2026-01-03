import React from 'react';
import './ActivityModal.css';

const ActivityModal = ({ children, onClose }) => {
  return (
    <div className="activity-modal-overlay" onClick={onClose}>
      <div className="activity-modal-content" onClick={(e) => e.stopPropagation()}>
        {children}
      </div>
    </div>
  );
};

export default ActivityModal;
