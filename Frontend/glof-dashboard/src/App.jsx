import { BrowserRouter, Routes, Route } from 'react-router-dom';
import Layout from './components/Layout';
import Dashboard from './pages/Dashboard';
import SARAnalysis from './pages/SARAnalysis';
import LakeAnalysis from './pages/LakeAnalysis';
import TerrainAnalysis from './pages/TerrainAnalysis';
import Alerts from './pages/Alerts';
import Settings from './pages/Settings';
import './index.css';

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Layout />}>
          <Route index element={<Dashboard />} />
          <Route path="sar-analysis" element={<SARAnalysis />} />
          <Route path="lake-analysis" element={<LakeAnalysis />} />
          <Route path="terrain-analysis" element={<TerrainAnalysis />} />
          <Route path="alerts" element={<Alerts />} />
          <Route path="settings" element={<Settings />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}

export default App;
