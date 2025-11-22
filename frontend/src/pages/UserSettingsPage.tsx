import { useState, useEffect, useRef } from 'react'
import {
    Box,
    Card,
    CardContent,
    Typography,
    Button,
    Switch,
    FormControlLabel,
    Divider,
    Alert,
    CircularProgress,
    Chip,
    Stack,
    Dialog,
    DialogTitle,
    DialogContent,
    DialogActions,
    IconButton,
    Avatar,
    TextField,
} from '@mui/material'
import CloseIcon from '@mui/icons-material/Close'
import CameraAltIcon from '@mui/icons-material/CameraAlt'
import { useAuth } from '../contexts/AuthContext'
import { apiClient, userApiClient, subscriptionService } from '../services/api'
import PurchaseModal from '../components/payments/PurchaseModal'
import PaymentModal from '../components/payments/PaymentModal'
import { SubscriptionPlan } from '../types'

interface NotificationPreferences {
    comment_on_post: boolean
    post_reaction: boolean
    payment_successful: boolean
    payment_failed: boolean
    subscription_activated: boolean
    subscription_expiring: boolean
    subscription_cancelled: boolean
}

interface Subscription {
    status: string
    plan: string
    valid_until: string | null
}

interface Email {
    id: number
    subject: string
    body: string
    from_email: string
    to_email: string
    created_at: string
    read: boolean
}

const UserSettingsPage = () => {
    const { user, refreshUser } = useAuth()
    const [loading, setLoading] = useState(true)
    const [saving, setSaving] = useState(false)
    const [uploadingImage, setUploadingImage] = useState(false)
    const [error, setError] = useState<string | null>(null)
    const [success, setSuccess] = useState<string | null>(null)
    const [subscription, setSubscription] = useState<Subscription | null>(null)
    const [plans, setPlans] = useState<SubscriptionPlan[]>([])
    const [subscriptionDialogOpen, setSubscriptionDialogOpen] = useState(false)
    const [emails, setEmails] = useState<Email[]>([])
    const [selectedEmail, setSelectedEmail] = useState<Email | null>(null)
    const [preferences, setPreferences] = useState<NotificationPreferences>({
        comment_on_post: true,
        post_reaction: true,
        payment_successful: true,
        payment_failed: true,
        subscription_activated: true,
        subscription_expiring: true,
        subscription_cancelled: true,
    })
    const [profileData, setProfileData] = useState({
        first_name: user?.first_name || '',
        last_name: user?.last_name || '',
        bio: user?.bio || '',
        website: user?.website || '',
    })
    const fileInputRef = useRef<HTMLInputElement>(null)

    // Subscription state for PurchaseModal
    const [processingPlan, setProcessingPlan] = useState<string | null>(null)
    const [subscriptionClientSecret, setSubscriptionClientSecret] = useState<
        string | null
    >(null)
    const [subscriptionId, setSubscriptionId] = useState<number | null>(null)
    const [subscriptionAmount, setSubscriptionAmount] = useState<number>(0)
    const [subscriptionAlert, setSubscriptionAlert] = useState<{
        type: 'success' | 'error'
        message: string
    } | null>(null)
    const [paymentModalOpen, setPaymentModalOpen] = useState(false)

    useEffect(() => {
        loadSettings()
    }, [])

    useEffect(() => {
        if (user) {
            setProfileData({
                first_name: user.first_name || '',
                last_name: user.last_name || '',
                bio: user.bio || '',
                website: user.website || '',
            })
        }
    }, [user])

    const loadSettings = async () => {
        setLoading(true)
        setError(null)

        try {
            // Load notification preferences
            const prefsResponse = await userApiClient.get(
                '/notification-preferences/'
            )
            setPreferences(prefsResponse.data)

            // Load current subscription (any status)
            try {
                const subsResponse = await apiClient.get(
                    '/v0/subscriptions/current/'
                )
                if (subsResponse.data) {
                    setSubscription(subsResponse.data)
                }
            } catch (err: any) {
                // No subscription is okay
                if (err.response?.status !== 404) {
                    console.error('Error loading subscription:', err)
                }
            }

            // Load subscription plans
            try {
                const plansResponse = await subscriptionService.getPlans()
                setPlans(
                    Array.isArray(plansResponse.data) ? plansResponse.data : []
                )
            } catch (err: any) {
                console.error('Error loading plans:', err)
            }

            // Load emails
            try {
                const emailsResponse = await apiClient.get('/v0/emails/')
                setEmails(
                    emailsResponse.data.results || emailsResponse.data || []
                )
            } catch (err: any) {
                console.error('Error loading emails:', err)
            }
        } catch (err: any) {
            setError(err.response?.data?.detail || 'Failed to load settings')
        } finally {
            setLoading(false)
        }
    }

    const handlePreferenceChange = (field: keyof NotificationPreferences) => {
        setPreferences((prev) => ({
            ...prev,
            [field]: !prev[field],
        }))
    }

    const savePreferences = async () => {
        setSaving(true)
        setError(null)
        setSuccess(null)

        try {
            const response = await userApiClient.patch(
                '/notification-preferences/',
                preferences
            )
            setPreferences(response.data) // Use the response from PATCH
            setSuccess('Notification preferences saved successfully')
        } catch (err: any) {
            setError(err.response?.data?.detail || 'Failed to save preferences')
        } finally {
            setSaving(false)
        }
    }

    const cancelSubscription = async () => {
        if (!subscription) return
        if (
            !window.confirm(
                'Are you sure you want to cancel your subscription?'
            )
        ) {
            return
        }

        setSaving(true)
        setError(null)
        setSuccess(null)

        try {
            await apiClient.post(`/v0/subscriptions/cancel/`)
            setSuccess('Subscription cancelled successfully')
            setSubscription((prev) =>
                prev
                    ? {
                          ...prev,
                          status: 'canceled',
                      }
                    : prev
            )
            loadSettings() // Reload to get updated status
        } catch (err: any) {
            setError(
                err.response?.data?.detail || 'Failed to cancel subscription'
            )
        } finally {
            setSaving(false)
        }
    }

    const handleSubscribeClick = () => {
        setSubscriptionDialogOpen(true)
    }

    const handleSubscriptionCreate = async (planKey: string) => {
        setProcessingPlan(planKey)
        setSubscriptionAlert(null)
        try {
            const { data } =
                await subscriptionService.createSubscription(planKey)
            if (data.client_secret) {
                setSubscriptionClientSecret(data.client_secret)
                setSubscriptionId(null)
                setSubscriptionAmount(data.amount || 0)
                setSubscriptionDialogOpen(false)
                setPaymentModalOpen(true)
            } else {
                setSubscriptionAlert({
                    type: 'error',
                    message: 'Failed to create subscription. Please try again.',
                })
            }
        } catch (err: any) {
            console.error('Subscription error', err)
            setSubscriptionAlert({
                type: 'error',
                message:
                    err.response?.data?.error ||
                    err.message ||
                    'Unable to start the subscription. Please try again.',
            })
        } finally {
            setProcessingPlan(null)
        }
    }

    const handleSubscriptionPaymentSuccess = async () => {
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
                    message: 'Subscription activated!',
                })
                setSuccess('Subscription activated successfully')
                await loadSettings()
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
        } catch (err: any) {
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

    const handleEmailClick = async (email: Email) => {
        setSelectedEmail(email)

        // Mark as read if not already read
        if (!email.read) {
            try {
                await apiClient.get(`/v0/emails/${email.id}/`)
                // Update local state
                setEmails((prevEmails) =>
                    prevEmails.map((e) =>
                        e.id === email.id ? { ...e, read: true } : e
                    )
                )
            } catch (err) {
                console.error('Error marking email as read:', err)
            }
        }
    }

    const handleCloseEmailDialog = () => {
        setSelectedEmail(null)
    }

    const getPlanLabel = (plan: string) => {
        const labels: { [key: string]: string } = {
            day: 'Daily',
            week: 'Weekly',
            month: 'Monthly',
        }
        return labels[plan] || plan
    }

    const getStatusColor = (status: string) => {
        switch (status) {
            case 'active':
                return 'success'
            case 'canceled':
                return 'default'
            case 'past_due':
                return 'warning'
            default:
                return 'info'
        }
    }

    const handleProfilePictureClick = () => {
        fileInputRef.current?.click()
    }

    const handleProfilePictureChange = async (
        event: React.ChangeEvent<HTMLInputElement>
    ) => {
        const file = event.target.files?.[0]
        if (!file) return

        // Validate file size (5MB limit)
        if (file.size > 5 * 1024 * 1024) {
            setError('Image size must be less than 5MB')
            return
        }

        // Validate file type
        if (!file.type.startsWith('image/')) {
            setError('Please select an image file')
            return
        }

        setUploadingImage(true)
        setError(null)

        try {
            const formData = new FormData()
            formData.append('profile_picture', file)

            await userApiClient.patch('/me/', formData, {
                headers: {
                    'Content-Type': 'multipart/form-data',
                },
            })

            setSuccess('Profile picture updated successfully')
            await refreshUser()
        } catch (err: any) {
            console.error('Error uploading profile picture:', err)
            setError(
                err.response?.data?.profile_picture?.[0] ||
                    'Failed to upload profile picture'
            )
        } finally {
            setUploadingImage(false)
        }
    }

    const handleProfileUpdate = async () => {
        setSaving(true)
        setError(null)

        try {
            await userApiClient.patch('/me/', profileData)
            setSuccess('Profile updated successfully')
            await refreshUser()
        } catch (err: any) {
            console.error('Error updating profile:', err)
            setError(err.response?.data?.detail || 'Failed to update profile')
        } finally {
            setSaving(false)
        }
    }

    if (loading) {
        return (
            <Box display="flex" justifyContent="center" py={8}>
                <CircularProgress />
            </Box>
        )
    }

    return (
        <Box maxWidth="md" mx="auto">
            <Typography variant="h4" gutterBottom>
                User Settings
            </Typography>

            {error && (
                <Alert
                    severity="error"
                    sx={{ mb: 2 }}
                    onClose={() => setError(null)}
                >
                    {error}
                </Alert>
            )}

            {success && (
                <Alert
                    severity="success"
                    sx={{ mb: 2 }}
                    onClose={() => setSuccess(null)}
                >
                    {success}
                </Alert>
            )}

            {/* Profile Picture Section */}
            <Card sx={{ mb: 3 }}>
                <CardContent>
                    <Typography variant="h6" gutterBottom>
                        Profile Picture
                    </Typography>
                    <Box
                        sx={{
                            display: 'flex',
                            alignItems: 'center',
                            gap: 3,
                        }}
                    >
                        <Box sx={{ position: 'relative' }}>
                            <Avatar
                                src={user?.profile_picture || undefined}
                                sx={{
                                    width: 120,
                                    height: 120,
                                    fontSize: '3rem',
                                }}
                            >
                                {user?.first_name?.[0]?.toUpperCase() ||
                                    user?.email?.[0]?.toUpperCase()}
                            </Avatar>
                            {uploadingImage && (
                                <CircularProgress
                                    size={120}
                                    sx={{
                                        position: 'absolute',
                                        top: 0,
                                        left: 0,
                                    }}
                                />
                            )}
                        </Box>
                        <Box>
                            <input
                                ref={fileInputRef}
                                type="file"
                                accept="image/*"
                                onChange={handleProfilePictureChange}
                                style={{ display: 'none' }}
                            />
                            <Button
                                variant="outlined"
                                startIcon={<CameraAltIcon />}
                                onClick={handleProfilePictureClick}
                                disabled={uploadingImage}
                            >
                                {uploadingImage
                                    ? 'Uploading...'
                                    : 'Change Picture'}
                            </Button>
                            <Typography
                                variant="caption"
                                color="text.secondary"
                                sx={{ display: 'block', mt: 1 }}
                            >
                                JPG, PNG or WebP. Max size 5MB.
                            </Typography>
                        </Box>
                    </Box>
                </CardContent>
            </Card>

            {/* Profile Information Section */}
            <Card sx={{ mb: 3 }}>
                <CardContent>
                    <Typography variant="h6" gutterBottom>
                        Profile Information
                    </Typography>
                    <Box
                        sx={{
                            display: 'flex',
                            flexDirection: 'column',
                            gap: 2,
                        }}
                    >
                        <TextField
                            label="First Name"
                            value={profileData.first_name}
                            onChange={(e) =>
                                setProfileData({
                                    ...profileData,
                                    first_name: e.target.value,
                                })
                            }
                            fullWidth
                        />
                        <TextField
                            label="Last Name"
                            value={profileData.last_name}
                            onChange={(e) =>
                                setProfileData({
                                    ...profileData,
                                    last_name: e.target.value,
                                })
                            }
                            fullWidth
                        />
                        <TextField
                            label="Bio"
                            value={profileData.bio}
                            onChange={(e) =>
                                setProfileData({
                                    ...profileData,
                                    bio: e.target.value,
                                })
                            }
                            multiline
                            rows={3}
                            fullWidth
                        />
                        <TextField
                            label="Website"
                            value={profileData.website}
                            onChange={(e) =>
                                setProfileData({
                                    ...profileData,
                                    website: e.target.value,
                                })
                            }
                            fullWidth
                            placeholder="https://example.com"
                        />
                        <Button
                            variant="contained"
                            onClick={handleProfileUpdate}
                            disabled={saving}
                        >
                            {saving ? 'Saving...' : 'Save Changes'}
                        </Button>
                    </Box>
                </CardContent>
            </Card>

            {/* Email Address Section */}
            <Card sx={{ mb: 3 }}>
                <CardContent>
                    <Typography variant="h6" gutterBottom>
                        Email Address
                    </Typography>
                    <Typography variant="body1" color="text.secondary">
                        {user?.email}
                    </Typography>
                    <Typography
                        variant="caption"
                        color="text.secondary"
                        sx={{ mt: 1, display: 'block' }}
                    >
                        Email changes are not currently supported
                    </Typography>
                </CardContent>
            </Card>

            {/* Email History Section */}
            <Card sx={{ mb: 3 }}>
                <CardContent>
                    <Typography variant="h6" gutterBottom>
                        Email History
                    </Typography>
                    <Typography
                        variant="body2"
                        color="text.secondary"
                        sx={{ mb: 2 }}
                    >
                        View notification emails sent to your account
                    </Typography>

                    {emails.length === 0 ? (
                        <Typography variant="body2" color="text.secondary">
                            No emails yet
                        </Typography>
                    ) : (
                        <Box
                            sx={{
                                display: 'flex',
                                flexDirection: 'column',
                                gap: 1,
                            }}
                        >
                            {emails.slice(0, 5).map((email) => (
                                <Box
                                    key={email.id}
                                    sx={{
                                        p: 2,
                                        border: 1,
                                        borderColor: 'divider',
                                        borderRadius: 1,
                                        cursor: 'pointer',
                                        backgroundColor: email.read
                                            ? 'transparent'
                                            : 'action.hover',
                                        '&:hover': {
                                            backgroundColor: 'action.selected',
                                        },
                                    }}
                                    onClick={() => handleEmailClick(email)}
                                >
                                    <Stack
                                        direction="row"
                                        justifyContent="space-between"
                                        alignItems="center"
                                    >
                                        <Box sx={{ flex: 1, minWidth: 0 }}>
                                            <Typography
                                                variant="subtitle2"
                                                sx={{
                                                    fontWeight: email.read
                                                        ? 'normal'
                                                        : 'bold',
                                                    overflow: 'hidden',
                                                    textOverflow: 'ellipsis',
                                                    whiteSpace: 'nowrap',
                                                }}
                                            >
                                                {email.subject}
                                            </Typography>
                                            <Typography
                                                variant="caption"
                                                color="text.secondary"
                                                sx={{
                                                    overflow: 'hidden',
                                                    textOverflow: 'ellipsis',
                                                    whiteSpace: 'nowrap',
                                                    display: 'block',
                                                }}
                                            >
                                                {email.body.substring(0, 100)}
                                                ...
                                            </Typography>
                                        </Box>
                                        <Typography
                                            variant="caption"
                                            color="text.secondary"
                                            sx={{ ml: 2 }}
                                        >
                                            {new Date(
                                                email.created_at
                                            ).toLocaleDateString()}
                                        </Typography>
                                    </Stack>
                                </Box>
                            ))}
                            {emails.length > 5 && (
                                <Typography
                                    variant="caption"
                                    color="text.secondary"
                                    sx={{ mt: 1 }}
                                >
                                    Showing 5 of {emails.length} emails
                                </Typography>
                            )}
                        </Box>
                    )}
                </CardContent>
            </Card>

            {/* Subscription Section */}
            <Card sx={{ mb: 3 }}>
                <CardContent>
                    <Typography variant="h6" gutterBottom>
                        Subscription
                    </Typography>

                    {subscription ? (
                        <Box>
                            <Stack
                                direction="row"
                                spacing={2}
                                alignItems="center"
                                sx={{ mb: 2 }}
                            >
                                <Typography variant="body1">
                                    <strong>Plan:</strong>{' '}
                                    {getPlanLabel(subscription.plan)}
                                </Typography>
                                <Chip
                                    label={subscription.status}
                                    color={getStatusColor(subscription.status)}
                                    size="small"
                                />
                            </Stack>

                            {subscription.valid_until &&
                                subscription.status === 'canceled' && (
                                    <Typography
                                        variant="body2"
                                        color="text.secondary"
                                        sx={{ mb: 2 }}
                                    >
                                        Subscription cancelled. Access remains
                                        until{' '}
                                        {new Date(
                                            subscription.valid_until
                                        ).toLocaleDateString()}
                                        .
                                    </Typography>
                                )}

                            {subscription.valid_until &&
                                subscription.status !== 'canceled' && (
                                    <Typography
                                        variant="body2"
                                        color="text.secondary"
                                        sx={{ mb: 2 }}
                                    >
                                        Valid until:{' '}
                                        {new Date(
                                            subscription.valid_until
                                        ).toLocaleDateString()}
                                    </Typography>
                                )}

                            {subscription.status === 'active' && (
                                <Button
                                    variant="outlined"
                                    color="error"
                                    onClick={cancelSubscription}
                                    disabled={saving}
                                >
                                    Cancel Subscription
                                </Button>
                            )}
                        </Box>
                    ) : (
                        <Box>
                            <Typography
                                variant="body2"
                                color="text.secondary"
                                sx={{ mb: 2 }}
                            >
                                You don't have an active subscription
                            </Typography>
                            <Button
                                variant="contained"
                                color="primary"
                                onClick={handleSubscribeClick}
                            >
                                Subscribe
                            </Button>
                        </Box>
                    )}
                </CardContent>
            </Card>

            {/* Notification Preferences Section */}
            <Card>
                <CardContent>
                    <Typography variant="h6" gutterBottom>
                        Notification Preferences
                    </Typography>
                    <Typography
                        variant="body2"
                        color="text.secondary"
                        sx={{ mb: 2 }}
                    >
                        Choose which email notifications you'd like to receive
                    </Typography>

                    <Box
                        sx={{
                            display: 'flex',
                            flexDirection: 'column',
                            gap: 1,
                        }}
                    >
                        <Typography
                            variant="subtitle2"
                            sx={{ mt: 1, mb: 0.5, fontWeight: 'bold' }}
                        >
                            Blog Interactions
                        </Typography>
                        <FormControlLabel
                            control={
                                <Switch
                                    checked={preferences.comment_on_post}
                                    onChange={() =>
                                        handlePreferenceChange(
                                            'comment_on_post'
                                        )
                                    }
                                />
                            }
                            label="Email me when someone comments on my posts"
                        />
                        <FormControlLabel
                            control={
                                <Switch
                                    checked={preferences.post_reaction}
                                    onChange={() =>
                                        handlePreferenceChange('post_reaction')
                                    }
                                />
                            }
                            label="Email me when someone reacts to my posts"
                        />

                        <Typography
                            variant="subtitle2"
                            sx={{ mt: 2, mb: 0.5, fontWeight: 'bold' }}
                        >
                            Payments
                        </Typography>
                        <FormControlLabel
                            control={
                                <Switch
                                    checked={preferences.payment_successful}
                                    onChange={() =>
                                        handlePreferenceChange(
                                            'payment_successful'
                                        )
                                    }
                                />
                            }
                            label="Email me when a payment is successful"
                        />
                        <FormControlLabel
                            control={
                                <Switch
                                    checked={preferences.payment_failed}
                                    onChange={() =>
                                        handlePreferenceChange('payment_failed')
                                    }
                                />
                            }
                            label="Email me when a payment fails"
                        />

                        <Typography
                            variant="subtitle2"
                            sx={{ mt: 2, mb: 0.5, fontWeight: 'bold' }}
                        >
                            Subscriptions
                        </Typography>
                        <FormControlLabel
                            control={
                                <Switch
                                    checked={preferences.subscription_activated}
                                    onChange={() =>
                                        handlePreferenceChange(
                                            'subscription_activated'
                                        )
                                    }
                                />
                            }
                            label="Email me when my subscription is activated"
                        />
                        <FormControlLabel
                            control={
                                <Switch
                                    checked={preferences.subscription_expiring}
                                    onChange={() =>
                                        handlePreferenceChange(
                                            'subscription_expiring'
                                        )
                                    }
                                />
                            }
                            label="Email me when my subscription is about to expire"
                        />
                        <FormControlLabel
                            control={
                                <Switch
                                    checked={preferences.subscription_cancelled}
                                    onChange={() =>
                                        handlePreferenceChange(
                                            'subscription_cancelled'
                                        )
                                    }
                                />
                            }
                            label="Email me when my subscription is cancelled"
                        />
                    </Box>

                    <Divider sx={{ my: 2 }} />

                    <Button
                        variant="contained"
                        onClick={savePreferences}
                        disabled={saving}
                    >
                        {saving ? 'Saving...' : 'Save Preferences'}
                    </Button>
                </CardContent>
            </Card>

            {/* Email Detail Dialog */}
            <Dialog
                open={selectedEmail !== null}
                onClose={handleCloseEmailDialog}
                maxWidth="md"
                fullWidth
            >
                {selectedEmail && (
                    <>
                        <DialogTitle>
                            <Box
                                sx={{
                                    display: 'flex',
                                    alignItems: 'center',
                                    justifyContent: 'space-between',
                                }}
                            >
                                <Typography variant="h6">
                                    {selectedEmail.subject}
                                </Typography>
                                <IconButton
                                    edge="end"
                                    onClick={handleCloseEmailDialog}
                                    aria-label="close"
                                >
                                    <CloseIcon />
                                </IconButton>
                            </Box>
                        </DialogTitle>
                        <DialogContent dividers>
                            <Box sx={{ mb: 2 }}>
                                <Typography
                                    variant="caption"
                                    color="text.secondary"
                                >
                                    From: {selectedEmail.from_email}
                                </Typography>
                            </Box>
                            <Box sx={{ mb: 2 }}>
                                <Typography
                                    variant="caption"
                                    color="text.secondary"
                                >
                                    To: {selectedEmail.to_email}
                                </Typography>
                            </Box>
                            <Box sx={{ mb: 2 }}>
                                <Typography
                                    variant="caption"
                                    color="text.secondary"
                                >
                                    Date:{' '}
                                    {new Date(
                                        selectedEmail.created_at
                                    ).toLocaleString()}
                                </Typography>
                            </Box>
                            <Divider sx={{ my: 2 }} />
                            <Typography
                                variant="body1"
                                sx={{
                                    whiteSpace: 'pre-wrap',
                                    wordBreak: 'break-word',
                                }}
                            >
                                {selectedEmail.body}
                            </Typography>
                        </DialogContent>
                        <DialogActions>
                            <Button onClick={handleCloseEmailDialog}>
                                Close
                            </Button>
                        </DialogActions>
                    </>
                )}
            </Dialog>

            {/* Subscription Modal */}
            <PurchaseModal
                open={subscriptionDialogOpen}
                onClose={() => {
                    setSubscriptionDialogOpen(false)
                    setSubscriptionClientSecret(null)
                    setSubscriptionId(null)
                    setSubscriptionAmount(0)
                }}
                subscriptionPlans={plans}
                onSubscribe={handleSubscriptionCreate}
                onSubscriptionPaymentSuccess={() => {}}
                onSubscriptionPaymentError={() => {}}
                processingPlan={processingPlan}
                subscriptionAmount={0}
                subscriptionAlert={subscriptionAlert}
            />

            <PaymentModal
                open={paymentModalOpen}
                onClose={() => {
                    setPaymentModalOpen(false)
                    setSubscriptionClientSecret(null)
                    setSubscriptionId(null)
                    setSubscriptionAmount(0)
                }}
                clientSecret={subscriptionClientSecret || ''}
                amount={subscriptionAmount}
                isSubscription
                onSuccess={handleSubscriptionPaymentSuccess}
                onError={handleSubscriptionPaymentError}
                title="Complete Subscription"
                description="Enter your payment details to activate your subscription"
            />
        </Box>
    )
}

export default UserSettingsPage
