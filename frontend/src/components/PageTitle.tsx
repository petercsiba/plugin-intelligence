import React from 'react';
import Box from '@mui/material/Box';
import Typography from '@mui/material/Typography';

interface TitleProps {
    title: string;
}

const PageTitle: React.FC<TitleProps> = ({ title }) => {
    return (
        <Box
            sx={{
                my: 4,
                display: 'flex',
                flexDirection: 'column',
                justifyContent: 'center',
                alignItems: 'center',
            }}
        >
            <Typography variant="h4" component="h1" sx={{ mb: 2 }}>
                {title}
            </Typography>
        </Box>
    );
};

export default PageTitle;
