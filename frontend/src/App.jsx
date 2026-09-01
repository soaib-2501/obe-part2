import React from 'react';
import { Routes, Route } from 'react-router-dom';
import Navbar from './components/Navbar';
import ProtectedRoute, { GuestRoute } from './components/ProtectedRoute';
import Login from './pages/Login';
import Signup from './pages/Signup';
import Dashboard from './pages/Dashboard';
import Courses from './pages/Courses';
import CourseDetail from './pages/CourseDetail';
import CourseDescription from './pages/CourseDescription';
import CourseOpeningReport from './pages/CourseOpeningReport';
import CourseAssessments from './pages/CourseAssessments';
import CourseAssessmentTools from './pages/CourseAssessmentTools';
import Users from './pages/Users';

export default function App() {
  return (
    <div className="min-h-screen bg-slate-50">
      <Navbar />
      <Routes>
        <Route path="/login" element={<GuestRoute><Login /></GuestRoute>} />
        <Route path="/signup" element={<GuestRoute><Signup /></GuestRoute>} />
        <Route path="/" element={<ProtectedRoute><Dashboard /></ProtectedRoute>} />
        <Route path="/users" element={<ProtectedRoute adminOnly><Users /></ProtectedRoute>} />
        <Route path="/courses" element={<ProtectedRoute><Courses /></ProtectedRoute>} />
        <Route path="/courses/:id" element={<ProtectedRoute><CourseDetail /></ProtectedRoute>} />
        <Route path="/courses/:id/description" element={<ProtectedRoute><CourseDescription /></ProtectedRoute>} />
        <Route path="/courses/:id/opening-report" element={<ProtectedRoute><CourseOpeningReport /></ProtectedRoute>} />
        <Route path="/courses/:id/assessments" element={<ProtectedRoute><CourseAssessments /></ProtectedRoute>} />
        <Route path="/courses/:id/assessment-tools" element={<ProtectedRoute><CourseAssessmentTools /></ProtectedRoute>} />
      </Routes>
    </div>
  );
}
