import React, { useState } from 'react'
import {
    Button,
    TextField,
    DialogActions,
    Alert,
    CircularProgress,
} from '@mui/material'
import { authService } from '../../services/api'
import { useAuth } from '../../contexts/AuthContext'
import { User, LoginCredentials } from '../../types'

interface LoginFormProps {
    onSuccess: (user: User) => void
    onClose: () => void
}

interface ApiErrorResponse {
    response?: {
        data?: {
            error?: string
        }
    }
}

const LoginForm: React.FC<LoginFormProps> = ({ onSuccess, onClose }) => {
    const { login: setAuthUser } = useAuth()
    const [formData, setFormData] = useState<LoginCredentials>({
        email: '',
        password: '',
    })
    const [loading, setLoading] = useState<boolean>(false)
    const [error, setError] = useState<string | null>(null)

    const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        setFormData({
            ...formData,
            [e.target.name]: e.target.value,
        })
    }

    const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
        e.preventDefault()
        setLoading(true)
        setError(null)

        try {
            const response = await authService.login(formData)

            // Update auth context
            setAuthUser(response.data.token, response.data.user)

            onSuccess(response.data.user)
            onClose()
        } catch (err: unknown) {
            const error = err as ApiErrorResponse
            console.error('Login error:', error)
            setError(
                error.response?.data?.error || 'Login failed. Please try again.'
            )
        } finally {
            setLoading(false)
        }
    }

    return (
        <form onSubmit={handleSubmit}>
            {error && (
                <Alert severity="error" sx={{ mb: 2 }}>
                    {error}
                </Alert>
            )}

            <TextField
                autoFocus
                margin="dense"
                name="email"
                label="Email Address"
                type="email"
                fullWidth
                variant="outlined"
                value={formData.email}
                onChange={handleChange}
                required
            />
            <TextField
                margin="dense"
                name="password"
                label="Password"
                type="password"
                fullWidth
                variant="outlined"
                value={formData.password}
                onChange={handleChange}
                required
            />

            <DialogActions>
                <Button onClick={onClose} disabled={loading}>
                    Cancel
                </Button>
                <Button
                    type="submit"
                    variant="contained"
                    color="primary"
                    disabled={loading}
                >
                    {loading ? <CircularProgress size={24} /> : 'Login'}
                </Button>
            </DialogActions>
        </form>
    )
}

export default LoginForm
