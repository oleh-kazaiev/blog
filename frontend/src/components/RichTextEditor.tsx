import React, { useEffect, useRef } from 'react'
import { Box, IconButton, Paper, Stack, Tooltip } from '@mui/material'
import FormatBoldIcon from '@mui/icons-material/FormatBold'
import FormatItalicIcon from '@mui/icons-material/FormatItalic'
import FormatUnderlinedIcon from '@mui/icons-material/FormatUnderlined'
import LinkIcon from '@mui/icons-material/Link'
import FormatListBulletedIcon from '@mui/icons-material/FormatListBulleted'
import FormatListNumberedIcon from '@mui/icons-material/FormatListNumbered'
import FormatQuoteIcon from '@mui/icons-material/FormatQuote'

const RichTextEditor = ({ value, onChange, minHeight = 200 }) => {
    const ref = useRef(null)

    useEffect(() => {
        if (ref.current && value !== ref.current.innerHTML) {
            ref.current.innerHTML = value || ''
        }
    }, [value])

    const exec = (cmd, arg = null) => {
        document.execCommand(cmd, false, arg)
        if (ref.current) onChange(ref.current.innerHTML)
    }

    const promptLink = () => {
        const url = window.prompt('Enter URL')
        if (url) exec('createLink', url)
    }

    return (
        <Box>
            <Stack direction="row" spacing={1} sx={{ mb: 1 }}>
                <Tooltip title="Bold">
                    <span>
                        <IconButton size="small" onClick={() => exec('bold')}>
                            <FormatBoldIcon fontSize="small" />
                        </IconButton>
                    </span>
                </Tooltip>
                <Tooltip title="Italic">
                    <span>
                        <IconButton size="small" onClick={() => exec('italic')}>
                            <FormatItalicIcon fontSize="small" />
                        </IconButton>
                    </span>
                </Tooltip>
                <Tooltip title="Underline">
                    <span>
                        <IconButton
                            size="small"
                            onClick={() => exec('underline')}
                        >
                            <FormatUnderlinedIcon fontSize="small" />
                        </IconButton>
                    </span>
                </Tooltip>
                <Tooltip title="Link">
                    <span>
                        <IconButton size="small" onClick={promptLink}>
                            <LinkIcon fontSize="small" />
                        </IconButton>
                    </span>
                </Tooltip>
                <Tooltip title="Bulleted list">
                    <span>
                        <IconButton
                            size="small"
                            onClick={() => exec('insertUnorderedList')}
                        >
                            <FormatListBulletedIcon fontSize="small" />
                        </IconButton>
                    </span>
                </Tooltip>
                <Tooltip title="Numbered list">
                    <span>
                        <IconButton
                            size="small"
                            onClick={() => exec('insertOrderedList')}
                        >
                            <FormatListNumberedIcon fontSize="small" />
                        </IconButton>
                    </span>
                </Tooltip>
                <Tooltip title="Quote">
                    <span>
                        <IconButton
                            size="small"
                            onClick={() => exec('formatBlock', 'blockquote')}
                        >
                            <FormatQuoteIcon fontSize="small" />
                        </IconButton>
                    </span>
                </Tooltip>
            </Stack>
            <Paper variant="outlined">
                <Box
                    ref={ref}
                    role="textbox"
                    contentEditable
                    suppressContentEditableWarning
                    onInput={(e) => onChange(e.currentTarget.innerHTML)}
                    sx={{ p: 2, minHeight, '&:focus': { outline: 'none' } }}
                />
            </Paper>
        </Box>
    )
}

export default RichTextEditor
