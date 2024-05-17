import React from 'react';
import Container from '@mui/material/Container';
import Typography from '@mui/material/Typography';
import PageTitle from "@/components/PageTitle";

export default function Pricing() {
    return (
        <Container maxWidth="lg">
            <PageTitle title="Pricing" />
            <Container maxWidth="sm">
                <Typography variant="body1">
                    Talk to sales to get a quote.
                </Typography>
            </Container>
        </Container>
    );
}
