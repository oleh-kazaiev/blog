import React, { useState } from 'react'
import {
    Button,
    TextField,
    DialogActions,
    Alert,
    CircularProgress,
    Grid,
} from '@mui/material'
import { authService } from '../../services/api'
import { useAuth } from '../../contexts/AuthContext'

const RegisterForm = ({ onSuccess, onClose }) => {
    const { login: setAuthUser } = useAuth()
    const [formData, setFormData] = useState({
        email: '',
        first_name: '',
        last_name: '',
        password: '',
        confirm_password: '',
    })
    const [loading, setLoading] = useState(false)
    const [error, setError] = useState(null)

    const handleChange = (e) => {
        setFormData({
            ...formData,
            [e.target.name]: e.target.value,
        })
    }

    const handleSubmit = async (e) => {
        e.preventDefault()
        setLoading(true)
        setError(null)

        if (formData.password !== formData.confirm_password) {
            setError("Passwords don't match")
            setLoading(false)
            return
        }

        try {
            await authService.register(formData)

            const loginResponse = await authService.login({
                email: formData.email,
                password: formData.password,
            })

            // Update auth context
            setAuthUser(loginResponse.data.token, loginResponse.data.user)

            onSuccess(loginResponse.data.user)
            onClose()
        } catch (err) {
            console.error('Registration error:', err)
            setError(
                err.response?.data?.email ||
                    err.response?.data?.password ||
                    err.response?.data?.non_field_errors ||
                    'Registration failed. Please try again.'
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

            <Grid container spacing={2}>
                <Grid item xs={12}>
                    <TextField
                        autoFocus
                        name="email"
                        label="Email Address"
                        type="email"
                        fullWidth
                        variant="outlined"
                        value={formData.email}
                        onChange={handleChange}
                        required
                    />
                </Grid>
                <Grid item xs={12} sm={6}>
                    <TextField
                        name="first_name"
                        label="First Name"
                        type="text"
                        fullWidth
                        variant="outlined"
                        value={formData.first_name}
                        onChange={handleChange}
                        required
                    />
                </Grid>
                <Grid item xs={12} sm={6}>
                    <TextField
                        name="last_name"
                        label="Last Name"
                        type="text"
                        fullWidth
                        variant="outlined"
                        value={formData.last_name}
                        onChange={handleChange}
                        required
                    />
                </Grid>
                <Grid item xs={12}>
                    <TextField
                        name="password"
                        label="Password"
                        type="password"
                        fullWidth
                        variant="outlined"
                        value={formData.password}
                        onChange={handleChange}
                        required
                    />
                </Grid>
                <Grid item xs={12}>
                    <TextField
                        name="confirm_password"
                        label="Confirm Password"
                        type="password"
                        fullWidth
                        variant="outlined"
                        value={formData.confirm_password}
                        onChange={handleChange}
                        required
                    />
                </Grid>
            </Grid>

            <DialogActions sx={{ mt: 2 }}>
                <Button onClick={onClose} disabled={loading}>
                    Cancel
                </Button>
                <Button
                    type="submit"
                    variant="contained"
                    color="primary"
                    disabled={loading}
                >
                    {loading ? <CircularProgress size={24} /> : 'Register'}
                </Button>
            </DialogActions>
        </form>
    )
}

export default RegisterForm
