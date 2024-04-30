import React from 'react';
import Container from '@mui/material/Container';
import Typography from '@mui/material/Typography';
import Box from '@mui/material/Box';

export default function About() {
    return (
        <Container maxWidth="lg">
            <Box sx={{ my: 4 }}>
                <Typography variant="h4" component="h1">
                    About Us
                </Typography>
                <Typography variant="body1">
                    This is the About page of our Next.js application using Material-UI.
                </Typography>
            </Box>
        </Container>
    );
}
