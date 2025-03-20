'use client';
import { useState, useRef } from 'react';
import DocumentUploader from './components/document-uploader';

export default function Home() {
  const [isDragging, setIsDragging] = useState(false);
  const fileInputRef = useRef(null);

  const handleDrag = (e) => {
    e.preventDefault();
    e.stopPropagation();
  };

  const handleDragIn = (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.dataTransfer.items && e.dataTransfer.items.length > 0) {
      setIsDragging(true);
    }
  };

  const handleDragOut = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);

    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      fileInputRef.current?.handleFiles(e.dataTransfer.files);
      e.dataTransfer.clearData();
    }
  };

  return (
    <div
      className="min-h-screen relative"
      onDragEnter={handleDragIn}
      onDragLeave={handleDragOut}
      onDragOver={handleDrag}
      onDrop={handleDrop}
    >
      {isDragging && (
        <div className="absolute inset-0 bg-blue-500/10 border-2 border-dashed border-blue-500 rounded-lg z-50 flex items-center justify-center">
          <div className="bg-white p-8 rounded-lg shadow-lg">
            <p className="text-xl text-blue-500 font-semibold">Drop files here</p>
          </div>
        </div>
      )}
      
      <main className="p-8">
        <h1 className="text-3xl font-bold mb-8">Mortgage Document Portal with OCR</h1>
        
        <div className="max-w-2xl mx-auto bg-white p-6 rounded-lg shadow-md">
          <DocumentUploader ref={fileInputRef} />
        </div>
      </main>
    </div>
  );
}
