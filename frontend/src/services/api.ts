import axios from 'axios'

const wait = (ms: number) => new Promise((resolve) => setTimeout(resolve, ms))

// Create an axios instance with default config
const apiBase = process.env.REACT_APP_API_BASE || '/api'
const normalizeBase = (base: string): string => {
    if (!base) {
        return ''
    }

    return base.endsWith('/') ? base.replace(/\/+$/, '') : base
}

const resolvedApiBase = normalizeBase(apiBase) || '/api'
const resolvedUserApiBase = `${resolvedApiBase}/v0/users`

const apiClient = axios.create({
    baseURL: resolvedApiBase,
    timeout: 10000,
    headers: {
        'Content-Type': 'application/json',
        Accept: 'application/json',
    },
    withCredentials: true,
})

// Create a separate axios instance for user API endpoints
const userApiClient = axios.create({
    baseURL: resolvedUserApiBase,
    timeout: 10000,
    headers: {
        'Content-Type': 'application/json',
        Accept: 'application/json',
    },
    withCredentials: true,
})

userApiClient.interceptors.request.use(
    (config) => {
        if (
            config.baseURL &&
            typeof config.url === 'string' &&
            config.url.startsWith('/') &&
            config.url !== '/'
        ) {
            config.url = config.url.replace(/^\//, '')
        }

        const token =
            localStorage.getItem('authToken') || localStorage.getItem('token')
        if (token) {
            config.headers.Authorization = `Token ${token}`
        }

        return config
    },
    (error) => Promise.reject(error)
)

// Request interceptor for API calls
apiClient.interceptors.request.use(
    (config) => {
        // Ensure baseURL is applied even if URL starts with '/'
        // But don't strip the slash if it's the only character (root path)
        if (
            config.baseURL &&
            typeof config.url === 'string' &&
            config.url.startsWith('/') &&
            config.url !== '/'
        ) {
            config.url = config.url.replace(/^\//, '')
        }

        // Get auth token from localStorage if it exists
        const token =
            localStorage.getItem('authToken') || localStorage.getItem('token')
        if (token) {
            config.headers.Authorization = `Token ${token}`
        }

        return config
    },
    (error) => {
        return Promise.reject(error)
    }
)

// Response interceptor for API calls
apiClient.interceptors.response.use(
    (response) => {
        // Caching is disabled - just return the response
        return response
    },
    (error) => {
        // Handle common errors (401, 403, etc.)
        if (error.response) {
            if (error.response.status === 401) {
                // Clear auth data if unauthorized
                localStorage.removeItem('authToken')
                localStorage.removeItem('user')
                // Could also redirect to login page
            }
        }
        return Promise.reject(error)
    }
)

// Apply the same interceptors to userApiClient
userApiClient.interceptors.response.use(
    (response) => {
        return response
    },
    (error) => {
        // Handle common errors (401, 403, etc.)
        if (error.response) {
            if (error.response.status === 401) {
                // Clear auth data if unauthorized
                localStorage.removeItem('authToken')
                localStorage.removeItem('user')
                // Could also redirect to login page
            }
        }
        return Promise.reject(error)
    }
)

// Auth services
export const authService = {
    login: (credentials) => apiClient.post('/login/', credentials),
    register: (userData) => userApiClient.post('/', userData),
    logout: () => userApiClient.post('/logout/'),
    getProfile: () => userApiClient.get('/me/'),
}

// Post services
export const postService = {
    getPosts: (params) => apiClient.get('/v0/posts/', { params }),
    searchPosts: (query: string, params: Record<string, unknown> = {}) =>
        apiClient.get('/v0/search/', { params: { q: query, ...params } }),
    getPost: (slug) => apiClient.get(`/v0/posts/${slug}/`),
    getCategory: (slug) => apiClient.get(`/v0/categories/${slug}/`),
    getCategoryPosts: (slug, params) =>
        apiClient.get('/v0/posts/by_category/', {
            params: { ...params, slug },
        }),
    getCategories: () => apiClient.get('/v0/categories/'),
    createCategory: (name) =>
        apiClient.post('/v0/manage/categories/', { name }),
    purchasePost: (slug) => apiClient.post(`/v0/posts/${slug}/purchase/`),

    // Reaction endpoints
    addReaction: (slug, reactionType) =>
        apiClient.post(`/v0/posts/${slug}/react/`, {
            reaction_type: reactionType,
        }),

    // Comment endpoints
    addComment: (slug, commentData) =>
        apiClient.post(`/v0/posts/${slug}/add-comment/`, commentData),
    // Admin endpoints
    createPost: (data) => apiClient.post('/v0/manage/posts/', data),
}

export const paymentService = {
    getPayment: (paymentId: number) =>
        apiClient.get(`/v0/payments/${paymentId}/`),
    confirmPayment: (paymentId: number) =>
        apiClient.post(`/v0/payments/${paymentId}/confirm/`),
    pollPayment: async (
        paymentId: number,
        maxAttempts = 15,
        initialDelayMs = 1000
    ) => {
        for (let attempt = 0; attempt < maxAttempts; attempt++) {
            const { data } = await paymentService.getPayment(paymentId)
            if (
                !['pending', 'processing', 'requires_action'].includes(
                    data.status
                )
            ) {
                return data
            }

            // Exponential backoff: delay = initialDelay * 2^attempt, capped at 30 seconds
            if (attempt < maxAttempts - 1) {
                const delay = Math.min(
                    initialDelayMs * Math.pow(2, attempt),
                    30000
                )
                await wait(delay)
            }
        }
        throw new Error('Payment confirmation timed out')
    },
}

export const subscriptionService = {
    getPlans: () => apiClient.get('/v0/subscriptions/plans/'),
    createSubscription: (plan: string) =>
        apiClient.post('/v0/subscriptions/', { plan }),
    getSubscription: () => apiClient.get('/v0/subscriptions/current/'),
    confirmSubscription: () => apiClient.post('/v0/subscriptions/confirm/', {}),
    pollSubscription: async (
        id?: number,
        maxAttempts = 15,
        initialDelayMs = 1000
    ) => {
        for (let attempt = 0; attempt < maxAttempts; attempt++) {
            const { data } = await subscriptionService.getSubscription()
            if (
                !['pending', 'processing', 'incomplete', 'trialing'].includes(
                    data.status
                )
            ) {
                return data
            }

            // Exponential backoff: delay = initialDelay * 2^attempt, capped at 30 seconds
            if (attempt < maxAttempts - 1) {
                const delay = Math.min(
                    initialDelayMs * Math.pow(2, attempt),
                    30000
                )
                await wait(delay)
            }
        }
        throw new Error('Subscription confirmation timed out')
    },
}

export { apiClient, userApiClient }
export default apiClient
