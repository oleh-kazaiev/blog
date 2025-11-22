import React from 'react'
import { Card, CardHeader, CardContent, Typography, Box } from '@mui/material'
import InfoIcon from '@mui/icons-material/Info'

const TestCardList: React.FC = () => {
    return (
        <Card
            variant="outlined"
            sx={{ bgcolor: 'info.50', borderColor: 'info.main' }}
        >
            <CardHeader
                avatar={<InfoIcon color="info" />}
                title="Test Payment Information"
                titleTypographyProps={{ variant: 'h6' }}
            />
            <CardContent>
                <Typography variant="body1" gutterBottom>
                    You will be redirected to a secure checkout page where you
                    can complete your purchase.
                </Typography>
                <Box
                    sx={{
                        mt: 2,
                        p: 2,
                        bgcolor: 'background.paper',
                        borderRadius: 1,
                        border: '1px solid',
                        borderColor: 'divider',
                    }}
                >
                    <Typography
                        variant="subtitle2"
                        color="primary"
                        gutterBottom
                    >
                        <strong>Test Card Numbers:</strong>
                    </Typography>
                    <Typography variant="body2" component="div">
                        <ul style={{ margin: 0, paddingLeft: '20px' }}>
                            <li>
                                <strong>Success:</strong> 4242 4242 4242 4242
                            </li>
                            <li>
                                <strong>Requires authentication:</strong> 4000
                                0027 6000 3184
                            </li>
                            <li>
                                <strong>Insufficient funds:</strong> 4000 0000
                                0000 9995
                            </li>
                        </ul>
                    </Typography>
                    <Typography
                        variant="caption"
                        color="text.secondary"
                        sx={{ mt: 1, display: 'block' }}
                    >
                        Use any future expiration date, any 3-digit CVC, and any
                        5-digit ZIP code.
                    </Typography>
                </Box>
                <Typography
                    variant="caption"
                    color="warning.main"
                    sx={{ mt: 2, display: 'block', fontWeight: 'bold' }}
                >
                    ⚠️ This is a demo environment. Never use real payment
                    information.
                </Typography>
            </CardContent>
        </Card>
    )
}

export default TestCardList
