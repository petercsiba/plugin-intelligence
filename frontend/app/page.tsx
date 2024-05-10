// Mark the file as a Client Component
"use client";

import * as React from 'react';
import { useState, useEffect } from 'react';
import Container from '@mui/material/Container';
import Typography from '@mui/material/Typography';
import Box from '@mui/material/Box';
import NextLink from "next/link";
import Card from '@mui/material/Card';
import CardContent from '@mui/material/CardContent';
import Button from '@mui/material/Button';
import CircularProgress from '@mui/material/CircularProgress';
import Grid from '@mui/material/Grid';
import CardMedia from '@mui/material/CardMedia';
import {TopPluginResponse} from "./plugin/models";
import ArpuBubbleChartComponent from "./ArpuBubbleChart";
import {formatCurrency} from "@/utils";

const baseUrl = process.env.NEXT_PUBLIC_API_URL

const fetchTopPlugins = async (): Promise<TopPluginResponse[]> => {
    console.log("Attempting to fetch plugins from", `${baseUrl}/top-plugins/`);
    const response = await fetch(`${baseUrl}/top-plugins/`);
    return await response.json();
};

export default function HomePage() {
    const [loading, setLoading] = useState(true);
    const [plugins, setPlugins] = useState<TopPluginResponse[]>([]);

    useEffect(() => {
        console.log("useEffect is being triggered");
        (async () => {
            try {
                const fetchedPlugins = await fetchTopPlugins();
                setPlugins(fetchedPlugins);
            } catch (error) {
                console.error('Error fetching plugins:', error);
            } finally {
                setLoading(false);
            }
        })();
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
    if (plugins.length === 0) {
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
                    <Typography variant="h5" color="textSecondary">
                        No plugins found.
                    </Typography>
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
                    Plugin Intelligence - Top Google Plugins By Estimated Revenue
                </Typography>
                {/*
                <Link href="/about" color="secondary" underline="hover">
                    Go to the about page
                </Link>
                 */}
            </Box>
            <ArpuBubbleChartComponent />
            <Grid container spacing={3}>
                {plugins.map((plugin) => (
                    <Grid item xs={12} sm={6} md={4} key={plugin.id}>
                        <Card>
                            <CardContent>
                                <Typography variant="h5" gutterBottom>
                                    {plugin.name}
                                </Typography>
                                <CardMedia
                                    component="img"
                                    height="40"
                                    image={plugin.img_logo_link}
                                    alt={plugin.name}
                                />
                                { (plugin.revenue_lower_bound && plugin.revenue_upper_bound) ? (
                                    <Typography variant="body2" color="textSecondary">
                                        TTM Estimate: {formatCurrency(plugin.revenue_lower_bound)} - {formatCurrency(plugin.revenue_upper_bound)}
                                    </Typography>
                                ) : null}
                                {plugin.elevator_pitch ? (
                                <Typography variant="body2" color="textSecondary">
                                    {plugin.elevator_pitch}
                                </Typography>
                                ) : null}

                                <NextLink href={`/plugin/${plugin.id}`} passHref>
                                    <Button variant="contained" color="primary">
                                        View Details
                                    </Button>
                                </NextLink>
                            </CardContent>
                        </Card>
                    </Grid>
                ))}
            </Grid>
        </Container>
    );
}
