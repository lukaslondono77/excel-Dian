import React, { useState } from 'react';
import { useDropzone } from 'react-dropzone';
import axios from 'axios';
import toast, { Toaster } from 'react-hot-toast';
import { Upload, FileText, Download, Eye, Loader2, Calendar, BarChart3, FileSpreadsheet } from 'lucide-react';
import { getDianServiceUrl, getGatewayServiceUrl } from './config';
import './App.css';

function App() {
  const [parsedData, setParsedData] = useState(null);
  const [isUploading, setIsUploading] = useState(false);
  const [isGenerating, setIsGenerating] = useState(false);
  const [pdfUrl, setPdfUrl] = useState(null);
  const [showPreview, setShowPreview] = useState(false);

  // DIAN Processing states
  const [dianFiles, setDianFiles] = useState([]);
  const [isDianProcessing, setIsDianProcessing] = useState(false);
  const [dianResults, setDianResults] = useState(null);
  const [startDate, setStartDate] = useState('2023-01-01');
  const [endDate, setEndDate] = useState('2023-12-31');
  const [selectedFormato, setSelectedFormato] = useState('1001');
  const [exportFormat, setExportFormat] = useState('excel');
  const [activeTab, setActiveTab] = useState('dian'); // 'dian' or 'excel'
  const [consolidationOptions, setConsolidationOptions] = useState({
    monthly: true,
    account: true,
    nit: true,
    documentType: true
  });

  // Mock JWT token for development (replace with real auth)
  const getAuthToken = () => {
    // In production, this would come from your auth provider
    return "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ1c2VyXzEyMyIsIm5hbWUiOiJKb2huIERvZSIsImlhdCI6MTUxNjIzOTAyMn0.30I60qO4HuyGnuV7rKz11mM427u6UMvceAHw2ayVXi0";
  };

  // DIAN Processing dropzone
  const onDianDrop = async (acceptedFiles) => {
    if (acceptedFiles.length === 0) return;

    // Validate file types
    const validFiles = acceptedFiles.filter(file => 
      file.name.match(/\.(xlsx|xls|csv)$/)
    );

    if (validFiles.length === 0) {
      toast.error('Please upload Excel (.xlsx, .xls) or CSV files');
      return;
    }

    setDianFiles(validFiles);
    toast.success(`Added ${validFiles.length} file(s) for DIAN processing`);
  };

  // Process DIAN files
  const processDianFiles = async () => {
    if (dianFiles.length === 0) {
      toast.error('Please upload files first');
      return;
    }

    setIsDianProcessing(true);
    setDianResults(null);

    const formData = new FormData();
    formData.append('start_date', startDate);
    formData.append('end_date', endDate);
    formData.append('formato', selectedFormato);
    formData.append('export_format', exportFormat);

    // Add all files
    dianFiles.forEach((file, index) => {
      formData.append('file', file);
    });

    try {
      const response = await axios.post(getDianServiceUrl('/process_dian_files'), formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });

      setDianResults(response.data);
      toast.success(`Successfully processed ${dianFiles.length} files!`);
    } catch (error) {
      console.error('DIAN processing error:', error);
      toast.error(error.response?.data?.detail || 'Error processing files');
    } finally {
      setIsDianProcessing(false);
    }
  };

  // Download DIAN report
  const downloadDianReport = async () => {
    if (!dianResults?.download_url) return;

    try {
      const response = await axios.get(getDianServiceUrl(dianResults.download_url), {
        responseType: 'blob',
      });

      const blob = new Blob([response.data], { type: 'application/octet-stream' });
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = dianResults.report_filename || 'dian_report.xlsx';
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);
      toast.success('Report downloaded successfully!');
    } catch (error) {
      console.error('Download error:', error);
      toast.error('Error downloading report');
    }
  };

  const onDrop = async (acceptedFiles) => {
    if (acceptedFiles.length === 0) return;

    const file = acceptedFiles[0];
    
    // Validate file type
    if (!file.name.match(/\.(xlsx|xls)$/)) {
      toast.error('Please upload an Excel file (.xlsx or .xls)');
      return;
    }

    setIsUploading(true);
    setParsedData(null);
    setPdfUrl(null);

    const formData = new FormData();
    formData.append('file', file);

    try {
      console.log('Uploading file:', file.name, 'Size:', file.size);
      
      // Call the gateway service instead of individual services
      const response = await axios.post(getGatewayServiceUrl('/process_excel_to_pdf'), formData, {
        headers: {
          'Authorization': `Bearer ${getAuthToken()}`,
          'Content-Type': 'multipart/form-data',
        },
        timeout: 30000, // 30 second timeout
      });

      console.log('Upload successful:', response.data);

      // The gateway returns both parsed data and PDF URL
      setParsedData(response.data.excel_data);
      setPdfUrl(response.data.pdf_url);
      toast.success(`Successfully processed file and generated PDF!`);
    } catch (error) {
      console.error('Upload error details:', {
        message: error.message,
        status: error.response?.status,
        statusText: error.response?.statusText,
        data: error.response?.data,
        config: error.config
      });
      
      let errorMessage = 'Error processing file';
      if (error.response?.data?.detail) {
        errorMessage = error.response.data.detail;
      } else if (error.message) {
        errorMessage = error.message;
      }
      
      toast.error(errorMessage);
    } finally {
      setIsUploading(false);
    }
  };

  const generatePDF = async () => {
    if (!parsedData) return;

    setIsGenerating(true);
    setPdfUrl(null);

    try {
      // Call the gateway service for PDF generation
      const response = await axios.post(getGatewayServiceUrl('/process_excel_to_pdf'), {
        data: parsedData.parsed_data,
        file_id: parsedData.file_id,
        filename: parsedData.filename,
      }, {
        headers: {
          'Authorization': `Bearer ${getAuthToken()}`,
          'Content-Type': 'application/json',
        },
      });

      setPdfUrl(response.data.pdf_url);
      toast.success('PDF generated successfully!');
    } catch (error) {
      console.error('PDF generation error:', error);
      toast.error(error.response?.data?.detail || 'Error generating PDF');
    } finally {
      setIsGenerating(false);
    }
  };

  const handleDownload = async () => {
    if (!pdfUrl) return;
    
    try {
      // If it's a gateway download URL, call it directly
      if (pdfUrl.startsWith('/download_pdf/')) {
        const response = await axios.get(getGatewayServiceUrl(pdfUrl), {
          headers: {
            'Authorization': `Bearer ${getAuthToken()}`,
          },
          responseType: 'blob',
        });
        
        // Create download link
        const blob = new Blob([response.data], { type: 'application/pdf' });
        const url = window.URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = url;
        link.download = 'dian_report.pdf';
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        window.URL.revokeObjectURL(url);
      } else {
        // For external URLs, open in new tab
        window.open(pdfUrl, '_blank');
      }
    } catch (error) {
      console.error('Download error:', error);
      toast.error('Error downloading PDF');
    }
  };

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': ['.xlsx'],
      'application/vnd.ms-excel': ['.xls'],
    },
    multiple: false,
  });

  const { getRootProps: getDianRootProps, getInputProps: getDianInputProps, isDragActive: isDianDragActive } = useDropzone({
    onDrop: onDianDrop,
    accept: {
      'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': ['.xlsx'],
      'application/vnd.ms-excel': ['.xls'],
      'text/csv': ['.csv'],
    },
    multiple: true,
  });

  return (
    <div className="min-h-screen bg-gray-50">
      <Toaster position="top-right" />
      
      {/* Header */}
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-6">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">Excel to DIAN</h1>
              <p className="text-gray-600">Convert Excel files to DIAN-compliant reports</p>
            </div>
            <div className="flex items-center space-x-4">
              <div className="bg-green-100 text-green-800 px-3 py-1 rounded-full text-sm font-medium">
                System Online
              </div>
            </div>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Tab Navigation */}
        <div className="mb-8">
          <div className="border-b border-gray-200">
            <nav className="-mb-px flex space-x-8">
              <button
                onClick={() => setActiveTab('dian')}
                className={`py-2 px-1 border-b-2 font-medium text-sm ${
                  activeTab === 'dian'
                    ? 'border-primary-500 text-primary-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                <BarChart3 className="inline h-4 w-4 mr-2" />
                DIAN Processing
              </button>
              <button
                onClick={() => setActiveTab('excel')}
                className={`py-2 px-1 border-b-2 font-medium text-sm ${
                  activeTab === 'excel'
                    ? 'border-primary-500 text-primary-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                <FileText className="inline h-4 w-4 mr-2" />
                Excel to PDF
              </button>
            </nav>
          </div>
        </div>

        {activeTab === 'dian' ? (
          /* DIAN Processing Interface */
          <div className="space-y-8">
            {/* File Upload Section */}
            <div className="bg-white rounded-lg shadow-sm border p-6">
              <h2 className="text-xl font-semibold text-gray-900 mb-4 flex items-center">
                <FileSpreadsheet className="h-5 w-5 mr-2" />
                Upload Accounting Files
              </h2>
              
              <div
                {...getDianRootProps()}
                className={`border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-colors ${
                  isDianDragActive
                    ? 'border-primary-500 bg-primary-50'
                    : 'border-gray-300 hover:border-primary-400 hover:bg-gray-50'
                }`}
              >
                <input {...getDianInputProps()} />
                <Upload className="mx-auto h-12 w-12 text-gray-400 mb-4" />
                {isDianDragActive ? (
                  <p className="text-primary-600 font-medium">Drop the files here...</p>
                ) : (
                  <div>
                    <p className="text-gray-600 mb-2">
                      Drag & drop Excel or CSV files here, or click to select
                    </p>
                    <p className="text-sm text-gray-500">
                      Supports .xlsx, .xls, and .csv files
                    </p>
                  </div>
                )}
              </div>

              {dianFiles.length > 0 && (
                <div className="mt-4">
                  <h3 className="font-medium text-gray-900 mb-2">Selected Files:</h3>
                  <div className="space-y-2">
                    {dianFiles.map((file, index) => (
                      <div key={index} className="flex items-center justify-between p-2 bg-gray-50 rounded">
                        <span className="text-sm text-gray-700">{file.name}</span>
                        <span className="text-xs text-gray-500">
                          {(file.size / 1024 / 1024).toFixed(2)} MB
                        </span>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>

            {/* Processing Options */}
            <div className="bg-white rounded-lg shadow-sm border p-6">
              <h2 className="text-xl font-semibold text-gray-900 mb-4 flex items-center">
                <Calendar className="h-5 w-5 mr-2" />
                Processing Options
              </h2>
              
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Start Date
                  </label>
                  <input
                    type="date"
                    value={startDate}
                    onChange={(e) => setStartDate(e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
                  />
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    End Date
                  </label>
                  <input
                    type="date"
                    value={endDate}
                    onChange={(e) => setEndDate(e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
                  />
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    DIAN Format
                  </label>
                  <select
                    value={selectedFormato}
                    onChange={(e) => setSelectedFormato(e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
                  >
                    <option value="1001">Formato 1001</option>
                    <option value="1002">Formato 1002</option>
                    <option value="1003">Formato 1003</option>
                  </select>
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Export Format
                  </label>
                  <select
                    value={exportFormat}
                    onChange={(e) => setExportFormat(e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
                  >
                    <option value="excel">Excel</option>
                    <option value="pdf">PDF</option>
                  </select>
                </div>
              </div>

              {/* Consolidation Options */}
              <div className="mb-6">
                <h3 className="text-lg font-medium text-gray-900 mb-3">Consolidation Options</h3>
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                  <label className="flex items-center">
                    <input
                      type="checkbox"
                      checked={consolidationOptions.monthly}
                      onChange={(e) => setConsolidationOptions(prev => ({...prev, monthly: e.target.checked}))}
                      className="rounded border-gray-300 text-primary-600 focus:ring-primary-500"
                    />
                    <span className="ml-2 text-sm text-gray-700">Monthly</span>
                  </label>
                  
                  <label className="flex items-center">
                    <input
                      type="checkbox"
                      checked={consolidationOptions.account}
                      onChange={(e) => setConsolidationOptions(prev => ({...prev, account: e.target.checked}))}
                      className="rounded border-gray-300 text-primary-600 focus:ring-primary-500"
                    />
                    <span className="ml-2 text-sm text-gray-700">By Account</span>
                  </label>
                  
                  <label className="flex items-center">
                    <input
                      type="checkbox"
                      checked={consolidationOptions.nit}
                      onChange={(e) => setConsolidationOptions(prev => ({...prev, nit: e.target.checked}))}
                      className="rounded border-gray-300 text-primary-600 focus:ring-primary-500"
                    />
                    <span className="ml-2 text-sm text-gray-700">By NIT</span>
                  </label>
                  
                  <label className="flex items-center">
                    <input
                      type="checkbox"
                      checked={consolidationOptions.documentType}
                      onChange={(e) => setConsolidationOptions(prev => ({...prev, documentType: e.target.checked}))}
                      className="rounded border-gray-300 text-primary-600 focus:ring-primary-500"
                    />
                    <span className="ml-2 text-sm text-gray-700">By Document Type</span>
                  </label>
                </div>
              </div>

              <div className="mt-6">
                <button
                  onClick={processDianFiles}
                  disabled={dianFiles.length === 0 || isDianProcessing}
                  className="w-full bg-primary-600 text-white py-3 px-4 rounded-md hover:bg-primary-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center"
                >
                  {isDianProcessing ? (
                    <>
                      <Loader2 className="animate-spin h-5 w-5 mr-2" />
                      Processing Files...
                    </>
                  ) : (
                    <>
                      <BarChart3 className="h-5 w-5 mr-2" />
                      Process DIAN Report
                    </>
                  )}
                </button>
              </div>
            </div>

            {/* Results Section */}
            {dianResults && (
              <div className="bg-white rounded-lg shadow-sm border p-6">
                <h2 className="text-xl font-semibold text-gray-900 mb-4">Processing Results</h2>
                
                <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-6">
                  <div className="bg-blue-50 p-4 rounded-lg">
                    <h3 className="font-medium text-blue-900">Total Amount</h3>
                    <p className="text-2xl font-bold text-blue-600">
                      ${dianResults.overall_summaries.total_amount.toLocaleString()}
                    </p>
                  </div>
                  
                  <div className="bg-green-50 p-4 rounded-lg">
                    <h3 className="font-medium text-green-900">Total Transactions</h3>
                    <p className="text-2xl font-bold text-green-600">
                      {dianResults.overall_summaries.total_transactions.toLocaleString()}
                    </p>
                  </div>
                  
                  <div className="bg-purple-50 p-4 rounded-lg">
                    <h3 className="font-medium text-purple-900">Files Processed</h3>
                    <p className="text-2xl font-bold text-purple-600">
                      {dianResults.file_summaries.length}
                    </p>
                  </div>
                </div>

                {/* Consolidation Tables */}
                <div className="space-y-6">
                  {/* Monthly Breakdown */}
                  {consolidationOptions.monthly && dianResults.overall_summaries.monthly_breakdown && Object.keys(dianResults.overall_summaries.monthly_breakdown).length > 0 && (
                    <div className="bg-gray-50 p-4 rounded-lg">
                      <h3 className="text-lg font-semibold text-gray-900 mb-3">Monthly Consolidation</h3>
                      <div className="overflow-x-auto">
                        <table className="min-w-full divide-y divide-gray-200">
                          <thead className="bg-gray-100">
                            <tr>
                              <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">Month</th>
                              <th className="px-4 py-2 text-right text-xs font-medium text-gray-500 uppercase">Total Amount</th>
                              <th className="px-4 py-2 text-right text-xs font-medium text-gray-500 uppercase">Transactions</th>
                            </tr>
                          </thead>
                          <tbody className="bg-white divide-y divide-gray-200">
                            {Object.entries(dianResults.overall_summaries.monthly_breakdown)
                              .sort(([a], [b]) => a.localeCompare(b))
                              .map(([month, data]) => (
                                <tr key={month} className="hover:bg-gray-50">
                                  <td className="px-4 py-2 text-sm text-gray-900">{month}</td>
                                  <td className="px-4 py-2 text-sm text-gray-900 text-right font-medium">
                                    ${data.sum.toLocaleString()}
                                  </td>
                                  <td className="px-4 py-2 text-sm text-gray-900 text-right">{data.count}</td>
                                </tr>
                              ))}
                          </tbody>
                        </table>
                      </div>
                    </div>
                  )}

                  {/* Account Breakdown */}
                  {consolidationOptions.account && dianResults.overall_summaries.account_breakdown && Object.keys(dianResults.overall_summaries.account_breakdown).length > 0 && (
                    <div className="bg-gray-50 p-4 rounded-lg">
                      <h3 className="text-lg font-semibold text-gray-900 mb-3">Account Consolidation</h3>
                      <div className="overflow-x-auto">
                        <table className="min-w-full divide-y divide-gray-200">
                          <thead className="bg-gray-100">
                            <tr>
                              <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">Account Code</th>
                              <th className="px-4 py-2 text-right text-xs font-medium text-gray-500 uppercase">Total Amount</th>
                              <th className="px-4 py-2 text-right text-xs font-medium text-gray-500 uppercase">Transactions</th>
                            </tr>
                          </thead>
                          <tbody className="bg-white divide-y divide-gray-200">
                            {Object.entries(dianResults.overall_summaries.account_breakdown)
                              .sort(([,a], [,b]) => b.sum - a.sum) // Sort by amount descending
                              .map(([account, data]) => (
                                <tr key={account} className="hover:bg-gray-50">
                                  <td className="px-4 py-2 text-sm text-gray-900 font-mono">{account}</td>
                                  <td className="px-4 py-2 text-sm text-gray-900 text-right font-medium">
                                    ${data.sum.toLocaleString()}
                                  </td>
                                  <td className="px-4 py-2 text-sm text-gray-900 text-right">{data.count}</td>
                                </tr>
                              ))}
                          </tbody>
                        </table>
                      </div>
                    </div>
                  )}

                  {/* NIT Breakdown */}
                  {consolidationOptions.nit && dianResults.overall_summaries.nit_breakdown && Object.keys(dianResults.overall_summaries.nit_breakdown).length > 0 && (
                    <div className="bg-gray-50 p-4 rounded-lg">
                      <h3 className="text-lg font-semibold text-gray-900 mb-3">NIT (Third Party) Consolidation</h3>
                      <div className="overflow-x-auto">
                        <table className="min-w-full divide-y divide-gray-200">
                          <thead className="bg-gray-100">
                            <tr>
                              <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">NIT</th>
                              <th className="px-4 py-2 text-right text-xs font-medium text-gray-500 uppercase">Total Amount</th>
                              <th className="px-4 py-2 text-right text-xs font-medium text-gray-500 uppercase">Transactions</th>
                            </tr>
                          </thead>
                          <tbody className="bg-white divide-y divide-gray-200">
                            {Object.entries(dianResults.overall_summaries.nit_breakdown)
                              .sort(([,a], [,b]) => b.sum - a.sum) // Sort by amount descending
                              .map(([nit, data]) => (
                                <tr key={nit} className="hover:bg-gray-50">
                                  <td className="px-4 py-2 text-sm text-gray-900 font-mono">{nit}</td>
                                  <td className="px-4 py-2 text-sm text-gray-900 text-right font-medium">
                                    ${data.sum.toLocaleString()}
                                  </td>
                                  <td className="px-4 py-2 text-sm text-gray-900 text-right">{data.count}</td>
                                </tr>
                              ))}
                          </tbody>
                        </table>
                      </div>
                    </div>
                  )}

                  {/* Document Type Breakdown */}
                  {consolidationOptions.documentType && dianResults.overall_summaries.document_type_breakdown && Object.keys(dianResults.overall_summaries.document_type_breakdown).length > 0 && (
                    <div className="bg-gray-50 p-4 rounded-lg">
                      <h3 className="text-lg font-semibold text-gray-900 mb-3">Document Type Consolidation</h3>
                      <div className="overflow-x-auto">
                        <table className="min-w-full divide-y divide-gray-200">
                          <thead className="bg-gray-100">
                            <tr>
                              <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">Document Type</th>
                              <th className="px-4 py-2 text-right text-xs font-medium text-gray-500 uppercase">Total Amount</th>
                              <th className="px-4 py-2 text-right text-xs font-medium text-gray-500 uppercase">Transactions</th>
                            </tr>
                          </thead>
                          <tbody className="bg-white divide-y divide-gray-200">
                            {Object.entries(dianResults.overall_summaries.document_type_breakdown)
                              .sort(([,a], [,b]) => b.sum - a.sum) // Sort by amount descending
                              .map(([docType, data]) => (
                                <tr key={docType} className="hover:bg-gray-50">
                                  <td className="px-4 py-2 text-sm text-gray-900">{docType}</td>
                                  <td className="px-4 py-2 text-sm text-gray-900 text-right font-medium">
                                    ${data.sum.toLocaleString()}
                                  </td>
                                  <td className="px-4 py-2 text-sm text-gray-900 text-right">{data.count}</td>
                                </tr>
                              ))}
                          </tbody>
                        </table>
                      </div>
                    </div>
                  )}
                </div>

                <div className="flex space-x-4 mt-6">
                  <button
                    onClick={downloadDianReport}
                    className="bg-primary-600 text-white px-4 py-2 rounded-md hover:bg-primary-700 flex items-center"
                  >
                    <Download className="h-4 w-4 mr-2" />
                    Download Report
                  </button>
                </div>
              </div>
            )}
          </div>
        ) : (
          /* Original Excel to PDF Interface */
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
            
            {/* Upload Section */}
            <div className="bg-white rounded-lg shadow-sm border p-6">
              <h2 className="text-xl font-semibold text-gray-900 mb-4">Upload Excel File</h2>
              
              <div
                {...getRootProps()}
                className={`border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-colors ${
                  isDragActive
                    ? 'border-primary-500 bg-primary-50'
                    : 'border-gray-300 hover:border-primary-400 hover:bg-gray-50'
                }`}
              >
                <input {...getInputProps()} />
                <Upload className="mx-auto h-12 w-12 text-gray-400 mb-4" />
                {isDragActive ? (
                  <p className="text-primary-600 font-medium">Drop the Excel file here...</p>
                ) : (
                  <div>
                    <p className="text-gray-600 mb-2">
                      Drag & drop an Excel file here, or click to select
                    </p>
                    <p className="text-sm text-gray-500">
                      Supports .xlsx and .xls files
                    </p>
                  </div>
                )}
              </div>

              {isUploading && (
                <div className="mt-4 flex items-center justify-center text-primary-600">
                  <Loader2 className="animate-spin h-5 w-5 mr-2" />
                  Processing file and generating PDF...
                </div>
              )}

              {parsedData && (
                <div className="mt-6 p-4 bg-green-50 border border-green-200 rounded-lg">
                  <div className="flex items-center justify-between">
                    <div>
                      <h3 className="font-medium text-green-800">File Processed Successfully</h3>
                      <p className="text-sm text-green-600">
                        {parsedData.parsed_data.total_rows} rows, {parsedData.parsed_data.columns} columns
                      </p>
                    </div>
                    <button
                      onClick={() => setShowPreview(!showPreview)}
                      className="flex items-center text-green-700 hover:text-green-800"
                    >
                      <Eye className="h-4 w-4 mr-1" />
                      {showPreview ? 'Hide' : 'Preview'}
                    </button>
                  </div>
                </div>
              )}
            </div>

            {/* PDF Generation Section */}
            <div className="bg-white rounded-lg shadow-sm border p-6">
              <h2 className="text-xl font-semibold text-gray-900 mb-4">Generate PDF Report</h2>
              
              {!parsedData ? (
                <div className="text-center py-12">
                  <FileText className="mx-auto h-12 w-12 text-gray-400 mb-4" />
                  <p className="text-gray-500">Upload an Excel file first to generate a PDF report</p>
                </div>
              ) : (
                <div className="space-y-4">
                  <div className="p-4 bg-blue-50 border border-blue-200 rounded-lg">
                    <h3 className="font-medium text-blue-800">Ready to Generate PDF</h3>
                    <p className="text-sm text-blue-600 mt-1">
                      Click the button below to create a DIAN-compliant PDF report
                    </p>
                  </div>

                  <button
                    onClick={generatePDF}
                    disabled={isGenerating}
                    className="w-full bg-primary-600 text-white py-3 px-4 rounded-md hover:bg-primary-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center"
                  >
                    {isGenerating ? (
                      <>
                        <Loader2 className="animate-spin h-5 w-5 mr-2" />
                        Generating PDF...
                      </>
                    ) : (
                      <>
                        <FileText className="h-5 w-5 mr-2" />
                        Generate DIAN PDF
                      </>
                    )}
                  </button>

                  {pdfUrl && (
                    <div className="p-4 bg-green-50 border border-green-200 rounded-lg">
                      <div className="flex items-center justify-between">
                        <div>
                          <h3 className="font-medium text-green-800">PDF Generated Successfully</h3>
                          <p className="text-sm text-green-600">Your DIAN-compliant report is ready</p>
                        </div>
                        <button
                          onClick={handleDownload}
                          className="bg-green-600 text-white px-4 py-2 rounded-md hover:bg-green-700 flex items-center"
                        >
                          <Download className="h-4 w-4 mr-2" />
                          Download
                        </button>
                      </div>
                    </div>
                  )}
                </div>
              )}
            </div>
          </div>
        )}
      </main>
    </div>
  );
}

export default App; 