// page.js
'use client';
import { useState } from 'react';

import DocumentUploader from './components/document-uploader';
import axios from 'axios';


export default function Home() {

  const [file, setFile] = useState(null);
  const [status, setStatus] = useState("idle");
  const [uploadProgress, setUploadProgress] = useState(0);

  // when person selects a file to upload
  function handleFileChange(e) {
    if (e.target.files) {
      setFile(e.target.files[0]);
    }
  }

  async function handleFileUpload() {
    if (!file) return;

    setStatus("uploading");

    // This is the format of the data we want to send, in a FormData object
    const formData = new FormData();
    formData.append('file', file);

    // which flask route to choose for ocr
    const route = "/gptocr"

    try {
      // axios to do http requests (instead of fetch from usual usage)
      await axios.post(route, formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });
      

      setStatus("success");
    } catch {
      setStatus("error");
    }
  }


  const [files, setFiles] = useState([]);
  const [ocrResults, setOcrResults] = useState(null);
  const [isProcessing, setIsProcessing] = useState(false);

  const handleRunOcr = async () => {
    if (!selectedOcr) return;

    setIsProcessing(true);
    try {
      const route = `/${selectedOcr}`;
      const response = await fetch(route, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ files }),
      });

      if (!response.ok) {
        throw new Error('Failed to process OCR');
      }

      const data = await response.json();
      setOcrResults({
        success: true,
        message: data.message || 'OCR processed successfully!',
      });
    } catch (error) {
      setOcrResults({
        success: false,
        message: error.message || 'OCR processing failed',
      });
    } finally {
      setIsProcessing(false);
    }
  };

  return (
    <div className="space-y-2">
      <input type="file" onChange={handleFileChange} />

      {file && (
        <div className="mb-4 text-sm">
          <p>File name: {file.name}</p>
          <p>Size: {(file.size / 1024).toFixed(2)} KB</p>
          <p>Type: {file.type}</p>
        </div>
      )}

      {file && status !== 'uploading' && (
        <button onClick={handleFileUpload}>Upload</button>
      )}

      {status === 'success' && (
        <p className="text-sm text-green-600">File uploaded successfully!</p>
      )}

      {status === 'error' && (
        <p className="text-sm text-red-600">Upload failed. Please try again.</p>
      )}



      <div className="min-h-screen bg-background text-foreground p-8">
        <div className="max-w-4xl mx-auto">
          <h1 className="text-3xl font-bold mb-8">Mortgage Document Portal</h1>

          {/* Upload Section */}
          <div className="mb-8">
            <h2 className="text-xl font-semibold mb-4">Upload Documents</h2>
            <DocumentUploader onFilesUpdate={setFiles} />
          </div>

          {/* OCR Selection */}
          <div className="mb-8">
            <h2 className="text-xl font-semibold mb-4">Process Documents</h2>
            <div className="flex gap-4 items-center">
              <button
                onClick={handleRunOcr}
                disabled={files.length === 0 || isProcessing}
                className="bg-primary text-white px-6 py-2 rounded-lg font-medium disabled:opacity-50"
              >
                {isProcessing ? 'Processing...' : 'Run OCR'}
              </button>
            </div>
          </div>

          {/* Results Display */}
          {ocrResults && (
            <div>
              <h2 className="text-xl font-semibold mb-4">Results</h2>
              <div
                className={`p-4 rounded-lg ${
                  ocrResults.success
                    ? 'bg-green-100 text-green-800'
                    : 'bg-red-100 text-red-800'
                }`}
              >
                {ocrResults.message}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}