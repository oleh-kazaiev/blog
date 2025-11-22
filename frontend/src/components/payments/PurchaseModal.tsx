import React, { useState } from 'react'
import {
    Dialog,
    DialogTitle,
    DialogContent,
    Box,
    Tabs,
    Tab,
    Typography,
    Button,
    Card,
    CardContent,
    CardActions,
    Stack,
    CircularProgress,
    Alert,
} from '@mui/material'
import LockOpenIcon from '@mui/icons-material/LockOpen'
import SubscriptionsIcon from '@mui/icons-material/Subscriptions'
import { SubscriptionPlan } from '../../types'

interface TabPanelProps {
    children?: React.ReactNode
    index: number
    value: number
}

function TabPanel(props: TabPanelProps) {
    const { children, value, index, ...other } = props

    return (
        <div
            role="tabpanel"
            hidden={value !== index}
            id={`purchase-tabpanel-${index}`}
            aria-labelledby={`purchase-tab-${index}`}
            {...other}
        >
            {value === index && <Box sx={{ pt: 3 }}>{children}</Box>}
        </div>
    )
}

interface PurchaseModalProps {
    open: boolean
    onClose: () => void
    postTitle?: string
    priceCents?: number
    subscriptionAmount: number
    onPaymentSuccess?: () => void
    onPaymentError?: (error: string) => void
    onSubscriptionPaymentSuccess: () => void
    onSubscriptionPaymentError: (error: string) => void
    // Active props
    onPurchasePost?: () => void
    onSubscribe: (planKey: string) => void
    subscriptionPlans: SubscriptionPlan[]
    processingPurchase?: boolean
    processingPlan: string | null
    purchaseAlert?: { type: 'success' | 'error'; message: string } | null
    subscriptionAlert?: { type: 'success' | 'error'; message: string } | null
}

const formatPrice = (cents: number) => {
    return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: 'USD',
    }).format(cents / 100)
}

const formatDuration = (seconds: number) => {
    if (seconds === 86400) return '1 day'
    if (seconds === 604800) return '1 week'
    if (seconds >= 2592000) return '1 month'
    const days = Math.round(seconds / 86400)
    return `${days} day${days === 1 ? '' : 's'}`
}

const PurchaseModal: React.FC<PurchaseModalProps> = ({
    open,
    onClose,
    postTitle,
    priceCents,
    onPurchasePost,
    onSubscribe,
    subscriptionPlans,
    processingPurchase = false,
    processingPlan,
    purchaseAlert,
    subscriptionAlert,
}) => {
    const showPostPurchase = !!postTitle && priceCents !== undefined
    const [activeTab, setActiveTab] = useState(showPostPurchase ? 0 : 1)

    // Reset tab when opening/closing or when mode changes
    React.useEffect(() => {
        if (open) {
            setActiveTab(showPostPurchase ? 0 : 1)
        }
    }, [open, showPostPurchase])

    const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
        setActiveTab(newValue)
    }

    return (
        <Dialog open={open} onClose={onClose} maxWidth="md" fullWidth>
            <DialogTitle>Unlock Premium Content</DialogTitle>
            <DialogContent>
                {showPostPurchase && (
                    <Box sx={{ borderBottom: 1, borderColor: 'divider' }}>
                        <Tabs
                            value={activeTab}
                            onChange={handleTabChange}
                            aria-label="purchase options"
                        >
                            <Tab
                                icon={<LockOpenIcon />}
                                label="Buy This Post"
                                iconPosition="start"
                            />
                            <Tab
                                icon={<SubscriptionsIcon />}
                                label="Subscribe"
                                iconPosition="start"
                            />
                        </Tabs>
                    </Box>
                )}

                {showPostPurchase && (
                    <TabPanel value={activeTab} index={0}>
                        {purchaseAlert && (
                            <Alert severity={purchaseAlert.type} sx={{ mb: 2 }}>
                                {purchaseAlert.message}
                            </Alert>
                        )}

                        <Card variant="outlined" sx={{ bgcolor: 'primary.50' }}>
                            <CardContent>
                                <Typography variant="h6" gutterBottom>
                                    One-time Access
                                </Typography>
                                <Typography
                                    variant="h3"
                                    color="primary"
                                    gutterBottom
                                >
                                    {formatPrice(priceCents!)}
                                </Typography>
                                <Typography
                                    variant="body1"
                                    color="text.secondary"
                                    gutterBottom
                                >
                                    Unlock this post permanently. Perfect if you
                                    only need this article.
                                </Typography>
                                <Typography
                                    variant="subtitle2"
                                    color="text.secondary"
                                    sx={{ mt: 2 }}
                                >
                                    <strong>Post:</strong> {postTitle}
                                </Typography>
                            </CardContent>
                            <CardActions sx={{ px: 3, pb: 3 }}>
                                <Button
                                    variant="contained"
                                    color="primary"
                                    size="large"
                                    fullWidth
                                    onClick={onPurchasePost}
                                    disabled={processingPurchase}
                                    startIcon={
                                        processingPurchase ? (
                                            <CircularProgress size={20} />
                                        ) : null
                                    }
                                >
                                    {processingPurchase
                                        ? 'Processing...'
                                        : 'CONTINUE TO CHECKOUT'}
                                </Button>
                            </CardActions>
                        </Card>
                    </TabPanel>
                )}

                <TabPanel value={activeTab} index={showPostPurchase ? 1 : 1}>
                    {subscriptionAlert && (
                        <Alert severity={subscriptionAlert.type} sx={{ mb: 2 }}>
                            {subscriptionAlert.message}
                        </Alert>
                    )}

                    <Stack spacing={2}>
                        {subscriptionPlans.map((plan) => (
                            <Card key={plan.key} variant="outlined">
                                <CardContent>
                                    <Typography variant="h6" gutterBottom>
                                        {plan.label}
                                    </Typography>
                                    <Typography
                                        variant="h3"
                                        color="primary"
                                        gutterBottom
                                    >
                                        {formatPrice(plan.price_cents)}
                                    </Typography>
                                    <Typography
                                        variant="body2"
                                        color="text.secondary"
                                    >
                                        Access every premium post for{' '}
                                        {formatDuration(plan.duration_seconds)}.
                                    </Typography>
                                </CardContent>
                                <CardActions sx={{ px: 3, pb: 3 }}>
                                    <Button
                                        variant="contained"
                                        color="secondary"
                                        size="large"
                                        fullWidth
                                        onClick={() => onSubscribe(plan.key)}
                                        disabled={processingPlan === plan.key}
                                        startIcon={
                                            processingPlan === plan.key ? (
                                                <CircularProgress size={20} />
                                            ) : null
                                        }
                                    >
                                        {processingPlan === plan.key
                                            ? 'Starting...'
                                            : `SUBSCRIBE (${formatDuration(plan.duration_seconds).toUpperCase()})`}
                                    </Button>
                                </CardActions>
                            </Card>
                        ))}
                    </Stack>
                </TabPanel>
            </DialogContent>
        </Dialog>
    )
}

export default PurchaseModal
