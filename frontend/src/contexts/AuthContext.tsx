import React, {
    createContext,
    useContext,
    useState,
    useEffect,
    ReactNode,
} from 'react'
import { User } from '../types'
import { authService } from '../services/api'

interface AuthContextType {
    user: User | null
    token: string | null
    isAuthenticated: boolean
    isAdmin: boolean
    hasActiveSubscription: boolean
    loading: boolean
    login: (token: string, user: User) => void
    logout: () => void
    refreshUser: () => Promise<void>
}

const AuthContext = createContext<AuthContextType | undefined>(undefined)

interface AuthProviderProps {
    children: ReactNode
}

export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
    const [user, setUser] = useState<User | null>(null)
    const [token, setToken] = useState<string | null>(null)
    const [loading, setLoading] = useState(true)

    const clearStoredAuth = () => {
        localStorage.removeItem('token')
        localStorage.removeItem('authToken')
        localStorage.removeItem('user')
    }

    const persistAuth = (newToken: string, newUser?: User) => {
        localStorage.setItem('token', newToken)
        localStorage.setItem('authToken', newToken)
        if (newUser) {
            localStorage.setItem('user', JSON.stringify(newUser))
        }
    }

    // Initialize auth state from localStorage
    useEffect(() => {
        let isMounted = true

        const initAuth = async () => {
            const storedToken =
                localStorage.getItem('authToken') ||
                localStorage.getItem('token')

            if (storedToken) {
                setToken(storedToken)
                persistAuth(storedToken)

                try {
                    const response = await authService.getProfile()
                    if (!isMounted) return
                    setUser(response.data)
                    localStorage.setItem('user', JSON.stringify(response.data))
                } catch (error) {
                    console.error('Failed to fetch user:', error)
                    clearStoredAuth()
                    if (isMounted) {
                        setToken(null)
                        setUser(null)
                    }
                }
            }

            if (isMounted) {
                setLoading(false)
            }
        }

        initAuth()

        // Listen for storage changes from other tabs
        const handleStorageChange = (e: StorageEvent) => {
            if (e.key === 'authToken' || e.key === 'token') {
                const newToken = e.newValue
                if (newToken) {
                    // Token was added or updated in another tab
                    setToken(newToken)

                    authService
                        .getProfile()
                        .then((response) => {
                            setUser(response.data)
                            localStorage.setItem(
                                'user',
                                JSON.stringify(response.data)
                            )
                        })
                        .catch((err) => {
                            console.error(
                                'Failed to fetch user on storage change:',
                                err
                            )
                        })
                } else {
                    // Token was removed in another tab
                    setToken(null)
                    setUser(null)
                    localStorage.removeItem('user')
                }
            }
        }

        window.addEventListener('storage', handleStorageChange)

        return () => {
            isMounted = false
            window.removeEventListener('storage', handleStorageChange)
        }
    }, [])

    const login = (newToken: string, newUser: User) => {
        setToken(newToken)
        setUser(newUser)
        persistAuth(newToken, newUser)
    }

    const logout = () => {
        setToken(null)
        setUser(null)
        clearStoredAuth()
        authService.logout().catch((error) => {
            console.error('Failed to logout:', error)
        })
    }

    const refreshUser = async () => {
        if (!token) return

        try {
            const response = await authService.getProfile()
            setUser(response.data)
        } catch (error) {
            console.error('Failed to refresh user:', error)
            logout()
        }
    }

    const value: AuthContextType = {
        user,
        token,
        isAuthenticated: !!token && !!user,
        isAdmin: user?.is_admin || false,
        hasActiveSubscription: user?.has_active_subscription || false,
        loading,
        login,
        logout,
        refreshUser,
    }

    return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

export const useAuth = (): AuthContextType => {
    const context = useContext(AuthContext)
    if (context === undefined) {
        throw new Error('useAuth must be used within an AuthProvider')
    }
    return context
}
