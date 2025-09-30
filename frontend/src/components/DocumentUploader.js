import React, { useState, useCallback } from 'react';
import { useDropzone } from 'react-dropzone';
import apiClient from '../apiClient';
import Spinner from './common/spinner';

const DocumentUploader = ({ setUploadStatus }) => {
  const [isLoading, setIsLoading] = useState(false);

  const onDrop = useCallback(async (acceptedFiles) => {
    if (acceptedFiles.length === 0) return;
    
    setIsLoading(true);
    setUploadStatus({ message: `Uploading ${acceptedFiles.length} file(s)...`, type: null });

    const formData = new FormData();
    acceptedFiles.forEach(file => {
      formData.append('files', file);
    });

    try {
      const response = await apiClient.post('/api/upload-documents', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });
      const { total_documents_processed, total_chunks_indexed } = response.data;
      setUploadStatus({ message: `Success! Processed ${total_documents_processed} file(s) and indexed ${total_chunks_indexed} chunks.`, type: 'success' });
    } catch (error) {
      const errorMessage = error.response?.data?.detail || 'File upload failed.';
      setUploadStatus({ message: errorMessage, type: 'error' });
    } finally {
      setIsLoading(false);
    }
  }, [setUploadStatus]);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({ onDrop, accept: {'application/pdf': ['.pdf'], 'text/plain': ['.txt'], 'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx']} });

  return (
    <div className="bg-white p-6 rounded-lg shadow-md">
      <h2 className="text-xl font-semibold mb-4 text-gray-800">2. Upload Documents</h2>
      <div
        {...getRootProps()}
        className={`border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-colors ${
          isDragActive ? 'border-indigo-500 bg-indigo-50' : 'border-gray-300 hover:border-indigo-400'
        }`}
      >
        <input {...getInputProps()} />
        {isLoading ? (
          <div className="flex justify-center items-center text-gray-600">
             <svg className="animate-spin h-5 w-5 mr-3 text-indigo-500" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
            Processing...
          </div>
        ) : isDragActive ? (
          <p className="text-indigo-600">Drop the files here ...</p>
        ) : (
          <p className="text-gray-500">Drag 'n' drop files here, or click to select (PDF, DOCX, TXT)</p>
        )}
      </div>
    </div>
  );
};

export default DocumentUploader;
