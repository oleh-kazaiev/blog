import { Routes, Route } from 'react-router-dom'
import { Container } from '@mui/material'
import Header from './components/Header'
import Footer from './components/Footer'
import HomePage from './pages/HomePage'
import PostDetailPage from './pages/PostDetailPage'
import CategoryPage from './pages/CategoryPage'
import NewPostPage from './pages/NewPostPage'
import ManageDashboardPage from './pages/AdminDashboardPage'
import UserSettingsPage from './pages/UserSettingsPage'
import ProtectedRoute from './components/ProtectedRoute'

function App() {
    return (
        <>
            <Header />
            <Container
                component="main"
                sx={{ py: 4, minHeight: 'calc(100vh - 128px)' }}
            >
                <Routes>
                    <Route path="/" element={<HomePage />} />
                    <Route path="/post/:slug" element={<PostDetailPage />} />
                    <Route path="/category/:slug" element={<CategoryPage />} />
                    <Route
                        path="/settings"
                        element={
                            <ProtectedRoute requireAdmin={false}>
                                <UserSettingsPage />
                            </ProtectedRoute>
                        }
                    />
                    <Route
                        path="/admin"
                        element={
                            <ProtectedRoute requireAdmin={true}>
                                <ManageDashboardPage />
                            </ProtectedRoute>
                        }
                    />
                    <Route
                        path="/admin/posts/new"
                        element={
                            <ProtectedRoute requireAdmin={true}>
                                <NewPostPage />
                            </ProtectedRoute>
                        }
                    />
                </Routes>
            </Container>
            <Footer />
        </>
    )
}

export default App
