import React from 'react';
import Spinner from './common/spinner';
import StatusMessage from './common/statusMessage';

const ResultsView = ({ results, isLoading, queryError }) => {
  if (isLoading) {
    return (
      <div className="flex justify-center items-center mt-10">
         <svg className="animate-spin h-8 w-8 text-indigo-600" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
           <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
           <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
         </svg>
        <span className="text-gray-600 ml-3">Processing query...</span>
      </div>
    );
  }

  if (queryError) {
    return <StatusMessage message={queryError} type="error" />;
  }
  
  if (!results) {
    return (
        <div className="text-center py-10 px-4 bg-gray-50 rounded-lg">
            <h3 className="text-lg font-medium text-gray-700">Your results will appear here</h3>
            <p className="text-sm text-gray-500 mt-1">Connect to a database, upload documents, and ask a question to begin.</p>
        </div>
    );
  }

  // Helper to safely render cell values, showing 'N/A' for null or undefined.
  const renderCell = (value) => {
    if (value === null || typeof value === 'undefined') {
      return <span className="text-gray-400 italic">N/A</span>;
    }
    return String(value);
  };

  const { sql_result, document_result, query_type, _cache_hit } = results;

  return (
    <div className="space-y-8">
      <div className="flex justify-between items-center bg-gray-100 p-3 rounded-md">
          <span className="font-mono text-sm text-gray-700">Query Type: <span className="font-semibold text-indigo-600">{query_type || 'N/A'}</span></span>
          {typeof _cache_hit !== 'undefined' && (
            <span className={`text-sm font-semibold px-2 py-1 rounded-full ${ _cache_hit ? 'bg-green-200 text-green-800' : 'bg-blue-200 text-blue-800'}`}>
                {_cache_hit ? 'CACHE HIT' : 'CACHE MISS'}
            </span>
          )}
      </div>

      {sql_result && sql_result.rows && (
        <div>
          <h3 className="text-xl font-semibold mb-3 text-gray-800">Database Results</h3>
          {sql_result.rows.length > 0 ? (
            <div className="overflow-x-auto rounded-lg border">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    {Object.keys(sql_result.rows[0]).map(key => (
                      <th key={key} className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">{key}</th>
                    ))}
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {sql_result.rows.map((row, i) => (
                    <tr key={i}>
                      {Object.values(row).map((val, j) => (
                        <td key={j} className="px-6 py-4 whitespace-nowrap text-sm text-gray-700">{renderCell(val)}</td>
                      ))}
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          ) : <p className="text-gray-500">No matching records found in the database.</p>}
        </div>
      )}

      {document_result && document_result.results && (
        <div>
          <h3 className="text-xl font-semibold mb-3 text-gray-800">Document Results</h3>
          {document_result.results.length > 0 ? (
            <div className="space-y-4">
              {document_result.results.map((doc) => (
                <div key={doc.doc_id} className="bg-white p-4 rounded-lg shadow border border-gray-200">
                  <div className="flex justify-between items-center mb-2">
                    <p className="font-semibold text-indigo-700">{doc.filename}</p>
                    <span className="text-xs font-mono bg-gray-200 text-gray-700 px-2 py-1 rounded">Score: {doc.distance.toFixed(4)}</span>
                  </div>
                  <p className="text-sm text-gray-600 bg-gray-50 p-3 rounded-md whitespace-pre-wrap">{doc.chunk}</p>
                </div>
              ))}
            </div>
          ) : <p className="text-gray-500">No relevant documents found.</p>}
        </div>
      )}
    </div>
  );
};

export default ResultsView;
