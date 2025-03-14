"use client";

import { useState, useRef } from "react";
import { Upload, File, CheckCircle, AlertCircle, X } from "lucide-react";
import { Button } from "./ui/button";
import { uploadFiles } from "./lib/actions";
import { Progress } from "./ui/progress";

export default function DocumentUploader() {
  const [files, setFiles] = useState([]);
  const [isDragging, setIsDragging] = useState(false);
  const fileInputRef = useRef(null);

  const handleDragOver = (e) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = (e) => {
    e.preventDefault();
    setIsDragging(false);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setIsDragging(false);

    if (e.dataTransfer.files) {
      handleFiles(e.dataTransfer.files);
    }
  };

  const handleFileInputChange = (e) => {
    if (e.target.files) {
      handleFiles(e.target.files);
    }
  };

  const handleFiles = async (fileList) => {
    const allowedTypes = ["application/pdf", "image/png", "image/jpeg"];
    const newFiles = [];

    for (let i = 0; i < fileList.length; i++) {
      const file = fileList[i];

      if (!allowedTypes.includes(file.type)) {
        newFiles.push({
          id: crypto.randomUUID(),
          name: file.name,
          size: file.size,
          type: file.type,
          status: "error",
          progress: 0,
          error: "Invalid file type. Only PDF, PNG, and JPG are allowed.",
        });
        continue;
      }

      newFiles.push({
        id: crypto.randomUUID(),
        name: file.name,
        size: file.size,
        type: file.type,
        status: "uploading",
        progress: 0,
      });
    }

    setFiles((prev) => [...prev, ...newFiles]);

    // Process each file
    for (let i = 0; i < fileList.length; i++) {
      const file = fileList[i];
      const fileId = newFiles[i].id;

      if (newFiles[i].status === "error") continue;

      try {
        // Simulate progress updates
        const progressInterval = setInterval(() => {
          setFiles((prev) =>
            prev.map((f) => (f.id === fileId && f.progress < 90 ? { ...f, progress: f.progress + 10 } : f)),
          );
        }, 200);

        // Upload the file
        const result = await uploadFiles([file]);

        clearInterval(progressInterval);

        setFiles((prev) => prev.map((f) => (f.id === fileId ? { ...f, status: "success", progress: 100 } : f)));
      } catch (error) {
        setFiles((prev) =>
          prev.map((f) =>
            f.id === fileId
              ? {
                  ...f,
                  status: "error",
                  progress: 0,
                  error: "Failed to upload file. Please try again.",
                }
              : f,
          ),
        );
      }
    }
  };

  const removeFile = (id) => {
    setFiles((prev) => prev.filter((file) => file.id !== id));
  };

  const formatFileSize = (bytes) => {
    if (bytes < 1024) return bytes + " bytes";
    else if (bytes < 1048576) return (bytes / 1024).toFixed(1) + " KB";
    else return (bytes / 1048576).toFixed(1) + " MB";
  };

  const getFileIcon = (fileType) => {
    if (fileType === "application/pdf") {
      return <File className="h-5 w-5 text-red-500" />;
    } else if (fileType.startsWith("image/")) {
      return <File className="h-5 w-5 text-blue-500" />;
    } else {
      return <File className="h-5 w-5 text-gray-500" />;
    }
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case "success":
        return <CheckCircle className="h-5 w-5 text-green-500" />;
      case "error":
        return <AlertCircle className="h-5 w-5 text-red-500" />;
      case "uploading":
        return null;
      default:
        return null;
    }
  };

  return (
    <div className="space-y-4">
      <div
        className={`border-2 border-dashed rounded-lg p-8 text-center ${
          isDragging ? "border-blue-500 bg-blue-50" : "border-slate-300 hover:border-blue-400 hover:bg-slate-50"
        } transition-colors duration-150 ease-in-out`}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
      >
        <div className="flex flex-col items-center justify-center space-y-3">
          <div className="p-3 bg-blue-50 rounded-full">
            <Upload className="h-8 w-8 text-blue-500" />
          </div>
          <h3 className="text-lg font-medium text-slate-800">Drag and drop your files here</h3>
          <p className="text-sm text-slate-500 max-w-md">
            Upload your documents in PDF, PNG, or JPG format. Files will be securely stored for your mortgage
            application.
          </p>
          <div className="pt-2">
            <Button onClick={() => fileInputRef.current?.click()} variant="outline" className="mt-2">
              Browse Files
            </Button>
            <input
              type="file"
              ref={fileInputRef}
              onChange={handleFileInputChange}
              className="hidden"
              multiple
              accept=".pdf,.png,.jpg,.jpeg"
            />
          </div>
        </div>
      </div>

      {files.length > 0 && (
        <div className="mt-6 space-y-3">
          <h3 className="font-medium text-slate-800">Uploaded Documents</h3>
          <div className="space-y-3">
            {files.map((file) => (
              <div key={file.id} className="flex items-center justify-between p-3 bg-white border rounded-lg">
                <div className="flex items-center space-x-3">
                  {getFileIcon(file.type)}
                  <div>
                    <p className="text-sm font-medium text-slate-800 truncate max-w-[200px] sm:max-w-xs">{file.name}</p>
                    <p className="text-xs text-slate-500">{formatFileSize(file.size)}</p>
                    {file.error && <p className="text-xs text-red-500 mt-1">{file.error}</p>}
                  </div>
                </div>
                <div className="flex items-center space-x-3">
                  {file.status === "uploading" ? (
                    <div className="w-24">
                      <Progress value={file.progress} className="h-2" />
                    </div>
                  ) : (
                    getStatusIcon(file.status)
                  )}
                  <button onClick={() => removeFile(file.id)} className="p-1 hover:bg-slate-100 rounded-full">
                    <X className="h-4 w-4 text-slate-500" />
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}