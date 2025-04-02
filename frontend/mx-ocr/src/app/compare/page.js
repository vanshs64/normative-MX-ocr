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
  const [overallCer, setOverallCer] = useState([]);

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

        if (response.ok) {
          // note that data is a dict with 2 keys, result for the table data and cer (overall cer)
          const data = await response.json();
          console.log(data.table_data)
          setTableData(data["table_data"]);
          setOverallCer(data["overall_cer"]);
        } else {
          console.error("Failed to fetch specific file data");
        }
      } catch (error) {
        console.error("Error fetching specific file data:", error);
      }
    };

    fetchSpecificFile();
  }, [selectedFile]);


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
        
        <p>Overall Character Error Rate: {(overallCer)}</p>
        {/* Table to display the comparison data */}
        <table className="table-auto border-collapse border border-gray-300 w-full">
          <thead>
            <tr>
              <th className="border border-gray-300 px-4 py-2">Key</th>
              <th className="border border-gray-300 px-4 py-2">Hypothesis</th>
              <th className="border border-gray-300 px-4 py-2">Reference</th>
              <th className="border border-gray-300 px-4 py-2">CER</th>
            </tr>
          </thead>
          <tbody>
            {tableData.map((row, index) => (
              <tr key={index}>
                <td className="border border-gray-300 px-4 py-2 font-medium">{row[0]}</td>
                <td className="border border-gray-300 px-4 py-2">
                  {typeof row[1] === 'object' 
                    ? JSON.stringify(row[1]) 
                    : row[1] || 'N/A'}
                </td>
                <td className="border border-gray-300 px-4 py-2">
                  {typeof row[2] === 'object' 
                    ? JSON.stringify(row[2]) 
                    : row[2] || 'N/A'}
                </td>
                <td className="border border-gray-300 px-4 py-2">
                  {row[3].toFixed(4)}
                </td>
              </tr>
            ))}
          </tbody>
        </table>

      </div>
    </div>
  );
};

export default Compare;