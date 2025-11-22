import React, { useState, useEffect } from 'react'
import { useParams } from 'react-router-dom'
import {
    Typography,
    Grid,
    Card,
    CardContent,
    CardMedia,
    CardActionArea,
    Pagination,
    Box,
    Breadcrumbs,
    Link,
    CircularProgress,
    Badge,
    Stack,
} from '@mui/material'
import { Link as RouterLink } from 'react-router-dom'
import ThumbUpOutlinedIcon from '@mui/icons-material/ThumbUpOutlined'
import ThumbDownOutlinedIcon from '@mui/icons-material/ThumbDownOutlined'
import { postService } from '../services/api'

const CategoryPage = () => {
    const { slug } = useParams()
    const [posts, setPosts] = useState([])
    const [category, setCategory] = useState(null)
    const [loading, setLoading] = useState(true)
    const [error, setError] = useState(null)
    const [page, setPage] = useState(1)
    const [count, setCount] = useState(0)
    const postsPerPage = 6

    useEffect(() => {
        const fetchCategoryAndPosts = async () => {
            try {
                setLoading(true)

                // Fetch category
                const { data: categoryData } =
                    await postService.getCategory(slug)
                setCategory(categoryData)

                // Fetch posts for this category
                const { data: postsData } = await postService.getCategoryPosts(
                    slug,
                    { page }
                )
                const items = Array.isArray(postsData?.results)
                    ? postsData.results
                    : Array.isArray(postsData)
                      ? postsData
                      : []
                setPosts(items)

                if (typeof postsData?.count === 'number') {
                    setCount(Math.ceil(postsData.count / postsPerPage))
                } else {
                    setCount(
                        Math.max(Math.ceil(items.length / postsPerPage), 0)
                    )
                }

                setLoading(false)
            } catch (err) {
                console.error(err)
                if (err.response && err.response.status === 404) {
                    setError('Category not found')
                } else {
                    setError('Failed to fetch data. Please try again later.')
                }
                setLoading(false)
            }
        }

        fetchCategoryAndPosts()
    }, [slug, page])

    const handlePageChange = (event, value) => {
        setPage(value)
        window.scrollTo(0, 0)
    }

    if (loading) return <CircularProgress />
    if (error) return <Typography color="error">{error}</Typography>
    if (!category) return <Typography>Category not found</Typography>

    return (
        <Box>
            <Breadcrumbs aria-label="breadcrumb" sx={{ mb: 3 }}>
                <Link
                    component={RouterLink}
                    to="/"
                    underline="hover"
                    color="inherit"
                >
                    Home
                </Link>
                <Typography color="text.primary">{category.name}</Typography>
            </Breadcrumbs>

            <Typography variant="h4" component="h1" gutterBottom>
                Posts in {category.name}
            </Typography>

            {posts.length === 0 ? (
                <Typography>No posts available in this category.</Typography>
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
                                        {post.featured_image && (
                                            <CardMedia
                                                component="img"
                                                height="140"
                                                image={post.featured_image}
                                                alt={post.title}
                                            />
                                        )}
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
                                                By:{' '}
                                                {post.author.full_name ||
                                                    post.author.email}{' '}
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
        </Box>
    )
}

export default CategoryPage
