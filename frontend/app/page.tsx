import * as React from 'react';
import Container from '@mui/material/Container';
import Typography from '@mui/material/Typography';
import Box from '@mui/material/Box';
import Link from '@mui/material/Link';
import ProTip from '@/components/ProTip';
import Copyright from '@/components/Copyright';

export default function HomePage() {
  return (
    <Container maxWidth="lg">
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
          Plugin Intelligence - Trosku Panko Plugin Revenue Estimator
        </Typography>
      <Link href="/about" color="secondary" underline="hover">
        Go to the about page
      </Link>
        <ProTip />
        <Copyright />
      </Box>
    </Container>
  );
}
