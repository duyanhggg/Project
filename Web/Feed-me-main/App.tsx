import React, { useEffect, useState } from 'react';
import { HashRouter, Routes, Route, useSearchParams, Navigate } from 'react-router-dom';
import { CreateProfile } from './pages/CreateProfile';
import { ViewProfile } from './pages/ViewProfile';
import { decodeProfileData } from './utils';

const ViewPageWrapper: React.FC = () => {
  const [searchParams] = useSearchParams();
  const dataStr = searchParams.get('data');
  const [profileData, setProfileData] = useState(decodeProfileData(dataStr));

  useEffect(() => {
    setProfileData(decodeProfileData(dataStr));
  }, [dataStr]);

  return (
    <div className="min-h-screen p-4 md:p-8 flex items-start justify-center">
      <ViewProfile data={profileData} />
    </div>
  );
};

const CreatePageWrapper: React.FC = () => {
  return (
    <div className="min-h-screen p-4 md:p-8">
        <CreateProfile />
    </div>
  );
};

function App() {
  return (
    <HashRouter>
      <Routes>
        <Route path="/" element={<CreatePageWrapper />} />
        <Route path="/view" element={<ViewPageWrapper />} />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </HashRouter>
  );
}

export default App;