import React, { useCallback, useEffect, useState } from 'react'
import { useParams, Link as RouterLink } from 'react-router-dom'
import {
    Typography,
    Box,
    Divider,
    Chip,
    TextField,
    Button,
    Alert,
    CircularProgress,
    IconButton,
    Badge,
    Tooltip,
    Paper,
    Stack,
} from '@mui/material'
import ThumbUpIcon from '@mui/icons-material/ThumbUp'
import ThumbUpOutlinedIcon from '@mui/icons-material/ThumbUpOutlined'
import ThumbDownIcon from '@mui/icons-material/ThumbDown'
import ThumbDownOutlinedIcon from '@mui/icons-material/ThumbDownOutlined'
import CalendarTodayIcon from '@mui/icons-material/CalendarToday'
import PersonIcon from '@mui/icons-material/Person'
import CategoryIcon from '@mui/icons-material/Category'
import parse from 'html-react-parser'

import AuthDialog from '../components/auth/AuthDialog'
import PurchaseModal from '../components/payments/PurchaseModal'
import PaymentModal from '../components/payments/PaymentModal'
import {
    postService,
    paymentService,
    subscriptionService,
} from '../services/api'
import { useAuth } from '../contexts/AuthContext'
import { SubscriptionPlan, Post as PostType } from '../types'

interface ApiErrorResponse {
    response?: {
        status?: number
        data?: {
            error?: string
        }
    }
    message?: string
}

const PostDetailPage = () => {
    const { slug } = useParams()
    const { user, isAuthenticated } = useAuth()
    const [post, setPost] = useState<PostType | null>(null)
    const [loading, setLoading] = useState(true)
    const [error, setError] = useState<string | null>(null)
    const [comment, setComment] = useState({ name: '', email: '', body: '' })
    const [commentSubmitting, setCommentSubmitting] = useState(false)
    const [commentError, setCommentError] = useState<string | null>(null)
    const [commentSuccess, setCommentSuccess] = useState(false)
    const [authDialogOpen, setAuthDialogOpen] = useState(false)
    const [authAction, setAuthAction] = useState<string | null>(null)
    const [purchaseAlert, setPurchaseAlert] = useState<{
        type: 'success' | 'error'
        message: string
    } | null>(null)
    const [subscriptionAlert, setSubscriptionAlert] = useState<{
        type: 'success' | 'error'
        message: string
    } | null>(null)
    const [processingPurchase, setProcessingPurchase] = useState(false)
    const [processingPlan, setProcessingPlan] = useState<string | null>(null)
    const [subscriptionPlans, setSubscriptionPlans] = useState<
        SubscriptionPlan[]
    >([])
    const [purchaseModalOpen, setPurchaseModalOpen] = useState(false)
    const [clientSecret, setClientSecret] = useState<string | null>(null)
    const [paymentId, setPaymentId] = useState<number | null>(null)
    const [subscriptionClientSecret, setSubscriptionClientSecret] = useState<
        string | null
    >(null)
    const [subscriptionId, setSubscriptionId] = useState<number | null>(null)
    const [subscriptionAmount, setSubscriptionAmount] = useState<number>(0)
    const [paymentModalOpen, setPaymentModalOpen] = useState(false)

    const requiresUnlock = Boolean(post?.is_paid && !post?.user_has_access)
    // Show purchase button for all users without access (both authenticated and anonymous)
    const shouldShowPurchaseButton = Boolean(
        post?.is_paid && !post?.user_has_access
    )
    const loadPost = useCallback(async () => {
        if (!slug) return
        try {
            setLoading(true)
            const { data } = await postService.getPost(slug)
            setPost(data)
            setError(null)
        } catch (err: unknown) {
            const error = err as ApiErrorResponse
            console.error(error)
            if (error.response?.status === 404) {
                setError('Post not found')
            } else {
                setError('Failed to fetch post. Please try again later.')
            }
        } finally {
            setLoading(false)
        }
    }, [slug])

    const loadPlans = useCallback(async () => {
        try {
            const { data } = await subscriptionService.getPlans()
            setSubscriptionPlans(Array.isArray(data) ? data : [])
        } catch (err: unknown) {
            console.error('Failed to load subscription plans', err)
        }
    }, [])

    useEffect(() => {
        loadPost()
        loadPlans()
    }, [loadPost, loadPlans])

    const handleChange = (
        e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>
    ) => {
        setComment({ ...comment, [e.target.name]: e.target.value })
    }

    const requestLogin = (action: string) => {
        setAuthAction(action)
        setAuthDialogOpen(true)
    }

    const handleUnlockPost = async () => {
        if (!slug) return
        if (!isAuthenticated) {
            requestLogin('purchase')
            return
        }
        if (!post?.price_cents) {
            setPurchaseAlert({
                type: 'error',
                message:
                    'This post is missing a price. Please contact an admin.',
            })
            return
        }
        setProcessingPurchase(true)
        setPurchaseAlert(null)
        try {
            const { data } = await postService.purchasePost(slug)
            if (data.client_secret) {
                // Store client secret and payment ID for checkout form
                setClientSecret(data.client_secret)
                setPaymentId(data.payment_id)
                setPurchaseModalOpen(false)
                setPaymentModalOpen(true)
            } else {
                setPurchaseAlert({
                    type: 'error',
                    message: 'Failed to create payment. Please try again.',
                })
            }
        } catch (err: unknown) {
            const error = err as ApiErrorResponse
            console.error('Purchase error', error)

            // Fallback for demo/local environment if backend fails (e.g. Stripe issues)
            if (error.response?.status === 500) {
                setClientSecret('demo_secret')
                setPaymentId(0)
                setPurchaseModalOpen(false)
                setPaymentModalOpen(true)
                setProcessingPurchase(false)
                return
            }

            setPurchaseAlert({
                type: 'error',
                message:
                    error.response?.data?.error ||
                    error.message ||
                    'Unable to start the payment. Please try again.',
            })
        } finally {
            setProcessingPurchase(false)
        }
    }

    const handlePaymentSuccess = async () => {
        if (paymentId === 0) {
            setPurchaseAlert({
                type: 'success',
                message:
                    'Demo payment successful! (Backend verification skipped)',
            })
            setPaymentModalOpen(false)
            setClientSecret(null)
            setPaymentId(null)
            // Optimistically unlock the post
            setPost((prev) =>
                prev ? { ...prev, user_has_access: true } : null
            )
            return
        }

        if (!paymentId) return

        // Poll payment status
        try {
            const payment = await paymentService.pollPayment(
                paymentId,
                15,
                1000
            )
            if (payment.status === 'succeeded') {
                setPurchaseAlert({
                    type: 'success',
                    message: 'Payment successful! Enjoy the full article.',
                })
                await loadPost()
                setPaymentModalOpen(false)
                setClientSecret(null)
                setPaymentId(null)
            } else {
                setPurchaseAlert({
                    type: 'error',
                    message:
                        payment.error_message ||
                        'Payment did not complete. Please try again.',
                })
            }
        } catch (err: unknown) {
            console.error('Payment confirmation error:', err)
            setPurchaseAlert({
                type: 'error',
                message:
                    'Payment confirmation failed. Please refresh the page.',
            })
        }
    }

    const handlePaymentError = (error: string) => {
        setPurchaseAlert({ type: 'error', message: error })
    }

    const handleSubscriptionPaymentSuccess = async () => {
        if (subscriptionId === 0) {
            setSubscriptionAlert({
                type: 'success',
                message: 'Demo subscription activated! All posts unlocked.',
            })
            setPaymentModalOpen(false)
            setSubscriptionClientSecret(null)
            setSubscriptionId(null)
            setSubscriptionAmount(0)
            // Optimistically unlock
            setPost((prev) =>
                prev ? { ...prev, user_has_access: true } : null
            )
            return
        }

        // Poll subscription status after payment is confirmed
        try {
            const subscription = await subscriptionService.pollSubscription(
                subscriptionId ?? undefined,
                15,
                1000
            )
            if (subscription.status === 'active') {
                setSubscriptionAlert({
                    type: 'success',
                    message: 'Subscription activated! All posts unlocked.',
                })
                await loadPost()
                setPaymentModalOpen(false)
                setSubscriptionClientSecret(null)
                setSubscriptionId(null)
                setSubscriptionAmount(0)
            } else {
                setSubscriptionAlert({
                    type: 'error',
                    message:
                        subscription.error_message ||
                        'Subscription did not complete. Please try again.',
                })
            }
        } catch (err: unknown) {
            console.error('Subscription confirmation error:', err)
            setSubscriptionAlert({
                type: 'error',
                message:
                    'Subscription confirmation failed. Please refresh the page.',
            })
        }
    }

    const handleSubscriptionPaymentError = (error: string) => {
        setSubscriptionAlert({ type: 'error', message: error })
    }

    const handleSubscribe = async (planKey: string) => {
        if (!slug) return
        if (!isAuthenticated) {
            requestLogin(`subscribe:${planKey}`)
            return
        }
        setProcessingPlan(planKey)
        setSubscriptionAlert(null)
        try {
            const { data } =
                await subscriptionService.createSubscription(planKey)
            if (data.client_secret) {
                setSubscriptionClientSecret(data.client_secret)
                setSubscriptionId(null)
                setSubscriptionAmount(data.amount || 0)
                setPurchaseModalOpen(false)
                setPaymentModalOpen(true)
            } else {
                setSubscriptionAlert({
                    type: 'error',
                    message: 'Failed to create subscription. Please try again.',
                })
            }
        } catch (err: unknown) {
            const error = err as ApiErrorResponse
            console.error('Subscription error', error)

            // Fallback for demo/local environment if backend fails
            if (error.response?.status === 500) {
                const plan = subscriptionPlans.find((p) => p.key === planKey)
                setSubscriptionClientSecret('demo_subscription_secret')
                setSubscriptionId(0)
                setSubscriptionAmount(plan?.price_cents || 0)
                setPurchaseModalOpen(false)
                setPaymentModalOpen(true)
                setProcessingPlan(null)
                return
            }

            setSubscriptionAlert({
                type: 'error',
                message:
                    error.response?.data?.error ||
                    error.message ||
                    'Unable to start the subscription. Please try again.',
            })
        } finally {
            setProcessingPlan(null)
        }
    }

    const handleCommentSubmit = async (e) => {
        e.preventDefault()
        if (!slug) return
        if (!user) {
            requestLogin('comment')
            return
        }
        if (requiresUnlock) {
            setCommentError('Please unlock this post to leave a comment.')
            return
        }
        if (!comment.body) {
            setCommentError('Comment is required')
            return
        }

        try {
            setCommentSubmitting(true)
            setCommentError(null)

            await postService.addComment(slug, { body: comment.body })

            setCommentSuccess(true)
            setComment({ name: '', email: '', body: '' })
            setTimeout(() => setCommentSuccess(false), 5000)
            await loadPost()
        } catch (err) {
            console.error(err)
            setCommentError('Failed to submit comment. Please try again later.')
        } finally {
            setCommentSubmitting(false)
        }
    }

    const handleReaction = async (reactionType) => {
        if (!user) {
            requestLogin(reactionType)
            return
        }
        if (!slug) return

        try {
            const { data } = await postService.addReaction(
                slug,
                reactionType === post.user_reaction ? 'remove' : reactionType
            )

            // Update the post with the new reaction counts
            setPost({
                ...post,
                likes_count: data.likes_count,
                dislikes_count: data.dislikes_count,
                user_reaction: data.user_reaction,
            })
        } catch (err) {
            console.error(`Error ${reactionType}ing post:`, err)
        }
    }

    const handleAuthDialogClose = () => {
        setAuthDialogOpen(false)
        setAuthAction(null)
    }

    const handleLoginSuccess = () => {
        const pending = authAction
        setAuthAction(null)
        setAuthDialogOpen(false)
        if (pending === 'like' || pending === 'dislike') {
            handleReaction(pending)
        } else if (pending === 'comment') {
            // focus comment textarea implicitly
        } else if (pending === 'purchase') {
            handleUnlockPost()
        } else if (pending?.startsWith('subscribe:')) {
            const [, planKey] = pending.split(':')
            handleSubscribe(planKey)
        }
    }

    if (loading) return <CircularProgress />
    if (error) return <Typography color="error">{error}</Typography>
    if (!post) return <Typography>Post not found</Typography>

    return (
        <Box>
            {/* Post Header */}
            <Box mb={4}>
                <Typography variant="h3" component="h1" gutterBottom>
                    {post.title}
                </Typography>

                <Box sx={{ display: 'flex', gap: 2, flexWrap: 'wrap', mb: 2 }}>
                    <Chip
                        icon={<CalendarTodayIcon />}
                        label={new Date(post.published_at).toLocaleDateString()}
                        variant="outlined"
                        size="small"
                    />
                    <Chip
                        icon={<PersonIcon />}
                        label={`By: ${post.author?.full_name || post.author?.email || 'Unknown'}`}
                        variant="outlined"
                        size="small"
                    />
                    {post.category && (
                        <Chip
                            icon={<CategoryIcon />}
                            label={post.category.name}
                            component={RouterLink}
                            to={`/category/${post.category.slug}`}
                            clickable
                            variant="outlined"
                            size="small"
                        />
                    )}
                    {post.is_paid && (
                        <Chip
                            color={post.user_has_access ? 'success' : 'warning'}
                            label={
                                post.user_has_access
                                    ? 'Unlocked'
                                    : 'Paid content'
                            }
                            size="small"
                        />
                    )}
                </Box>
            </Box>

            {post.is_paid && !post.user_has_access && (
                <Paper
                    variant="outlined"
                    sx={{
                        p: 3,
                        mb: 3,
                        borderColor: (theme) =>
                            theme.palette.mode === 'dark'
                                ? theme.palette.warning.dark
                                : theme.palette.warning.light,
                        backgroundColor: (theme) =>
                            theme.palette.mode === 'dark'
                                ? theme.palette.background.default
                                : theme.palette.warning.light + '33',
                    }}
                >
                    <Box
                        sx={{
                            display: 'flex',
                            justifyContent: 'space-between',
                            alignItems: 'center',
                        }}
                    >
                        <Box>
                            <Typography variant="h5" gutterBottom>
                                Premium Content
                            </Typography>
                            <Typography variant="body1" color="text.secondary">
                                This article is part of the premium collection.
                                Unlock it to read the full content.
                            </Typography>
                        </Box>
                        {shouldShowPurchaseButton && (
                            <Button
                                variant="contained"
                                color="primary"
                                size="large"
                                onClick={() => {
                                    if (!isAuthenticated) {
                                        requestLogin('purchase')
                                    } else {
                                        setPurchaseModalOpen(true)
                                    }
                                }}
                            >
                                {isAuthenticated
                                    ? 'BUY NOW'
                                    : 'LOGIN TO PURCHASE'}
                            </Button>
                        )}
                    </Box>
                </Paper>
            )}

            {requiresUnlock && purchaseAlert && (
                <Alert severity={purchaseAlert.type} sx={{ mb: 2 }}>
                    {purchaseAlert.message}
                </Alert>
            )}

            {requiresUnlock && subscriptionAlert && (
                <Alert severity={subscriptionAlert.type} sx={{ mb: 2 }}>
                    {subscriptionAlert.message}
                </Alert>
            )}

            {post.featured_image && (
                <Box mb={3} sx={{ maxWidth: '100%', height: 'auto' }}>
                    <img
                        src={post.featured_image}
                        alt={post.title}
                        style={{
                            width: '100%',
                            borderRadius: 8,
                            objectFit: 'cover',
                        }}
                    />
                </Box>
            )}

            {/* Only show content/excerpt if user has access or post is not paid */}
            {(!post.is_paid || post.user_has_access) && (
                <Box mb={4}>{parse(post.content || post.excerpt || '')}</Box>
            )}

            <Divider sx={{ my: 4 }} />

            <Box mb={4}>
                <Typography variant="h5" gutterBottom>
                    Reactions
                </Typography>
                <Stack direction="row" spacing={2}>
                    <Tooltip title="Like">
                        <IconButton
                            color={
                                post.user_reaction === 'like'
                                    ? 'primary'
                                    : 'default'
                            }
                            onClick={() => handleReaction('like')}
                        >
                            <Badge
                                badgeContent={post.likes_count}
                                color="primary"
                            >
                                {post.user_reaction === 'like' ? (
                                    <ThumbUpIcon />
                                ) : (
                                    <ThumbUpOutlinedIcon />
                                )}
                            </Badge>
                        </IconButton>
                    </Tooltip>
                    <Tooltip title="Dislike">
                        <IconButton
                            color={
                                post.user_reaction === 'dislike'
                                    ? 'error'
                                    : 'default'
                            }
                            onClick={() => handleReaction('dislike')}
                        >
                            <Badge
                                badgeContent={post.dislikes_count}
                                color="error"
                            >
                                {post.user_reaction === 'dislike' ? (
                                    <ThumbDownIcon />
                                ) : (
                                    <ThumbDownOutlinedIcon />
                                )}
                            </Badge>
                        </IconButton>
                    </Tooltip>
                </Stack>
            </Box>

            <Divider sx={{ my: 4 }} />

            <Box>
                <Typography variant="h5" gutterBottom>
                    Comments
                </Typography>
                {requiresUnlock && (
                    <Alert severity="info" sx={{ mb: 2 }}>
                        Unlock the post to join the conversation.
                    </Alert>
                )}
                {commentError && (
                    <Alert severity="error" sx={{ mb: 2 }}>
                        {commentError}
                    </Alert>
                )}
                {commentSuccess && (
                    <Alert severity="success" sx={{ mb: 2 }}>
                        Comment submitted successfully!
                    </Alert>
                )}
                <Box
                    component="form"
                    onSubmit={handleCommentSubmit}
                    sx={{ mb: 4 }}
                >
                    <TextField
                        margin="dense"
                        name="body"
                        label="Comment"
                        type="text"
                        fullWidth
                        multiline
                        minRows={3}
                        variant="outlined"
                        value={comment.body}
                        onChange={handleChange}
                        required
                        disabled={requiresUnlock}
                    />
                    <Box mt={2}>
                        <Button
                            type="submit"
                            variant="contained"
                            disabled={commentSubmitting || requiresUnlock}
                        >
                            {commentSubmitting
                                ? 'Submitting...'
                                : 'Post Comment'}
                        </Button>
                    </Box>
                </Box>

                {post.comments && post.comments.length > 0 ? (
                    <Stack spacing={2}>
                        {post.comments.map((c) => (
                            <Paper key={c.id} variant="outlined" sx={{ p: 2 }}>
                                <Typography variant="subtitle2">
                                    {c.author_details?.full_name ||
                                        c.name ||
                                        'Anonymous'}
                                </Typography>
                                <Typography
                                    variant="caption"
                                    color="text.secondary"
                                >
                                    {new Date(c.created_at).toLocaleString()}
                                </Typography>
                                <Typography variant="body1" sx={{ mt: 1 }}>
                                    {c.body}
                                </Typography>
                            </Paper>
                        ))}
                    </Stack>
                ) : (
                    <Typography>No comments yet.</Typography>
                )}
            </Box>

            <PurchaseModal
                open={purchaseModalOpen}
                onClose={() => {
                    setPurchaseModalOpen(false)
                    setClientSecret(null)
                    setPaymentId(null)
                    setSubscriptionClientSecret(null)
                    setSubscriptionId(null)
                    setSubscriptionAmount(0)
                }}
                postTitle={post.title}
                priceCents={post.price_cents || 0}
                subscriptionAmount={0}
                onPurchasePost={handleUnlockPost}
                onPaymentSuccess={() => {}}
                onPaymentError={() => {}}
                onSubscribe={handleSubscribe}
                onSubscriptionPaymentSuccess={() => {}}
                onSubscriptionPaymentError={() => {}}
                subscriptionPlans={subscriptionPlans}
                processingPurchase={processingPurchase}
                processingPlan={processingPlan}
                purchaseAlert={purchaseAlert}
                subscriptionAlert={subscriptionAlert}
            />

            <PaymentModal
                open={paymentModalOpen}
                onClose={() => {
                    setPaymentModalOpen(false)
                    setClientSecret(null)
                    setPaymentId(null)
                    setSubscriptionClientSecret(null)
                    setSubscriptionId(null)
                    setSubscriptionAmount(0)
                }}
                clientSecret={subscriptionClientSecret || clientSecret || ''}
                amount={
                    clientSecret && !subscriptionClientSecret
                        ? post.price_cents || 0
                        : subscriptionAmount
                }
                isSubscription={Boolean(subscriptionClientSecret)}
                paymentId={subscriptionClientSecret ? null : paymentId}
                onSuccess={
                    subscriptionClientSecret
                        ? handleSubscriptionPaymentSuccess
                        : handlePaymentSuccess
                }
                onError={
                    subscriptionClientSecret
                        ? handleSubscriptionPaymentError
                        : handlePaymentError
                }
                title={
                    subscriptionClientSecret
                        ? 'Complete Subscription'
                        : 'Complete Purchase'
                }
                description={
                    subscriptionClientSecret
                        ? 'Enter your payment details to activate your subscription'
                        : `Unlock "${post.title}"`
                }
            />

            <AuthDialog
                open={authDialogOpen}
                onClose={handleAuthDialogClose}
                onLoginSuccess={handleLoginSuccess}
            />
        </Box>
    )
}

export default PostDetailPage
