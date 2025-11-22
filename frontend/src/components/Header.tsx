import React, { useState } from 'react'
import { Link as RouterLink } from 'react-router-dom'
import {
    AppBar,
    Toolbar,
    Typography,
    Button,
    Container,
    Box,
    Menu,
    MenuItem,
    IconButton,
    Avatar,
    Divider,
    Tooltip,
} from '@mui/material'
import Brightness4Icon from '@mui/icons-material/Brightness4'
import Brightness7Icon from '@mui/icons-material/Brightness7'
import MenuIcon from '@mui/icons-material/Menu'
import PersonIcon from '@mui/icons-material/Person'
import AuthDialog from './auth/AuthDialog'
import { ColorModeContext } from '../theme'
import { useAuth } from '../contexts/AuthContext'

const Header = () => {
    const colorMode = React.useContext(ColorModeContext)
    const { user, isAdmin, logout: logoutUser } = useAuth()
    const [navMenuAnchorEl, setNavMenuAnchorEl] = useState(null)
    const [userMenuAnchorEl, setUserMenuAnchorEl] = useState(null)
    const [authDialogOpen, setAuthDialogOpen] = useState(false)
    const navMenuOpen = Boolean(navMenuAnchorEl)
    const userMenuOpen = Boolean(userMenuAnchorEl)

    const handleNavMenuClick = (event) => {
        setNavMenuAnchorEl(event.currentTarget)
    }

    const handleNavMenuClose = () => {
        setNavMenuAnchorEl(null)
    }

    const handleUserMenuClick = (event) => {
        setUserMenuAnchorEl(event.currentTarget)
    }

    const handleUserMenuClose = () => {
        setUserMenuAnchorEl(null)
    }

    const handleAuthDialogOpen = () => {
        setAuthDialogOpen(true)
    }

    const handleAuthDialogClose = () => {
        setAuthDialogOpen(false)
    }

    const handleLoginSuccess = () => {
        // User is already set in AuthContext via login forms
    }

    const handleLogout = async () => {
        logoutUser()
        handleUserMenuClose()
    }

    return (
        <>
            <AppBar
                position="static"
                sx={{
                    bgcolor: (theme) =>
                        theme.palette.mode === 'dark'
                            ? theme.palette.grey[900]
                            : theme.palette.grey[100],
                    color: (theme) =>
                        theme.palette.mode === 'dark'
                            ? '#fff'
                            : theme.palette.text.primary,
                }}
            >
                <Container maxWidth="lg">
                    <Toolbar>
                        <Box
                            sx={{
                                display: { xs: 'none', md: 'flex' },
                                alignItems: 'center',
                                gap: 1,
                                mr: 2,
                                flexGrow: 1,
                            }}
                        >
                            <Button
                                variant="text"
                                color="inherit"
                                component={RouterLink}
                                to="/"
                            >
                                Home
                            </Button>
                            {(user?.is_admin ||
                                user?.has_active_subscription) && (
                                <Button
                                    variant="text"
                                    color="inherit"
                                    component={RouterLink}
                                    to="/admin/posts/new"
                                >
                                    Create New Post
                                </Button>
                            )}
                        </Box>

                        {/* Theme toggle */}
                        <Tooltip
                            title={`Switch to ${colorMode.mode === 'light' ? 'dark' : 'light'} mode`}
                        >
                            <IconButton
                                color="inherit"
                                onClick={colorMode.toggleColorMode}
                                sx={{ mr: 1 }}
                                aria-label="toggle theme"
                            >
                                {colorMode.mode === 'dark' ? (
                                    <Brightness7Icon />
                                ) : (
                                    <Brightness4Icon />
                                )}
                            </IconButton>
                        </Tooltip>

                        {/* User Authentication */}
                        {user ? (
                            <Box>
                                <IconButton
                                    onClick={handleUserMenuClick}
                                    color="inherit"
                                >
                                    {user.profile_picture ? (
                                        <Avatar
                                            src={user.profile_picture}
                                            alt={user.full_name}
                                        />
                                    ) : (
                                        <Avatar>
                                            {user.first_name[0]}
                                            {user.last_name[0]}
                                        </Avatar>
                                    )}
                                </IconButton>
                                <Menu
                                    id="user-menu"
                                    anchorEl={userMenuAnchorEl}
                                    open={userMenuOpen}
                                    onClose={handleUserMenuClose}
                                >
                                    <MenuItem disabled>
                                        <Typography variant="subtitle2">
                                            Signed in as{' '}
                                            <strong>{user.email}</strong>
                                        </Typography>
                                    </MenuItem>
                                    <Divider />
                                    <MenuItem
                                        component={RouterLink}
                                        to="/settings"
                                        onClick={handleUserMenuClose}
                                    >
                                        User Settings
                                    </MenuItem>
                                    <Divider />
                                    {(isAdmin ||
                                        user?.has_active_subscription) && (
                                        <>
                                            <MenuItem
                                                component={RouterLink}
                                                to="/admin"
                                                onClick={handleUserMenuClose}
                                            >
                                                Admin Dashboard
                                            </MenuItem>
                                            <MenuItem
                                                component={RouterLink}
                                                to="/admin/posts/new"
                                                onClick={handleUserMenuClose}
                                            >
                                                New Post
                                            </MenuItem>
                                            <Divider />
                                        </>
                                    )}
                                    <MenuItem onClick={handleLogout}>
                                        Logout
                                    </MenuItem>
                                </Menu>
                            </Box>
                        ) : (
                            <Button
                                variant="text"
                                color="inherit"
                                startIcon={<PersonIcon />}
                                onClick={handleAuthDialogOpen}
                            >
                                Sign In
                            </Button>
                        )}

                        {/* Mobile Navigation */}
                        <Box sx={{ display: { xs: 'flex', md: 'none' } }}>
                            <IconButton
                                size="large"
                                edge="end"
                                color="inherit"
                                aria-label="menu"
                                onClick={handleNavMenuClick}
                            >
                                <MenuIcon />
                            </IconButton>
                            <Menu
                                anchorEl={navMenuAnchorEl}
                                open={navMenuOpen}
                                onClose={handleNavMenuClose}
                            >
                                <MenuItem
                                    component={RouterLink}
                                    to="/"
                                    onClick={handleNavMenuClose}
                                >
                                    Home
                                </MenuItem>
                                {user?.is_admin && (
                                    <MenuItem
                                        component={RouterLink}
                                        to="/admin/posts/new"
                                        onClick={handleNavMenuClose}
                                    >
                                        Create New Post
                                    </MenuItem>
                                )}
                            </Menu>
                        </Box>
                    </Toolbar>
                </Container>
            </AppBar>

            {/* Authentication Dialog */}
            <AuthDialog
                open={authDialogOpen}
                onClose={handleAuthDialogClose}
                onLoginSuccess={handleLoginSuccess}
            />
        </>
    )
}

export default Header
