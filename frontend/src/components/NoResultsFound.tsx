import React from 'react';
import { useRouter } from 'next/router';
import Container from '@mui/material/Container';
import Box from '@mui/material/Box';
import Typography from '@mui/material/Typography';
import Button from '@mui/material/Button';


interface NoResultsFoundProps {
    model_name: string;
}

const NoResultsFound: React.FC<NoResultsFoundProps> = ({ model_name }) => {
    const router = useRouter();

    const handleGoBack = () => {
        router.back();
    };

    const handleGoHome = () => {
        router.push('/');
    };

    return (
        <Container maxWidth="lg">
            <Box
                sx={{
                    my: 4,
                    display: 'flex',
                    flexDirection: 'column',
                    justifyContent: 'center',
                    alignItems: 'center',
                    textAlign: 'center',
                }}
            >
                <Typography variant="h5" color="textSecondary" gutterBottom>
                    Oh this is embarrassing - no {model_name} found :/
                </Typography>
                <Box sx={{ mt: 2 }}>
                    <Button variant="contained" color="primary" onClick={handleGoBack} sx={{ mr: 1 }}>
                        Go Back
                    </Button>
                    <Button variant="contained" color="secondary" onClick={handleGoHome}>
                        Go to Home Page
                    </Button>
                </Box>
            </Box>
        </Container>
    );
};

export default NoResultsFound;
