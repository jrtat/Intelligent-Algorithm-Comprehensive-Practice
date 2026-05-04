import { Routes, Route } from 'react-router-dom';
import { JobDashboard } from './components/JobDashboard/JobDashboard.tsx';
import { JobDetailPage } from './components/JobDetail/JobDetail.tsx';
import { JobSummaryPage } from './components/JobSummary/JobSummary.tsx';
import { JobMapPage } from './components/JobMap/JobMap.tsx';
import Home from './pages/Home.tsx';
//import JobProfile from './components/JobProfile/JobProfile';
import { JobProfileDetail } from './components/JobProfileList/JobProfileDetail.tsx';
import CapabilityAnalysis from './pages/CapabilityAnalysis.tsx';
import CareerReport from './pages/CareerReport.tsx';
import JobMatch from './pages/JobMatch.tsx';
import TopToast from './components/TopToast/TopToast.tsx';
import { ToastProvider, useToast } from './context/ToastContext.tsx';
import './App.css';

function AppContent() {
  const { toastVisible, toastMessage, toastOnClick, hideToast } = useToast();

  return (
    <>
      <TopToast
        visible={toastVisible}
        message={toastMessage}
        onClick={toastOnClick}
        onDismiss={hideToast}
      />
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/dashboard" element={<JobDashboard />} />
        <Route path="/summary" element={<JobSummaryPage />} />
        <Route path="/map" element={<JobMapPage />} />
        <Route path="/:jobId" element={<JobDetailPage />} />
        <Route path="/profile-list" element={<JobProfileDetail />} />
        <Route path="/profile-list/:jobName" element={<JobProfileDetail />} />
        {/* <Route path="/profile/:jobId" element={<JobProfile />} /> */}
        <Route path="/capability-analysis" element={<CapabilityAnalysis />} />
        <Route path="/career-report" element={<CareerReport />} />
        <Route path="/job-match" element={<JobMatch />} />
      </Routes>
    </>
  );
}

function App() {
  return (
    <ToastProvider>
      <AppContent />
    </ToastProvider>
  );
}

export default App;
