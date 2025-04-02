// page.js
'use client';
import { useState, useRef } from 'react';
import DocumentUploader from './components/document-uploader';

export default function Home() {
  const [files, setFiles] = useState([]);
  const [selectedOcr, setSelectedOcr] = useState('');
  const [ocrResults, setOcrResults] = useState(null);
  const [isProcessing, setIsProcessing] = useState(false);

  const ocrOptions = [
    { value: 'gpt', label: 'Openai ChatGPT 4o' },
    { value: 'claude', label: 'Claude Sonnet 3.0' },
    { value: 'vision', label: 'Google Vision OCR' },
    { value: 'docai', label: 'Google Document AI' },
  ];

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
            <select
              value={selectedOcr}
              onChange={(e) => setSelectedOcr(e.target.value)}
              className="bg-input-bg border border-card-border rounded-lg px-4 py-2 flex-1"
            >
              <option value="">Select OCR Type</option>
              {ocrOptions.map(option => (
                <option key={option.value} value={option.value}>
                  {option.label}
                </option>
              ))}
            </select>
            
            <button
              onClick={handleRunOcr}
              disabled={!selectedOcr || files.length === 0 || isProcessing}
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
            <div className={`p-4 rounded-lg ${
              ocrResults.success ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
            }`}>
              {ocrResults.message}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}