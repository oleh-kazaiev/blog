import React, { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import {
    Box,
    Button,
    TextField,
    Typography,
    Stack,
    FormControlLabel,
    Checkbox,
    InputAdornment,
} from '@mui/material'
import Autocomplete from '@mui/material/Autocomplete'
import { postService } from '../services/api'
import RichTextEditor from '../components/RichTextEditor'

const NewPostPage = () => {
    const navigate = useNavigate()
    const [categories, setCategories] = useState([])
    const [form, setForm] = useState({
        title: '',
        content: '',
        excerpt: '',
        category: '',
        publish_now: true,
        publish_at: new Date().toISOString().slice(0, 16), // local datetime-local default
        is_paid: false,
        price_input: '',
    })
    const [saving, setSaving] = useState(false)
    const [error, setError] = useState(null)

    useEffect(() => {
        const load = async () => {
            try {
                const { data } = await postService.getCategories()
                setCategories(Array.isArray(data) ? data : data?.results || [])
            } catch (e) {
                setCategories([])
            }
        }
        load()
    }, [])

    const handleChange = (e) => {
        const { name, value, type, checked } = e.target
        setForm((f) => ({
            ...f,
            [name]: type === 'checkbox' ? checked : value,
        }))
    }

    const handleSubmit = async (e) => {
        e.preventDefault()
        setSaving(true)
        setError(null)
        try {
            if (form.is_paid) {
                const priceValue = parseFloat(form.price_input || '0')
                if (Number.isNaN(priceValue) || priceValue <= 0) {
                    setError('Please enter a valid price for paid posts.')
                    setSaving(false)
                    return
                }
            }
            const now = new Date()
            const publishAtRaw =
                form.publish_now || !form.publish_at
                    ? now
                    : new Date(form.publish_at)
            const scheduledInPast = publishAtRaw <= now
            const shouldPublishNow = form.publish_now || scheduledInPast
            const priceCents = form.is_paid
                ? Math.round(parseFloat(form.price_input || '0') * 100)
                : 0
            // Resolve category id: support selecting existing or typing a new one
            let categoryId = form.category
            if (typeof categoryId === 'string' && categoryId.trim() !== '') {
                const existing = categories.find(
                    (c) =>
                        c.name.toLowerCase() === categoryId.trim().toLowerCase()
                )
                if (existing) {
                    categoryId = existing.id
                } else {
                    // Create new category via admin API
                    try {
                        const { data: newCat } =
                            await postService.createCategory(categoryId.trim())
                        categoryId = newCat.id
                        setCategories((prev) => [...prev, newCat])
                    } catch (err) {
                        // If backend reports duplicate (slug unique), try to find again
                        const fallback = categories.find(
                            (c) =>
                                c.name.toLowerCase() ===
                                categoryId.trim().toLowerCase()
                        )
                        if (fallback) categoryId = fallback.id
                        else throw err
                    }
                }
            }
            const payload = {
                title: form.title,
                content: form.content,
                excerpt: form.excerpt,
                category: categoryId,
                is_published: shouldPublishNow,
                published_at: publishAtRaw.toISOString(),
                is_paid: form.is_paid,
                price_cents: priceCents,
                price_currency: 'usd',
            }
            const { data } = await postService.createPost(payload)
            if (data?.slug) {
                navigate(`/post/${data.slug}`)
            } else {
                navigate('/')
            }
        } catch (err) {
            setError(err.response?.data || 'Failed to create post')
        } finally {
            setSaving(false)
        }
    }

    return (
        <Box
            component="form"
            onSubmit={handleSubmit}
            sx={{ maxWidth: 800, mx: 'auto' }}
        >
            <Typography variant="h4" gutterBottom>
                Create New Post
            </Typography>
            {error && (
                <Typography color="error" sx={{ mb: 2 }}>
                    {typeof error === 'string' ? error : JSON.stringify(error)}
                </Typography>
            )}
            <Stack spacing={2}>
                <TextField
                    label="Title"
                    name="title"
                    value={form.title}
                    onChange={handleChange}
                    fullWidth
                    required
                />
                <TextField
                    label="Excerpt"
                    name="excerpt"
                    value={form.excerpt}
                    onChange={handleChange}
                    fullWidth
                    multiline
                    minRows={2}
                />
                <Box>
                    <Typography variant="subtitle1" sx={{ mb: 1 }}>
                        Content
                    </Typography>
                    <RichTextEditor
                        value={form.content}
                        onChange={(html) =>
                            setForm((f) => ({ ...f, content: html }))
                        }
                        minHeight={260}
                    />
                </Box>
                <Box>
                    <Typography variant="subtitle1" sx={{ mb: 1 }}>
                        Category
                    </Typography>
                    <Autocomplete
                        freeSolo
                        options={categories}
                        getOptionLabel={(option) =>
                            typeof option === 'string' ? option : option.name
                        }
                        onInputChange={(e, value) =>
                            setForm((f) => ({ ...f, category: value }))
                        }
                        onChange={(e, value) => {
                            if (value && typeof value === 'object')
                                setForm((f) => ({ ...f, category: value.id }))
                        }}
                        renderInput={(params) => (
                            <TextField
                                {...params}
                                placeholder="Select or type a category"
                                fullWidth
                            />
                        )}
                    />
                </Box>
                <Box>
                    <FormControlLabel
                        control={
                            <Checkbox
                                checked={form.is_paid}
                                onChange={handleChange}
                                name="is_paid"
                            />
                        }
                        label="Paid content (requires purchase to unlock)"
                    />
                    {form.is_paid && (
                        <Box sx={{ mt: 1 }}>
                            <TextField
                                label="Price"
                                type="number"
                                name="price_input"
                                value={form.price_input}
                                onChange={handleChange}
                                fullWidth
                                inputProps={{ min: 0, step: 0.5 }}
                                InputProps={{
                                    startAdornment: (
                                        <InputAdornment position="start">
                                            USD
                                        </InputAdornment>
                                    ),
                                }}
                                required
                            />
                        </Box>
                    )}
                </Box>
                <Box>
                    <FormControlLabel
                        control={
                            <Checkbox
                                checked={form.publish_now}
                                onChange={handleChange}
                                name="publish_now"
                            />
                        }
                        label="Publish now"
                    />
                    {!form.publish_now && (
                        <TextField
                            label="Publish at"
                            type="datetime-local"
                            name="publish_at"
                            value={form.publish_at}
                            onChange={handleChange}
                            fullWidth
                            InputLabelProps={{ shrink: true }}
                        />
                    )}
                </Box>
                <Stack direction="row" spacing={2} justifyContent="flex-end">
                    <Button
                        variant="outlined"
                        onClick={() => navigate('/')}
                        disabled={saving}
                    >
                        Cancel
                    </Button>
                    <Button
                        variant="contained"
                        color="primary"
                        type="submit"
                        disabled={saving}
                    >
                        {saving ? 'Saving...' : 'Create Post'}
                    </Button>
                </Stack>
            </Stack>
        </Box>
    )
}

export default NewPostPage
