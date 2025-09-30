import React, { useState } from 'react';
import apiClient from '../apiClient.js';
import Spinner from './common/spinner.js';

const DatabaseConnector = ({ setSchema, setDbStatus }) => {
  const [connectionString, setConnectionString] = useState('postgresql://user:password@localhost:5432/company_db');
  const [isLoading, setIsLoading] = useState(false);

  const handleConnect = async (e) => {
    e.preventDefault();
    setIsLoading(true);
    setDbStatus({ message: null, type: null });
    try {
      // Create a URL-encoded version of the connection string for the backend.
      // This specifically handles the case where a password might contain '@'.
      const lastAtIndex = connectionString.lastIndexOf('@');
      let encodedConnectionString = connectionString;

      // We only encode if an '@' exists and it's part of the user:password section.
      if (lastAtIndex > connectionString.indexOf('://') + 2) {
        const userInfoPart = connectionString.substring(0, lastAtIndex);
        const hostPart = connectionString.substring(lastAtIndex);
        // Replace any '@' in the user/password part with its URL-encoded equivalent '%40'.
        const encodedUserInfoPart = userInfoPart.replace(/@/g, '%40');
        encodedConnectionString = encodedUserInfoPart + hostPart;
      }

      const formData = new FormData();
      // Send the safely encoded string to the backend.
      formData.append('connection_string', encodedConnectionString);
      
      const response = await apiClient.post('/api/connect-database', formData);
      
      setSchema(response.data.schema);
      setDbStatus({ message: 'Successfully connected and discovered schema!', type: 'success' });
    } catch (error) {
      const errorMessage = error.response?.data?.detail || 'Failed to connect to the database.';
      setDbStatus({ message: errorMessage, type: 'error' });
      setSchema(null);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="bg-white p-6 rounded-lg shadow-md">
      <h2 className="text-xl font-semibold mb-4 text-gray-800">1. Connect to Database</h2>
      <form onSubmit={handleConnect}>
        <div className="mb-4">
          <label htmlFor="connection-string" className="block text-sm font-medium text-gray-600 mb-1">Connection String</label>
          <input
            id="connection-string"
            type="text"
            value={connectionString}
            onChange={(e) => setConnectionString(e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
            placeholder="e.g., postgresql://user:pass@host/db"
          />
        </div>
        <button
          type="submit"
          disabled={isLoading}
          className="w-full flex justify-center items-center bg-indigo-600 text-white py-2 px-4 rounded-md hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:bg-indigo-300"
        >
          {isLoading ? <Spinner /> : 'Connect & Analyze'}
        </button>
      </form>
    </div>
  );
};

export default DatabaseConnector;
