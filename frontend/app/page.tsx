// Mark the file as a Client Component
"use client";

import * as React from 'react';
import { useState, useEffect } from 'react';
import Container from '@mui/material/Container';
import Typography from '@mui/material/Typography';
import Box from '@mui/material/Box';
import NextLink from "next/link";
import Button from '@mui/material/Button';
import CircularProgress from '@mui/material/CircularProgress';
import {TopPluginResponse} from "./plugin/models";
import ArpuBubbleChartComponent from "./ArpuBubbleChart";
import {formatCurrency, formatNumber, formatNumberShort} from "@/utils";
import {Paper, Table, TableBody, TableCell, TableContainer, TableHead, TableRow } from '@mui/material';

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
            <TableContainer component={Paper}>
                <Table size="small"> {/* Smaller cell padding */}
                    <TableHead>
                        <TableRow>
                            <TableCell>Logo</TableCell>
                            <TableCell>Name</TableCell>
                            <TableCell>Type</TableCell>
                            <TableCell>Revenue Estimate</TableCell>
                            <TableCell>User Count</TableCell>
                            <TableCell>Details</TableCell>
                        </TableRow>
                    </TableHead>
                    <TableBody>
                        {plugins.map((plugin) => (
                            <TableRow key={plugin.id}>
                                <TableCell style={{ maxWidth: '64px' }}>
                                    {plugin.img_logo_link ? (
                                        <img src={plugin.img_logo_link} alt={plugin.name} style={{ width: 64 }} />
                                    ) : (
                                        ''
                                    )}
                                </TableCell>
                                <TableCell>{plugin.name}</TableCell>
                                <TableCell>{plugin.plugin_type}</TableCell>
                                <TableCell>
                                    {plugin.revenue_lower_bound && plugin.revenue_upper_bound ? (
                                        `${formatCurrency(plugin.revenue_lower_bound)} - ${formatCurrency(plugin.revenue_upper_bound)}`
                                    ) : 'N/A'}
                                </TableCell>
                                <TableCell>{formatNumberShort(plugin.user_count)}</TableCell>
                                <TableCell>
                                    <NextLink href={`/plugin/${plugin.id}`} passHref>
                                        <Button variant="contained" color="primary" fullWidth> {/* Full width on mobile */}
                                            View
                                        </Button>
                                    </NextLink>
                                </TableCell>
                            </TableRow>
                        ))}
                    </TableBody>
                </Table>
            </TableContainer>

        </Container>
    );
}
