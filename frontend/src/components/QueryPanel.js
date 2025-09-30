import React, { useState } from 'react';
import apiClient from '../apiClient.js';

const QueryPanel = ({ setResults, setIsLoading, setQueryError }) => {
  const [query, setQuery] = useState('');

  const handleQuery = async (e) => {
    e.preventDefault();
    if (!query.trim()) {
      setQueryError('Please enter a query.');
      return;
    }
    
    setIsLoading(true);
    setResults(null);
    setQueryError(null);

    try {
      const response = await apiClient.post('/api/query', { query });
      setResults(response.data);
    } catch (error) {
      const errorMessage = error.response?.data?.detail || 'An error occurred while processing the query.';
      setQueryError(errorMessage);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <form onSubmit={handleQuery} className="mb-6">
      <label htmlFor="query-input" className="block text-lg font-medium text-gray-700 mb-2">
        Ask a question about your data
      </label>
      <div className="flex items-center space-x-2">
        <input
          id="query-input"
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          className="flex-grow px-4 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
          placeholder="e.g., How many employees in Engineering?"
        />
        <button
          type="submit"
          className="bg-indigo-600 text-white py-2 px-6 rounded-md hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
        >
          Query
        </button>
      </div>
    </form>
  );
};

export default QueryPanel;

