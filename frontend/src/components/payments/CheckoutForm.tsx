import React, { useState } from 'react'
import {
    Box,
    TextField,
    Button,
    Typography,
    Alert,
    Paper,
    Grid,
    CircularProgress,
} from '@mui/material'
import CreditCardIcon from '@mui/icons-material/CreditCard'
import { subscriptionService, paymentService } from '../../services/api'

interface CheckoutFormProps {
    clientSecret: string
    amount: number
    onSuccess: () => void
    onError: (error: string) => void
    isSubscription?: boolean
    paymentId?: number | null
}

const TEST_CARDS = [
    {
        label: 'Success',
        number: '4242424242424242',
        description: 'Payment succeeds',
    },
    {
        label: 'Decline',
        number: '4000000000009995',
        description: 'Card declined (insufficient funds)',
    },
    {
        label: '3D Secure',
        number: '4000002760003184',
        description: 'Requires authentication',
    },
]

const CheckoutForm: React.FC<CheckoutFormProps> = ({
    clientSecret,
    amount,
    onSuccess,
    onError,
    isSubscription = false,
    paymentId = null,
}) => {
    const [processing, setProcessing] = useState(false)
    const [cardNumber, setCardNumber] = useState('')
    const [expiry, setExpiry] = useState('')
    const [cvc, setCvc] = useState('')
    const [zip, setZip] = useState('')

    const formatCardNumber = (value: string) => {
        const cleaned = value.replace(/\s/g, '')
        const matches = cleaned.match(/.{1,4}/g)
        return matches ? matches.join(' ') : cleaned
    }

    const formatExpiry = (value: string) => {
        const cleaned = value.replace(/\D/g, '')
        if (cleaned.length >= 2) {
            return cleaned.slice(0, 2) + '/' + cleaned.slice(2, 4)
        }
        return cleaned
    }

    const handleCardNumberChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        const value = e.target.value.replace(/\s/g, '')
        if (value.length <= 16 && /^\d*$/.test(value)) {
            setCardNumber(formatCardNumber(value))
        }
    }

    const handleExpiryChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        const value = e.target.value.replace(/\D/g, '')
        if (value.length <= 4) {
            setExpiry(formatExpiry(value))
        }
    }

    const handleCvcChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        const value = e.target.value
        if (value.length <= 3 && /^\d*$/.test(value)) {
            setCvc(value)
        }
    }

    const handleZipChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        const value = e.target.value
        if (value.length <= 5 && /^\d*$/.test(value)) {
            setZip(value)
        }
    }

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault()
        setProcessing(true)

        const cleanCardNumber = cardNumber.replace(/\s/g, '')

        // Validate
        if (cleanCardNumber.length !== 16) {
            onError('Card number must be 16 digits')
            setProcessing(false)
            return
        }
        if (expiry.length !== 5) {
            onError('Invalid expiry date (MM/YY)')
            setProcessing(false)
            return
        }
        if (cvc.length !== 3) {
            onError('CVC must be 3 digits')
            setProcessing(false)
            return
        }
        if (zip.length !== 5) {
            onError('ZIP code must be 5 digits')
            setProcessing(false)
            return
        }

        // Check test card scenarios first
        if (cleanCardNumber === '4000000000009995') {
            onError('Your card was declined (insufficient funds)')
            setProcessing(false)
            return
        }

        if (!cleanCardNumber.startsWith('4')) {
            onError('Invalid card number')
            setProcessing(false)
            return
        }

        // For subscriptions, call the confirm endpoint to simulate Stripe confirmation
        try {
            if (isSubscription) {
                await subscriptionService.confirmSubscription()
            } else if (paymentId) {
                await paymentService.confirmPayment(paymentId)
            }

            // Simulate payment processing delay
            await new Promise((resolve) => setTimeout(resolve, 1500))
            onSuccess()
        } catch (err: any) {
            console.error('Payment confirmation error:', err)
            onError(
                err.response?.data?.error ||
                    'Payment confirmation failed. Please try again.'
            )
        } finally {
            setProcessing(false)
        }
    }

    const fillTestCard = (cardNumber: string) => {
        setCardNumber(formatCardNumber(cardNumber))
        setExpiry('12/28')
        setCvc('123')
        setZip('12345')
    }

    return (
        <Box>
            <Paper
                variant="outlined"
                sx={{
                    p: 2,
                    mb: 3,
                    bgcolor: 'info.50',
                    borderColor: 'info.main',
                }}
            >
                <Typography
                    variant="subtitle2"
                    color="info.main"
                    gutterBottom
                    sx={{ display: 'flex', alignItems: 'center', gap: 1 }}
                >
                    <CreditCardIcon fontSize="small" />
                    Test Card Numbers (Click to use)
                </Typography>
                <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
                    {TEST_CARDS.map((card) => (
                        <Button
                            key={card.number}
                            variant="outlined"
                            size="small"
                            onClick={() => fillTestCard(card.number)}
                            sx={{
                                justifyContent: 'flex-start',
                                textTransform: 'none',
                            }}
                        >
                            <Box sx={{ textAlign: 'left', width: '100%' }}>
                                <Typography
                                    variant="body2"
                                    sx={{ fontFamily: 'monospace' }}
                                >
                                    {formatCardNumber(card.number)}
                                </Typography>
                                <Typography
                                    variant="caption"
                                    color="text.secondary"
                                >
                                    {card.description}
                                </Typography>
                            </Box>
                        </Button>
                    ))}
                </Box>
                <Typography
                    variant="caption"
                    color="text.secondary"
                    sx={{ mt: 1, display: 'block' }}
                >
                    Use any future expiry (MM/YY), 3-digit CVC, and 5-digit ZIP
                </Typography>
            </Paper>

            <form onSubmit={handleSubmit}>
                <Grid container spacing={2}>
                    <Grid item xs={12}>
                        <TextField
                            fullWidth
                            label="Card Number"
                            value={cardNumber}
                            onChange={handleCardNumberChange}
                            placeholder="1234 5678 9012 3456"
                            required
                            disabled={processing}
                            inputProps={{ maxLength: 19 }}
                        />
                    </Grid>
                    <Grid item xs={6}>
                        <TextField
                            fullWidth
                            label="Expiry (MM/YY)"
                            value={expiry}
                            onChange={handleExpiryChange}
                            placeholder="12/28"
                            required
                            disabled={processing}
                            inputProps={{ maxLength: 5 }}
                        />
                    </Grid>
                    <Grid item xs={6}>
                        <TextField
                            fullWidth
                            label="CVC"
                            value={cvc}
                            onChange={handleCvcChange}
                            placeholder="123"
                            required
                            disabled={processing}
                            inputProps={{ maxLength: 3 }}
                        />
                    </Grid>
                    <Grid item xs={12}>
                        <TextField
                            fullWidth
                            label="ZIP Code"
                            value={zip}
                            onChange={handleZipChange}
                            placeholder="12345"
                            required
                            disabled={processing}
                            inputProps={{ maxLength: 5 }}
                        />
                    </Grid>
                    <Grid item xs={12}>
                        <Alert
                            severity="error"
                            sx={{ mb: 2, fontWeight: 'bold' }}
                        >
                            This is a demo environment. Never use real payment
                            information.
                        </Alert>
                        <Button
                            type="submit"
                            variant="contained"
                            color="primary"
                            size="large"
                            fullWidth
                            disabled={processing}
                            startIcon={
                                processing ? (
                                    <CircularProgress size={20} />
                                ) : null
                            }
                        >
                            {processing
                                ? 'Processing...'
                                : `Pay $${(amount / 100).toFixed(2)}`}
                        </Button>
                    </Grid>
                </Grid>
            </form>
        </Box>
    )
}

export default CheckoutForm
