import { Routes, Route } from 'react-router-dom';
import { JobList } from './components/JobList/JobList';
import { JobDetailPage } from './components/JobDetail/JobDetail';
import { JobSummaryPage } from './components/JobSummary/JobSummary';
import { JobMapPage } from './components/JobMap/JobMap';
import Home from './pages/Home';
import JobProfile from './components/JobProfile/JobProfile';
import './App.css';

function App() {
  return (
    <Routes>
      <Route path="/" element={<Home />} />
      <Route path="/dashboard" element={<JobList />} />
  	  <Route path="/summary" element={<JobSummaryPage />} />
      <Route path="/map" element={<JobMapPage />} />
      <Route path="/:jobId" element={<JobDetailPage />} />
      <Route path="/profile/:jobId" element={<JobProfile />} />
    </Routes>
  );
}

export default App;
