// Mark the file as a Client Component
"use client";

import * as React from 'react';
import { useState, useEffect } from 'react';
import axios from 'axios';
import Container from '@mui/material/Container';
import Typography from '@mui/material/Typography';
import Box from '@mui/material/Box';
import Link from '@mui/material/Link';
import Card from '@mui/material/Card';
import CardContent from '@mui/material/CardContent';
import CardActions from '@mui/material/CardActions';
import Button from '@mui/material/Button';
import CircularProgress from '@mui/material/CircularProgress';

const baseURL = process.env.NEXT_PUBLIC_API_URL;

export default function HomePage() {
  const [loading, setLoading] = useState(true);
  const [extensions, setExtensions] = useState([]);

  useEffect(() => {
    async function fetchExtensions() {
      try {
        /* Should I even use axios? */
        const response = await axios.get(`${baseURL}/top-extensions/`);
        setExtensions(response.data);
      } catch (error) {
        console.error('Error fetching extensions:', error);
      } finally {
        setLoading(false);
      }
    }

    fetchExtensions();
  }, []);

  if (loading) {
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
          <CircularProgress />
        </Box>
      </Container>
    );
  }

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
      </Box>

      {extensions.map((extension) => (
        <Card key={extension.id} sx={{ my: 2 }}>
          <CardContent>
            <Typography variant="h5">{extension.name}</Typography>
            <Typography variant="body2">{extension.description}</Typography>
            <Typography variant="body1">Rating: {extension.rating}</Typography>
            <Typography variant="body1">Rating Count: {extension.rating_count}</Typography>
            <Typography variant="body1">Users: {extension.user_count}</Typography>
          </CardContent>
          <CardActions>
            <Button size="small" href={extension.link} target="_blank" rel="noopener noreferrer">
              Learn More
            </Button>
          </CardActions>
        </Card>
      ))}
    </Container>
  );
}
