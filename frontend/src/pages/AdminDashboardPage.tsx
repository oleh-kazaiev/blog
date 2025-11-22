import {
    Box,
    Button,
    Card,
    CardContent,
    Grid,
    Stack,
    Typography,
} from '@mui/material'
import { Link as RouterLink } from 'react-router-dom'

const ManageDashboardPage = () => {
    return (
        <Box sx={{ maxWidth: 1100, mx: 'auto' }}>
            <Typography variant="h4" gutterBottom>
                Manage Posts
            </Typography>
            <Typography variant="body1" color="text.secondary" sx={{ mb: 3 }}>
                Quick actions and basic stats for your blog.
            </Typography>

            <Stack
                direction={{ xs: 'column', sm: 'row' }}
                spacing={2}
                sx={{ mb: 3 }}
            >
                <Button
                    component={RouterLink}
                    to="/admin/posts/new"
                    variant="contained"
                >
                    Create New Post
                </Button>
            </Stack>

            <Grid container spacing={2}>
                <Grid item xs={12} md={6}>
                    <Card>
                        <CardContent>
                            <Typography variant="h6" gutterBottom>
                                Overview
                            </Typography>
                            <Typography variant="body2" color="text.secondary">
                                Statistics and management tools coming soon.
                            </Typography>
                        </CardContent>
                    </Card>
                </Grid>
            </Grid>
        </Box>
    )
}

export default ManageDashboardPage
