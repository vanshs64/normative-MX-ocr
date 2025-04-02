"use client";

import { useState, useEffect } from "react";
import React from 'react';

const Compare = () => {
  
  // const pathHypothesis = "../../test_docs/hypotheses/";
  // const pathReference = "../../test_docs/reference/";
  
  // list of files that have both a reference and a hypothesis existing
  const [scannedFiles, setScannedFiles] = useState([]);
  
  const [selectedFile, setSelectedFile] = useState(scannedFiles[0] || "");
  const [tableData, setTableData] = useState([]);

  useEffect(() => {
    const fetchScannedFiles = async () => {
      try {
        console.log("Trying to fetch comparing files");
        const response = await fetch("http://127.0.0.1:3000/get_scanned_files");
        if (response.ok) {
          const data = await response.json();
          setScannedFiles(data);
        } else {
          console.error("Failed to fetch scanned files");
        }
      } catch (error) {
        console.error("Error fetching scanned files:", error);
      }
    };

    fetchScannedFiles();
  }, []);

  useEffect(() => {
    const fetchSpecificFile = async () => {
      if (!selectedFile) return;

      try {
        const response = await fetch("http://127.0.0.1:3000/get_hyp_ref", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ file_name: selectedFile }),
        });
    
        if (!response.ok) {
          const error = await response.text();
          console.error('Server error:', error);
          return;
        }
    
        const data = await response.json();
        if (data.error) {
          console.error('Backend error:', data.error);
        } else {
          setTableData(data);
        }
      } catch (error) {
        console.error("Error fetching specific file data:", error);
      }
    };
    
    // if the person selected a file thru the dropdown, fetch the comparison data for that name
    if (selectedFile) {
      fetchSpecificFile();
    }
  }, [selectedFile]);
    
  // Transform the data into comparable rows
  const transformData = (data) => {
    const hypContent = data.hyp_content;
    const refContent = data.ref_content;
  
    // Get all unique keys from both objects
    const allKeys = new Set([
      ...Object.keys(hypContent),
      ...Object.keys(refContent)
    ]);
  
    return Array.from(allKeys).map(key => ({
      key,
      hypothesis: hypContent[key] !== undefined ? hypContent[key] : "N/A",
      reference: refContent[key] !== undefined ? refContent[key] : "N/A"
    }));
  };
  
  useEffect(() => {
    if (tableData && Object.keys(tableData).length > 0) {
      const transformed = transformData(tableData);
      setTableData(transformed);
    }
  }, [tableData]);

  return (
    <div className="min-h-screen bg-background text-foreground p-8">
      <div className="max-w-4xl mx-auto">
        <h1 className="text-3xl font-bold mb-8">Compare OCR Results</h1>
        <p className="mb-4">This page will allow you to compare the results of different OCR engines.</p>
        
        {/* Dropdown for selecting a file */}
        <div className="mb-4">
          <label htmlFor="file-select" className="block text-lg font-medium mb-2">Select a file:</label>
          <select
            id="file-select"
            className="border border-gray-300 rounded px-4 py-2 w-full"
            value={selectedFile}
            onChange={(e) => setSelectedFile(e.target.value)}
          >
            {scannedFiles.map(file => (
              <option key={file} value={file}>{file}</option>
            ))}
          </select>
        </div>

        {/* Table to display the comparison data */}
        <table className="table-auto border-collapse border border-gray-300 w-full">
          <thead>
            <tr>
              <th className="border border-gray-300 px-4 py-2">Key</th>
              <th className="border border-gray-300 px-4 py-2">Hypothesis</th>
              <th className="border border-gray-300 px-4 py-2">Reference</th>
            </tr>
          </thead>
          <tbody>
            {tableData.map((row, index) => (
              <tr key={index}>
                <td className="border border-gray-300 px-4 py-2">{row.key}</td>
                <td className="border border-gray-300 px-4 py-2">{row.hypothesis}</td>
                <td className="border border-gray-300 px-4 py-2">{row.reference}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default Compare;