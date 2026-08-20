import React from 'react';
import { NavLink } from 'react-router-dom';

export default function CourseSubnav({ courseId }) {
  const link = 'px-3 py-1.5 rounded text-sm font-medium';
  const active = 'bg-slate-900 text-white';
  const idle = 'text-slate-600 hover:bg-slate-100';

  return (
    <div className="flex gap-2 mb-6">
      <NavLink
        to={`/courses/${courseId}`}
        end
        className={({ isActive }) => `${link} ${isActive ? active : idle}`}
      >
        Outcomes & Mapping
      </NavLink>
      <NavLink
        to={`/courses/${courseId}/assessments`}
        className={({ isActive }) => `${link} ${isActive ? active : idle}`}
      >
        Students & Marks
      </NavLink>
      <NavLink
        to={`/courses/${courseId}/projects`}
        className={({ isActive }) => `${link} ${isActive ? active : idle}`}
      >
        Projects
      </NavLink>
    </div>
  );
}
