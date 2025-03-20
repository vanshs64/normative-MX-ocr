"use client";

import { useState, useRef } from "react";
import { Upload, File, CheckCircle, AlertCircle, X } from "lucide-react";
import { Button } from "./ui/button";
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
        const formData = new FormData();
        formData.append('file', file);

        const response = await fetch('http://localhost:8080/save-file', {
          method: 'POST',
          body: formData,
        });

        const result = await response.json();

        clearInterval(progressInterval);

        if (response.ok) {
          setFiles((prev) => prev.map((f) => (f.id === fileId ? { ...f, status: "success", progress: 100 } : f)));
        } else {
          setFiles((prev) =>
            prev.map((f) =>
              f.id === fileId
                ? {
                    ...f,
                    status: "error",
                    progress: 0,
                    error: result.error || "Failed to upload file. Please try again.",
                  }
                : f,
            ),
          );
        }
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
      default:
        return <Upload className="h-5 w-5 text-gray-500" />;
    }
  };

  return (
    <div>
      <input
        type="file"
        ref={fileInputRef}
        onChange={handleFileInputChange}
        style={{ display: "none" }}
      />
      <div
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
        className={`border-2 border-dashed p-4 ${isDragging ? "border-blue-500" : "border-gray-300"}`}
      >
        <p>Drag and drop files here, or click to select files</p>
        <Button onClick={() => fileInputRef.current.click()}>Select Files</Button>
      </div>
      <div>
        {files.map((file) => (
          <div key={file.id} className="flex items-center justify-between p-2 border-b">
            <div className="flex items-center">
              {getFileIcon(file.type)}
              <div className="ml-2">
                <p className="text-sm font-medium">{file.name}</p>
                <p className="text-xs text-gray-500">{formatFileSize(file.size)}</p>
              </div>
            </div>
            <div className="flex items-center">
              {getStatusIcon(file.status)}
              {file.status === "uploading" && <Progress value={file.progress} />}
              {file.status === "error" && <p className="text-xs text-red-500 ml-2">{file.error}</p>}
              <Button onClick={() => removeFile(file.id)} className="ml-2">
                <X className="h-4 w-4" />
              </Button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}