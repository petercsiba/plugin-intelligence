import React from 'react';
import Container from '@mui/material/Container';
import Typography from '@mui/material/Typography';
import Box from '@mui/material/Box';

export default function Pricing() {
    return (
        <Container maxWidth="lg">
            <Box sx={{ my: 4 }}>
                <Typography variant="h4" component="h1">
                    Pricing
                </Typography>
                <Typography variant="body1">
                    Talk to sales to get a quote.
                </Typography>
            </Box>
        </Container>
    );
}
