import React, { useState } from 'react';
import DatabaseConnector from './components/DatabaseConnector';
import DocumentUploader from './components/DocumentUploader';
import QueryPanel from './components/QueryPanel';
import ResultsView from './components/ResultsView';
import StatusMessage from './components/common/statusMessage';


function App() {
  const [dbStatus, setDbStatus] = useState({ message: '', type: null });
  const [uploadStatus, setUploadStatus] = useState({ message: '', type: null });
    const [schema, setSchema] = useState(null); // <-- ADD THIS LINE

  const [results, setResults] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [queryError, setQueryError] = useState(null);

  return (
    <div className="bg-gray-50 min-h-screen font-sans">
      <header className="bg-white shadow-sm">
        <div className="container mx-auto px-4 py-4">
          <h1 className="text-2xl font-bold text-gray-800">AI-Powered NLP Query Engine</h1>
        </div>
      </header>
      
      <main className="container mx-auto p-4 md:p-8">
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
          {/* Left Column for Ingestion */}
          <div className="lg:col-span-4 space-y-6">
              <DatabaseConnector setSchema={setSchema} setDbStatus={setDbStatus} />
              {dbStatus.message && <StatusMessage message={dbStatus.message} type={dbStatus.type} />}
              
              <DocumentUploader setUploadStatus={setUploadStatus} />
              {uploadStatus.message && <StatusMessage message={uploadStatus.message} type={uploadStatus.type} />}
          </div>

          {/* Right Column for Querying */}
          <div className="lg:col-span-8 bg-white p-6 rounded-lg shadow-md">
            <h2 className="text-xl font-semibold mb-4 text-gray-800">3. Query Your Data</h2>
            <QueryPanel 
              setResults={setResults} 
              setIsLoading={setIsLoading}
              setQueryError={setQueryError}
            />
            <div className="mt-6 border-t border-gray-200 pt-6">
              <ResultsView 
                results={results} 
                isLoading={isLoading} 
                queryError={queryError} 
              />
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}

export default App;

