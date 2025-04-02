// document-uploader.js
'use client';
import { useState, useRef } from "react";
import { File, CheckCircle, AlertCircle, X, UploadCloud } from "lucide-react";

export default function DocumentUploader({ onFilesUpdate }) {
  const [files, setFiles] = useState([]);
  const [isDragging, setIsDragging] = useState(false);
  const fileInputRef = useRef(null);

  const handleDrag = (e) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragEnd = (e) => {
    e.preventDefault();
    setIsDragging(false);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setIsDragging(false);
    processFiles(e.dataTransfer.files);
  };

  const handleFileInput = (e) => {
    processFiles(e.target.files);
    e.target.value = null; // Reset input
  };

  const processFiles = (fileList) => {
    const allowedTypes = ["application/pdf", "image/png", "image/jpeg"];
    const newFiles = Array.from(fileList).map(file => ({
      id: crypto.randomUUID(),
      file,
      name: file.name,
      size: file.size,
      type: file.type,
      status: 'uploading',
      progress: 0,
      error: null
    }));

    // Simulate upload progress
    newFiles.forEach((fileObj, index) => {
      if (!allowedTypes.includes(fileObj.type)) {
        updateFileStatus(fileObj.id, 'error', 'Invalid file type');
        return;
      }

      const interval = setInterval(() => {
        setFiles(prev => prev.map(f => {
          if (f.id === fileObj.id && f.progress < 90) {
            return { ...f, progress: f.progress + 10 };
          }
          return f;
        }));
      }, 200);

      // Simulate successful upload after 2 seconds
      setTimeout(() => {
        clearInterval(interval);
        updateFileStatus(fileObj.id, 'success');
      }, 2000);
    });

    setFiles(prev => [...prev, ...newFiles]);
    onFilesUpdate?.(prev => [...prev, ...newFiles]);
  };

  const updateFileStatus = (id, status, error = null) => {
    setFiles(prev => prev.map(file => 
      file.id === id ? { ...file, status, error } : file
    ));
  };

  const removeFile = (id) => {
    setFiles(prev => prev.filter(file => file.id !== id));
    onFilesUpdate?.(prev => prev.filter(file => file.id !== id));
  };

  const formatSize = (bytes) => {
    const sizes = ['B', 'KB', 'MB'];
    if (bytes === 0) return '0 B';
    const i = Math.floor(Math.log(bytes) / Math.log(1024));
    return `${(bytes / Math.pow(1024, i)).toFixed(1)} ${sizes[i]}`;
  };

  return (
    <div className="border-2 border-dashed rounded-lg p-8 transition-colors
      ${isDragging ? 'border-primary bg-primary/10' : 'border-card-border'}">
      
      <div
        className="cursor-pointer text-center"
        onClick={() => fileInputRef.current?.click()}
        onDragOver={handleDrag}
        onDragLeave={handleDragEnd}
        onDrop={handleDrop}
      >
        <UploadCloud className="mx-auto h-12 w-12 text-muted mb-4" />
        <p className="font-medium">Drag & drop files or click to browse</p>
        <p className="text-sm text-muted mt-2">PDF, JPG, PNG (Max 10MB each)</p>
      </div>

      <input
        type="file"
        ref={fileInputRef}
        onChange={handleFileInput}
        className="hidden"
        multiple
      />

      <div className="mt-6 space-y-3">
        {files.map(file => (
          <div key={file.id} className="flex items-center justify-between p-3 bg-input-bg rounded-lg">
            <div className="flex items-center gap-3">
              <File className="h-5 w-5 text-blue-500" />
              <div>
                <p className="font-medium">{file.name}</p>
                <p className="text-xs text-muted">{formatSize(file.size)}</p>
              </div>
            </div>
            
            <div className="flex items-center gap-3">
              {file.status === 'success' ? (
                <CheckCircle className="h-5 w-5 text-green-500" />
              ) : file.status === 'error' ? (
                <div className="text-red-500 flex items-center gap-1">
                  <AlertCircle className="h-5 w-5" />
                  <span className="text-sm">{file.error}</span>
                </div>
              ) : (
                <div className="w-20 h-2 bg-gray-200 rounded-full overflow-hidden">
                  <div 
                    className="h-full bg-primary rounded-full transition-all"
                    style={{ width: `${file.progress}%` }}
                  />
                </div>
              )}
              <button 
                onClick={() => removeFile(file.id)}
                className="text-muted hover:text-foreground"
              >
                <X className="h-5 w-5" />
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}