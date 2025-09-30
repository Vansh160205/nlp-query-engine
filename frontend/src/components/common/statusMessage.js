import React from 'react';

const StatusMessage = ({ message, type }) => {
  if (!message) return null;

  const baseClasses = 'border px-4 py-3 rounded-md relative mt-2';
  const typeClasses = type === 'error' 
    ? 'bg-red-100 border-red-400 text-red-700' 
    : 'bg-green-100 border-green-400 text-green-700';

  return (
    <div className={`${baseClasses} ${typeClasses}`} role="alert">
      <span className="block sm:inline">{message}</span>
    </div>
  );
};

export default StatusMessage;
