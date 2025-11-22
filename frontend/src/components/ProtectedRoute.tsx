import React from 'react'
import { Navigate } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'
import { Box, CircularProgress, Typography, Container } from '@mui/material'

interface ProtectedRouteProps {
    children: React.ReactNode
    requireAdmin?: boolean
}

const ProtectedRoute: React.FC<ProtectedRouteProps> = ({
    children,
    requireAdmin = false,
}) => {
    const { isAuthenticated, isAdmin, hasActiveSubscription, loading } =
        useAuth()

    if (loading) {
        return (
            <Container>
                <Box
                    display="flex"
                    flexDirection="column"
                    alignItems="center"
                    justifyContent="center"
                    minHeight="60vh"
                    gap={2}
                >
                    <CircularProgress />
                    <Typography variant="body1" color="text.secondary">
                        Loading...
                    </Typography>
                </Box>
            </Container>
        )
    }

    if (!isAuthenticated) {
        return <Navigate to="/" replace />
    }

    if (requireAdmin && !(isAdmin || hasActiveSubscription)) {
        return (
            <Container>
                <Box
                    display="flex"
                    flexDirection="column"
                    alignItems="center"
                    justifyContent="center"
                    minHeight="60vh"
                    gap={2}
                >
                    <Typography variant="h4" color="error">
                        Access Denied
                    </Typography>
                    <Typography variant="body1" color="text.secondary">
                        You do not have permission to access this page.
                    </Typography>
                </Box>
            </Container>
        )
    }

    return <>{children}</>
}

export default ProtectedRoute
