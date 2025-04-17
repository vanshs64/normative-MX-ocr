// page.js
'use client';
import { useState } from 'react';

import './styles.css';
import axios from 'axios';


export default function Home() {

  const [file, setFile] = useState(null);
  const [status, setStatus] = useState("idle");
  const [extractionResult, setExtractionResult] = useState("");

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
    const route = "http://127.0.0.1:3000/gptocr"; // have to be VERY CAREFUL where this is routed to (relative /route won't work)

    try {
      // axios to do http requests (instead of fetch from usual usage)
      const response = await axios.post(route, formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });

      // Process the response from the backend
      const extractedText = response.data.text;
      console.log('Extracted Text:', extractedText);

      setExtractionResult(extractedText)
      setStatus("success");
    } catch {
      setStatus("error");
    }
  };


  return (
    <div className="upload-page">
      <div className="upload-container">
        <h1>Document OCR Upload</h1>
        <p className="reg-text">Please select a PDF or image file to extract text using our OCR engine. Supported formats: PDF, JPG, PNG.</p>

        <div className="file-input-section">
          <input type="file" onChange={handleFileChange} />
        </div>

        {file && (
          <div className="file-info">
            <p><strong>File Name:</strong> {file.name}</p>
            <p><strong>Size:</strong> {(file.size / 1024).toFixed(2)} KB</p>
            <p><strong>Type:</strong> {file.type}</p>
          </div>
        )}

        <button
          className="upload-button"
          onClick={handleFileUpload}
          disabled={!file || status === 'uploading'}
        >
          Upload
        </button>

        {status === 'uploading' && (
          <p className="reg-text">Loading...</p>
        )

        }

        {status === 'success' && (
          <p className="upload-success">File uploaded successfully!</p>
        )}

        {status === 'error' && (
          <p className="upload-error">Upload failed. Please try again.</p>
        )}
      </div>

        {extractionResult && (() => {
          try {
            const jsonResult = JSON.parse(extractionResult);
            return (
              <div className="extraction-result">
                <h2>Extraction Result</h2>
                <table>
                  <thead>
                    <tr>
                      <th>Key</th>
                      <th>Value</th>
                    </tr>
                  </thead>
                  <tbody>
                    {Object.entries(jsonResult).map(([key, value]) => (
                      <tr key={key}>
                        <td>{key}</td>
                        <td>{value}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            );
          } catch (e) {
            return <p className="error-text">Invalid JSON data in extraction result.</p>;
          }
        })()}

    </div>
  );
}