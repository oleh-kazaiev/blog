import React, { useState, useEffect } from 'react'
import {
    Grid,
    Typography,
    Card,
    CardContent,
    CardMedia,
    CardActionArea,
    Pagination,
    Box,
    Badge,
    Stack,
    Chip,
    Skeleton,
    Alert,
    Button,
    TextField,
} from '@mui/material'
import { Link as RouterLink } from 'react-router-dom'
import ThumbUpOutlinedIcon from '@mui/icons-material/ThumbUpOutlined'
import ThumbDownOutlinedIcon from '@mui/icons-material/ThumbDownOutlined'
import RefreshIcon from '@mui/icons-material/Refresh'
import { postService } from '../services/api'

const HomePage = () => {
    const [posts, setPosts] = useState([])
    const [loading, setLoading] = useState(true)
    const [error, setError] = useState(null)
    const [page, setPage] = useState(1)
    const [count, setCount] = useState(0)
    const [searchQuery, setSearchQuery] = useState('')
    const [searching, setSearching] = useState(false)
    const postsPerPage = 6

    useEffect(() => {
        const fetchPosts = async () => {
            try {
                setLoading(true)
                const fetcher = searchQuery
                    ? postService.searchPosts(searchQuery, { page })
                    : postService.getPosts({ page })
                const { data } = await fetcher
                const items = Array.isArray(data?.results)
                    ? data.results
                    : Array.isArray(data)
                      ? data
                      : []
                setPosts(items)
                const total =
                    typeof data?.count === 'number' ? data.count : items.length
                setCount(Math.max(Math.ceil(total / postsPerPage), 0))
                setError(null)
            } catch (err) {
                setError('Failed to fetch posts. Please try again later.')
            } finally {
                setLoading(false)
                setSearching(false)
            }
        }

        fetchPosts()
    }, [page, searchQuery])

    const handlePageChange = (event, value) => {
        setPage(value)
        window.scrollTo({ top: 0, behavior: 'smooth' })
    }

    const handleRetry = () => {
        setError(null)
        setLoading(true)
        window.location.reload()
    }

    const PostSkeleton = () => (
        <Card sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
            <Skeleton variant="rectangular" height={140} />
            <CardContent sx={{ flexGrow: 1 }}>
                <Skeleton variant="text" height={32} width="80%" />
                <Skeleton variant="text" height={20} />
                <Skeleton variant="text" height={20} width="60%" />
                <Skeleton variant="text" height={16} sx={{ mt: 2 }} />
                <Stack direction="row" spacing={1} sx={{ mt: 1 }}>
                    <Skeleton variant="circular" width={24} height={24} />
                    <Skeleton variant="circular" width={24} height={24} />
                </Stack>
            </CardContent>
        </Card>
    )

    if (error) {
        return (
            <Box sx={{ textAlign: 'center', py: 4 }}>
                <Alert severity="error" sx={{ mb: 2 }}>
                    {error}
                </Alert>
                <Button
                    variant="contained"
                    startIcon={<RefreshIcon />}
                    onClick={handleRetry}
                >
                    Retry
                </Button>
            </Box>
        )
    }

    return (
        <>
            <Stack
                direction={{ xs: 'column', sm: 'row' }}
                spacing={2}
                alignItems={{ xs: 'stretch', sm: 'center' }}
                justifyContent="space-between"
                sx={{ mb: 3 }}
            >
                <Typography variant="h4" component="h1">
                    Posts
                </Typography>

                <Stack direction="row" spacing={1} alignItems="center">
                    <TextField
                        size="small"
                        placeholder="Search posts..."
                        value={searchQuery}
                        onChange={(e) => {
                            setSearchQuery(e.target.value)
                            setPage(1)
                            setSearching(true)
                        }}
                        InputProps={{ 'aria-label': 'Search posts' }}
                    />
                    <Button
                        variant="outlined"
                        onClick={() => {
                            setPage(1)
                            setSearching(true)
                        }}
                        disabled={loading}
                    >
                        {searching ? 'Searching...' : 'Search'}
                    </Button>
                    {searchQuery && (
                        <Button
                            variant="text"
                            onClick={() => {
                                setSearchQuery('')
                                setPage(1)
                            }}
                            disabled={loading}
                        >
                            Clear
                        </Button>
                    )}
                </Stack>
            </Stack>

            {loading ? (
                <Grid container spacing={4}>
                    {[1, 2, 3, 4, 5, 6].map((n) => (
                        <Grid item xs={12} sm={6} md={4} key={n}>
                            <PostSkeleton />
                        </Grid>
                    ))}
                </Grid>
            ) : posts.length === 0 ? (
                <Box sx={{ textAlign: 'center', py: 4 }}>
                    <Typography variant="h6" color="text.secondary">
                        No posts found.
                    </Typography>
                    <Typography
                        variant="body2"
                        color="text.secondary"
                        sx={{ mt: 1 }}
                    >
                        Try adjusting your search or check back later for new
                        content.
                    </Typography>
                </Box>
            ) : (
                <>
                    <Grid container spacing={4}>
                        {posts.map((post) => (
                            <Grid item xs={12} sm={6} md={4} key={post.id}>
                                <Card
                                    sx={{
                                        height: '100%',
                                        display: 'flex',
                                        flexDirection: 'column',
                                    }}
                                >
                                    <CardActionArea
                                        component={RouterLink}
                                        to={`/post/${post.slug}`}
                                    >
                                        <Box sx={{ position: 'relative' }}>
                                            {post.is_paid && (
                                                <Chip
                                                    label={
                                                        post.has_access
                                                            ? 'Unlocked'
                                                            : 'Paid'
                                                    }
                                                    color={
                                                        post.has_access
                                                            ? 'success'
                                                            : 'warning'
                                                    }
                                                    size="small"
                                                    sx={{
                                                        position: 'absolute',
                                                        top: 8,
                                                        right: 8,
                                                        zIndex: 1,
                                                    }}
                                                />
                                            )}
                                            {post.featured_image && (
                                                <CardMedia
                                                    component="img"
                                                    height="140"
                                                    image={post.featured_image}
                                                    alt={post.title}
                                                    loading="lazy"
                                                />
                                            )}
                                        </Box>
                                        <CardContent sx={{ flexGrow: 1 }}>
                                            <Typography
                                                gutterBottom
                                                variant="h5"
                                                component="h2"
                                            >
                                                {post.title}
                                            </Typography>
                                            <Typography
                                                variant="body2"
                                                color="text.secondary"
                                            >
                                                {post.excerpt ||
                                                    'Click to read more...'}
                                            </Typography>
                                            <Typography
                                                variant="caption"
                                                color="text.secondary"
                                                sx={{ mt: 2, display: 'block' }}
                                            >
                                                Category:{' '}
                                                {post.category?.name ||
                                                    'Uncategorized'}{' '}
                                                | By:{' '}
                                                {post.author?.full_name ||
                                                    post.author?.email ||
                                                    'Unknown'}{' '}
                                                |
                                                {new Date(
                                                    post.published_at
                                                ).toLocaleDateString()}
                                            </Typography>

                                            {/* Like/Dislike counts */}
                                            <Stack
                                                direction="row"
                                                spacing={1}
                                                sx={{ mt: 1 }}
                                            >
                                                <Badge
                                                    badgeContent={
                                                        post.likes_count
                                                    }
                                                    color="primary"
                                                >
                                                    <ThumbUpOutlinedIcon fontSize="small" />
                                                </Badge>
                                                <Badge
                                                    badgeContent={
                                                        post.dislikes_count
                                                    }
                                                    color="error"
                                                >
                                                    <ThumbDownOutlinedIcon fontSize="small" />
                                                </Badge>
                                            </Stack>
                                        </CardContent>
                                    </CardActionArea>
                                </Card>
                            </Grid>
                        ))}
                    </Grid>

                    {count > 1 && (
                        <Box
                            sx={{
                                display: 'flex',
                                justifyContent: 'center',
                                mt: 4,
                            }}
                        >
                            <Pagination
                                count={count}
                                page={page}
                                onChange={handlePageChange}
                                color="primary"
                            />
                        </Box>
                    )}
                </>
            )}
        </>
    )
}

export default HomePage
