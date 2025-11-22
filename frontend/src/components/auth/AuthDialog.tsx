import React, { useState } from 'react'
import {
    Dialog,
    DialogContent,
    DialogTitle,
    Tabs,
    Tab,
    Box,
} from '@mui/material'
import LoginForm from './LoginForm'
import RegisterForm from './RegisterForm'

const AuthDialog = ({ open, onClose, onLoginSuccess }) => {
    const [tabValue, setTabValue] = useState(0)

    const handleTabChange = (event, newValue) => {
        setTabValue(newValue)
    }

    return (
        <Dialog open={open} onClose={onClose} maxWidth="sm" fullWidth>
            <DialogTitle>
                <Tabs
                    value={tabValue}
                    onChange={handleTabChange}
                    variant="fullWidth"
                >
                    <Tab label="Login" />
                    <Tab label="Register" />
                </Tabs>
            </DialogTitle>
            <DialogContent>
                <Box sx={{ py: 2 }}>
                    {tabValue === 0 ? (
                        <LoginForm
                            onSuccess={onLoginSuccess}
                            onClose={onClose}
                        />
                    ) : (
                        <RegisterForm
                            onSuccess={onLoginSuccess}
                            onClose={onClose}
                        />
                    )}
                </Box>
            </DialogContent>
        </Dialog>
    )
}

export default AuthDialog
