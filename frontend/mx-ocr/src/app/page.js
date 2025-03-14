import DocumentUploader from './components/document-uploader';

export default function Home() {
  return (
    <main className="min-h-screen bg-slate-50 p-4 md:p-8">
      <div className="max-w-4xl mx-auto">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-slate-800">Mortgage Document Portal</h1>
          <p className="text-slate-600 mt-2">
            Upload your required documents to complete your mortgage application.
          </p>
        </div>
        
        <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-6">
          <h2 className="text-xl font-semibold text-slate-800 mb-4">Document Upload</h2>
          <p className="text-slate-600 mb-6">
            Please upload the following documents in PDF, PNG, or JPG format:
          </p>
          
          <div className="space-y-4 mb-6">
            <div className="flex items-start gap-3">
              <div className="w-5 h-5 rounded-full bg-blue-100 flex items-center justify-center mt-0.5">
                <span className="text-blue-600 text-xs font-medium">1</span>
              </div>
              <div>
                <p className="font-medium text-slate-800">Proof of Income</p>
                <p className="text-sm text-slate-500">Last 3 months of pay stubs or tax returns</p>
              </div>
            </div>
            
            <div className="flex items-start gap-3">
              <div className="w-5 h-5 rounded-full bg-blue-100 flex items-center justify-center mt-0.5">
                <span className="text-blue-600 text-xs font-medium">2</span>
              </div>
              <div>
                <p className="font-medium text-slate-800">Bank Statements</p>
                <p className="text-sm text-slate-500">Last 3 months of all bank accounts</p>
              </div>
            </div>
            
            <div className="flex items-start gap-3">
              <div className="w-5 h-5 rounded-full bg-blue-100 flex items-center justify-center mt-0.5">
                <span className="text-blue-600 text-xs font-medium">3</span>
              </div>
              <div>
                <p className="font-medium text-slate-800">Identification</p>
                <p className="text-sm text-slate-500">Government-issued photo ID</p>
              </div>
            </div>
          </div>
          
          <DocumentUploader />
        </div>
      </div>
    </main>
  );
}