import { Routes, Route } from 'react-router-dom';
import { JobList } from './components/JobList/JobList';
import { JobDetailPage } from './components/JobDetail/JobDetail';
import { JobSummaryPage } from './components/JobSummary/JobSummary';
import { JobMapPage } from './components/JobMap/JobMap';
import Home from './pages/Home';
import JobProfile from './components/JobProfile/JobProfile';
import { JobProfileList } from './components/JobProfileList/JobProfileList';
import { JobProfileDetail } from './components/JobProfileList/JobProfileDetail';
import CapabilityAnalysis from './pages/CapabilityAnalysis';
import CareerReport from './pages/CareerReport';
import JobMatch from './pages/JobMatch';
import './App.css';

function App() {
  return (
    <Routes>
      <Route path="/" element={<Home />} />
      <Route path="/dashboard" element={<JobList />} />
      <Route path="/summary" element={<JobSummaryPage />} />
      <Route path="/map" element={<JobMapPage />} />
      <Route path="/:jobId" element={<JobDetailPage />} />
      <Route path="/profile-list" element={<JobProfileList />} />
      <Route path="/profile-list/:jobName" element={<JobProfileDetail />} />
      <Route path="/profile/:jobId" element={<JobProfile />} />
      <Route path="/capability-analysis" element={<CapabilityAnalysis />} />
      <Route path="/career-report" element={<CareerReport />} />
      <Route path="/job-match" element={<JobMatch />} />
    </Routes>
  );
}

export default App;
