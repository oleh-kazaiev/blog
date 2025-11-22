export interface User {
    id: string
    email: string
    first_name?: string
    last_name?: string
    is_admin?: boolean
    profile_picture?: string
    full_name?: string
    bio?: string
    website?: string
    has_active_subscription?: boolean
    emails?: Email[]
}

export interface Category {
    id: number
    name: string
    slug: string
    description?: string
    posts_count?: number
}

export interface Post {
    id: number
    title: string
    slug: string
    excerpt: string
    content: string
    featured_image?: string
    author: User
    category: Category
    created_at: string
    updated_at: string
    published_at?: string
    is_published: boolean
    tags?: string[]
    is_paid?: boolean
    price_cents?: number
    user_has_access?: boolean
    show_purchase_button?: boolean
    user_reaction?: string | null
    user_purchase_status?: string | null
    comments?: Comment[]
    likes_count?: number
    dislikes_count?: number
}

export interface Comment {
    id: number
    post?: number
    author?: User
    name?: string
    email?: string
    body: string
    created_at: string
    parent?: number
    replies?: Comment[]
    author_details?: User
}

export interface AuthResponse {
    token: string
    user: User
}

export interface LoginCredentials {
    email: string
    password: string
}

export interface RegisterData {
    email: string
    password: string
    confirm_password: string
    first_name?: string
    last_name?: string
}

export interface NotificationPreferences {
    comment_on_post: boolean
    post_reaction: boolean
    payment_successful: boolean
    payment_failed: boolean
    subscription_activated: boolean
    subscription_expiring: boolean
    subscription_cancelled: boolean
}

export interface Email {
    id: number
    subject: string
    body: string
    from_email: string
    to_email: string
    created_at: string
    read: boolean
}

export interface ApiError {
    detail?: string
    message?: string
    errors?: Record<string, string[]>
}

export interface SubscriptionPlan {
    key: string
    label: string
    price_cents: number
    currency: string
    duration_seconds: number
}
