import React from 'react'
import {
    Dialog,
    DialogTitle,
    DialogContent,
    IconButton,
    Box,
    Typography,
} from '@mui/material'
import CloseIcon from '@mui/icons-material/Close'
import CheckoutForm from './CheckoutForm'

interface PaymentModalProps {
    open: boolean
    onClose: () => void
    clientSecret: string
    amount: number
    onSuccess: () => void
    onError: (error: string) => void
    isSubscription?: boolean
    paymentId?: number | null
    title?: string
    description?: string
}

const PaymentModal: React.FC<PaymentModalProps> = ({
    open,
    onClose,
    clientSecret,
    amount,
    onSuccess,
    onError,
    isSubscription = false,
    paymentId = null,
    title = 'Complete Payment',
    description = 'Enter your payment details below',
}) => {
    return (
        <Dialog open={open} onClose={onClose} maxWidth="sm" fullWidth>
            <DialogTitle>
                <Box
                    sx={{
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'space-between',
                    }}
                >
                    <Typography variant="h6">{title}</Typography>
                    <IconButton edge="end" onClick={onClose} aria-label="close">
                        <CloseIcon />
                    </IconButton>
                </Box>
            </DialogTitle>
            <DialogContent dividers>
                <Typography
                    variant="body2"
                    color="text.secondary"
                    gutterBottom
                    sx={{ mb: 3 }}
                >
                    {description}
                </Typography>
                <CheckoutForm
                    clientSecret={clientSecret}
                    amount={amount}
                    onSuccess={onSuccess}
                    onError={onError}
                    isSubscription={isSubscription}
                    paymentId={paymentId}
                />
            </DialogContent>
        </Dialog>
    )
}

export default PaymentModal
