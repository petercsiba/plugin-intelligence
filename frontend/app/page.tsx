// Mark the file as a Client Component
"use client";

import * as React from 'react';
import { useState, useEffect } from 'react';
import Container from '@mui/material/Container';
import NextLink from "next/link";
import Button from '@mui/material/Button';
import {TopPluginResponse} from "./plugins/models";
import ArpuBubbleChartComponent from "./ArpuBubbleChart";
import {formatCurrency, formatNumberShort} from "@/utils";
import {Divider, Paper, Table, TableBody, TableCell, TableContainer, TableHead, TableRow } from '@mui/material';
import PageLoading from "@/components/PageLoading";
import NoResultsFound from "@/components/NoResultsFound";
import PageTitle from "@/components/PageTitle";
import ListBoxOneLine from "@/components/ListBoxOneLine";

const baseUrl = process.env.NEXT_PUBLIC_API_URL

const fetchTopPlugins = async (): Promise<TopPluginResponse[]> => {
    const url = `${baseUrl}/plugins/top`
    console.log("Attempting to fetch plugins from", url);
    const response = await fetch(url);
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

    if (loading) return <PageLoading />;

    if (plugins.length === 0) return <NoResultsFound model_name={"Plugins"} />;

    return (
        <Container maxWidth="lg">
            <PageTitle title="Top Google Plugins By Estimated Revenue" />
            <ArpuBubbleChartComponent />
            <TableContainer component={Paper}>
                <Table size="small"> {/* Smaller cell padding */}
                    <TableHead>
                        <TableRow>
                            <TableCell>Logo</TableCell>
                            <TableCell>Name</TableCell>
                            <TableCell>Main Tags</TableCell>
                            <TableCell>Revenue Estimate</TableCell>
                            <TableCell>Downloads</TableCell>
                            <TableCell>Lowest Paid Tier</TableCell>
                            <TableCell>Details</TableCell>
                        </TableRow>
                    </TableHead>
                    <TableBody>
                        {plugins.map((plugin) => (
                            <TableRow key={plugin.id}>
                                <TableCell>
                                    {plugin.img_logo_link ? (
                                        <img src={plugin.img_logo_link} alt={plugin.name} style={{ width: 48 }} />
                                    ) : (
                                        ''
                                    )}
                                </TableCell>
                                <TableCell style={{fontWeight: "bold"}}>{plugin.name}</TableCell>
                                <TableCell>
                                    <ListBoxOneLine listOfStrings={plugin.main_tags} />
                                </TableCell>
                                {/*<TableCell>{plugins.plugin_type}</TableCell>*/}
                                <TableCell>
                                    {plugin.revenue_lower_bound && plugin.revenue_upper_bound ? (
                                        `${formatCurrency(plugin.revenue_lower_bound)} - ${formatCurrency(plugin.revenue_upper_bound)}`
                                    ) : 'N/A'}
                                </TableCell>
                                <TableCell>{formatNumberShort(plugin.user_count)}</TableCell>
                                <TableCell>{formatCurrency(plugin.lowest_paid_tier)}</TableCell>
                                <TableCell>
                                    <NextLink href={`/plugins/${plugin.id}/detail`} passHref>
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
