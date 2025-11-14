import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
import { useAuthStore } from './store/authStore'
import { useEffect } from 'react'
import StudentHome from './pages/StudentHome'
import TeacherHome from './pages/TeacherHome'
import AdminHome from './pages/AdminHome'
import TeacherPreferences from './pages/TeacherPreferences'
import ClassroomIssueReport from './pages/ClassroomIssueReport'
import StudentMenu from './pages/StudentMenu'
import AdminCreateTeacher from './pages/AdminCreateTeacher'
import Login from './pages/Login'
import Register from './pages/Register'
import LoadingScreen from './components/LoadingScreen'
// Admin pages
import TeachersList from './pages/admin/TeachersList'
import EditTeacher from './pages/admin/EditTeacher'
import GroupsList from './pages/admin/GroupsList'
import StudentsList from './pages/admin/StudentsList'
import ClassroomsList from './pages/admin/ClassroomsList'
import BuildingsList from './pages/admin/BuildingsList'
// Placeholders for create/edit pages
import CreateGroup from './pages/admin/CreateGroup'
import EditGroup from './pages/admin/EditGroup'
import CreateStudent from './pages/admin/CreateStudent'
import EditStudent from './pages/admin/EditStudent'
import CreateClassroom from './pages/admin/CreateClassroom'
import EditClassroom from './pages/admin/EditClassroom'
import CreateBuilding from './pages/admin/CreateBuilding'
import EditBuilding from './pages/admin/EditBuilding'
import CourseLoadsList from './pages/admin/CourseLoadsList'
import CreateCourseLoad from './pages/admin/CreateCourseLoad'
import GenerateSchedule from './pages/admin/GenerateSchedule'
import ViewGroupSchedule from './pages/admin/ViewGroupSchedule'
import Profile from './pages/Profile'
import TicketsList from './pages/TicketsList'
import CreateTicket from './pages/CreateTicket'
import TicketDetails from './pages/TicketDetails'
import UniversityPasses from './pages/UniversityPasses'
import SingleWindow from './pages/SingleWindow'
import Parking from './pages/Parking'
import OtherServices from './pages/OtherServices'

function App() {
  const { user, isLoading, checkAuth, devRole } = useAuthStore()
  
  // Используем dev-роль, если она установлена, иначе реальную роль пользователя
  const effectiveRole = devRole || user?.role

  useEffect(() => {
    // Проверяем авторизацию при загрузке
    checkAuth()
  }, [checkAuth])

  useEffect(() => {
    // Инициализация MAX WebApp
    if (window.WebApp) {
      window.WebApp.ready()
    }
  }, [])

  if (isLoading) {
    return <LoadingScreen />
  }

  // Если пользователь не авторизован, показываем страницу входа
  if (!user) {
    return (
      <Router>
        <Routes>
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} />
          <Route path="*" element={<Navigate to="/login" replace />} />
        </Routes>
      </Router>
    )
  }

  // Роутинг в зависимости от роли (с учетом dev-режима)
  return (
    <Router>
      <Routes>
        {/* Студент */}
        {effectiveRole === 'student' && (
          <>
            <Route path="/" element={<StudentHome />} />
            <Route path="/menu" element={<StudentMenu />} />
            <Route path="/profile" element={<Profile />} />
            <Route path="/tickets/create" element={<CreateTicket />} />
            <Route path="/report-issue/:lessonId" element={<ClassroomIssueReport />} />
            <Route path="/passes" element={<UniversityPasses />} />
            <Route path="/single-window" element={<SingleWindow />} />
            <Route path="/parking" element={<Parking />} />
            <Route path="/other-services" element={<OtherServices />} />
          </>
        )}

        {/* Преподаватель */}
        {effectiveRole === 'teacher' && (
          <>
            <Route path="/" element={<TeacherHome />} />
            <Route path="/preferences" element={<TeacherPreferences />} />
            <Route path="/report-issue/:lessonId" element={<ClassroomIssueReport />} />
            <Route path="/profile" element={<Profile />} />
            <Route path="/tickets/create" element={<CreateTicket />} />
          </>
        )}

        {/* Админ */}
        {(effectiveRole === 'admin' || effectiveRole === 'staff') && (
          <>
            <Route path="/" element={<AdminHome />} />
            <Route path="/admin/teachers" element={<TeachersList />} />
            <Route path="/admin/teachers/create" element={<AdminCreateTeacher />} />
            <Route path="/admin/teachers/:id/edit" element={<EditTeacher />} />
            <Route path="/admin/groups" element={<GroupsList />} />
            <Route path="/admin/groups/create" element={<CreateGroup />} />
            <Route path="/admin/groups/:id/edit" element={<EditGroup />} />
            <Route path="/admin/students" element={<StudentsList />} />
            <Route path="/admin/students/create" element={<CreateStudent />} />
            <Route path="/admin/students/:id/edit" element={<EditStudent />} />
            <Route path="/admin/classrooms" element={<ClassroomsList />} />
            <Route path="/admin/classrooms/create" element={<CreateClassroom />} />
            <Route path="/admin/classrooms/:id/edit" element={<EditClassroom />} />
            <Route path="/admin/buildings" element={<BuildingsList />} />
            <Route path="/admin/buildings/create" element={<CreateBuilding />} />
            <Route path="/admin/buildings/:id/edit" element={<EditBuilding />} />
            <Route path="/admin/course-loads" element={<CourseLoadsList />} />
            <Route path="/admin/course-loads/create" element={<CreateCourseLoad />} />
            <Route path="/admin/schedule/generate" element={<GenerateSchedule />} />
            <Route path="/admin/schedule/group" element={<ViewGroupSchedule />} />
            <Route path="/profile" element={<Profile />} />
            <Route path="/tickets" element={<TicketsList />} />
            <Route path="/tickets/create" element={<CreateTicket />} />
            <Route path="/tickets/:id" element={<TicketDetails />} />
            {/* Старые пути для обратной совместимости */}
            <Route path="/teachers/create" element={<AdminCreateTeacher />} />
          </>
        )}

        {/* Fallback */}
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </Router>
  )
}

export default App

